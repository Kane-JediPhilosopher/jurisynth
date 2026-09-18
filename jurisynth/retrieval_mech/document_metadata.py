"""Deterministic source-document identity and instrument-scope metadata.

The source ``document_id`` is only a lookup key.  Instrument identity comes
from persisted CELEX/ELI metadata or the document's primary heading; filenames
are never decoded into an instrument identity.
"""

from __future__ import annotations

import html
import json
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from jurisynth.contracts import InstrumentScope, RetrievalRequest


_DC_IDENTIFIER = re.compile(
    r'<meta\s+name="DC\.identifier"[^>]*content="([^"]+)"', re.IGNORECASE | re.DOTALL
)
_DC_DESCRIPTION = re.compile(
    r'<meta\s+name="DC\.description"[^>]*content="([^"]+)"', re.IGNORECASE | re.DOTALL
)
_PRIMARY_TITLE = re.compile(
    r'<p[^>]*class="[^"]*doc-ti[^"]*"[^>]*>(.*?)</p>', re.IGNORECASE | re.DOTALL
)
_STANDALONE_ELI = re.compile(
    r'<p[^>]*class="[^"]*normal[^"]*"[^>]*>\s*ELI:\s*'
    r'(?:<a[^>]*>)?\s*(https?://data\.europa\.eu/eli/[^<\s]+)',
    re.IGNORECASE | re.DOTALL,
)
_CELEX = re.compile(r"CELEX:([^:\"&<]+)", re.IGNORECASE)
_TAG = re.compile(r"<[^>]+>")
_SPACE = re.compile(r"\s+")
_PARENTHETICAL = re.compile(r"\(([^()]{3,100})\)")
_INSTRUMENT_NUMBER = re.compile(
    r"\b(regulation|directive|decision|recommendation)\b"
    r"(?:\s*\((eu|ec|eec|euratom)\))?\s*(?:no\s*)?"
    r"(?:(\d{4})\s*/\s*(\d{1,5})|(\d{1,5})\s*/\s*(\d{2,4}))",
    re.IGNORECASE,
)
_QUERY_CITATION = re.compile(
    r"\b(regulation|directive|decision|recommendation)\b"
    r"(?:\s*\((eu|ec|eec|euratom)\))?\s*(?:no\s*)?"
    r"(?:(\d{4})\s*/\s*(\d{1,5})|(\d{1,5})\s*/\s*(\d{2,4}))",
    re.IGNORECASE,
)
_ELI_IN_TEXT = re.compile(r"https?://data\.europa\.eu/eli/[^\s<>)]+", re.IGNORECASE)
_CELEX_IN_TEXT = re.compile(r"\bCELEX\s*:?\s*([0-9A-Z()_]+)", re.IGNORECASE)


@dataclass(frozen=True, slots=True)
class DocumentMetadata:
    document_id: str
    celex: str | None
    eli: str | None
    title: str | None
    aliases: tuple[str, ...]
    canonical_keys: tuple[str, ...]

    @property
    def identified(self) -> bool:
        return bool(self.celex or self.eli or self.title)


@dataclass(frozen=True, slots=True)
class InstrumentScopeContext:
    target_keys: frozenset[str] = frozenset()
    matched_terms: tuple[str, ...] = ()
    source: str = "none"

    @property
    def explicitly_scoped(self) -> bool:
        return bool(self.target_keys)


class DocumentMetadataStore:
    """Read-only SQLite lookup used by retrieval without loading the corpus."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        if not self.path.is_file():
            raise FileNotFoundError(self.path)

    def get(self, document_id: str) -> DocumentMetadata | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT document_id, celex, eli, title, aliases_json, canonical_keys_json "
                "FROM documents WHERE document_id = ?",
                (document_id,),
            ).fetchone()
        return _row_to_metadata(row) if row is not None else None

    def resolve_request_scope(self, request: RetrievalRequest) -> InstrumentScopeContext:
        direct = self._resolve_text(request.leaf_query)
        # Leaf-local scope remains authoritative.  _resolve_text collects every
        # unambiguous instrument in that leaf, so a multi-regime leaf is not
        # reduced to its first match.  Contextual facts remain a fallback only,
        # preserving the existing single-instrument scope contract.
        contexts = [direct] if direct.target_keys else [
            self._resolve_text(fact) for fact in request.contextual_facts
        ]
        target_keys = {
            key for context in contexts for key in context.target_keys
        }
        matched_terms = {
            term for context in contexts for term in context.matched_terms
        }
        if not target_keys:
            return InstrumentScopeContext()
        source = "leaf_query" if direct.target_keys else "leaf_local_facts"
        return InstrumentScopeContext(
            frozenset(target_keys), tuple(sorted(matched_terms)), source
        )

    def classify_document(
        self, document_id: str, context: InstrumentScopeContext
    ) -> InstrumentScope:
        if not context.explicitly_scoped:
            return "unknown"
        record = self.get(document_id)
        if record is None or not record.identified:
            return "unknown"
        if context.target_keys.intersection(record.canonical_keys):
            return "in_scope"
        # A title alone is not enough to prove that a document belongs to a
        # different instrument.  Only a non-matching canonical identity makes
        # the cross-instrument classification unambiguous.
        if record.canonical_keys:
            return "cross_instrument"
        return "unknown"

    def document_ids_for_keys(
        self, keys: set[str] | frozenset[str], *, maximum_per_key: int = 4
    ) -> dict[str, tuple[str, ...]]:
        """Resolve canonical instrument keys to a small deterministic source set."""
        if maximum_per_key < 1:
            raise ValueError("maximum_per_key must be positive")
        requested = set(keys)
        matches: dict[str, list[tuple[tuple[object, ...], str]]] = {
            key: [] for key in requested
        }
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT document_id, celex, eli, title, canonical_keys_json FROM documents"
            ).fetchall()
        for document_id, celex, eli, title, raw_keys in rows:
            record_keys = requested.intersection(json.loads(str(raw_keys)))
            if not record_keys:
                continue
            normalized_title = normalize_alias(str(title or ""))
            is_corrigendum = "corrigendum" in normalized_title or "/corrigendum/" in str(eli or "").casefold()
            priority = (
                is_corrigendum,
                celex is None and eli is None,
                len(normalized_title),
                str(document_id),
            )
            for key in record_keys:
                matches[key].append((priority, str(document_id)))
        return {
            key: tuple(document_id for _, document_id in sorted(values)[:maximum_per_key])
            for key, values in matches.items()
        }

    def _resolve_text(self, text: str) -> InstrumentScopeContext:
        direct_keys = _canonical_keys_from_text(text)
        terms: set[str] = set()
        if direct_keys:
            terms.update(sorted(direct_keys))

        normalized = normalize_alias(text)
        candidates = _alias_ngrams(normalized)
        alias_rows: list[tuple[str, str]] = []
        if candidates:
            placeholders = ",".join("?" for _ in candidates)
            with self._connect() as connection:
                alias_rows = connection.execute(
                    f"SELECT normalized_alias, document_id FROM aliases "
                    f"WHERE normalized_alias IN ({placeholders})",
                    tuple(candidates),
                ).fetchall()

        by_alias: dict[str, list[DocumentMetadata]] = {}
        for alias, document_id in alias_rows:
            record = self.get(document_id)
            if record is not None:
                by_alias.setdefault(alias, []).append(record)
        for alias, records in by_alias.items():
            stable = _stable_alias_keys(records)
            if stable:
                direct_keys.update(stable)
                terms.add(alias)
        return InstrumentScopeContext(frozenset(direct_keys), tuple(sorted(terms)), "leaf_query")

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(f"file:{self.path.as_posix()}?mode=ro", uri=True)


def build_document_metadata_sidecar(
    source_root: str | Path, destination: str | Path
) -> dict[str, int]:
    """Extract source metadata into a small, replaceable SQLite sidecar."""
    source_root = Path(source_root)
    destination = Path(destination)
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite document metadata sidecar: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(destination)
    try:
        connection.executescript(
            """
            PRAGMA journal_mode = WAL;
            PRAGMA synchronous = NORMAL;
            CREATE TABLE documents (
                document_id TEXT PRIMARY KEY,
                celex TEXT,
                eli TEXT,
                title TEXT,
                aliases_json TEXT NOT NULL,
                canonical_keys_json TEXT NOT NULL
            );
            CREATE TABLE aliases (
                normalized_alias TEXT NOT NULL,
                document_id TEXT NOT NULL,
                alias_kind TEXT NOT NULL,
                PRIMARY KEY (normalized_alias, document_id),
                FOREIGN KEY (document_id) REFERENCES documents(document_id)
            );
            CREATE INDEX aliases_document_id ON aliases(document_id);
            """
        )
        document_count = identified_count = canonical_count = alias_count = 0
        for path in sorted(source_root.glob("batch_*/processed_docs/*.html")):
            record = parse_document_metadata(path)
            connection.execute(
                "INSERT INTO documents VALUES (?, ?, ?, ?, ?, ?)",
                (
                    record.document_id,
                    record.celex,
                    record.eli,
                    record.title,
                    json.dumps(record.aliases, ensure_ascii=False),
                    json.dumps(record.canonical_keys, ensure_ascii=False),
                ),
            )
            connection.executemany(
                "INSERT OR IGNORE INTO aliases VALUES (?, ?, ?)",
                ((alias, record.document_id, "derived") for alias in record.aliases),
            )
            document_count += 1
            identified_count += int(record.identified)
            canonical_count += int(bool(record.celex or record.eli))
            alias_count += len(record.aliases)
        connection.commit()
        connection.execute("PRAGMA journal_mode = DELETE")
        return {
            "documents": document_count,
            "identified_documents": identified_count,
            "canonical_documents": canonical_count,
            "aliases": alias_count,
        }
    except Exception:
        connection.close()
        destination.unlink(missing_ok=True)
        raise
    finally:
        if connection:
            connection.close()


def parse_document_metadata(path: str | Path) -> DocumentMetadata:
    path = Path(path)
    body = path.read_text(encoding="utf-8", errors="replace")
    celex_match = _DC_IDENTIFIER.search(body)
    celex_uri = html.unescape(celex_match.group(1)).strip() if celex_match else None
    celex_code_match = _CELEX.search(celex_uri or "")
    celex = celex_code_match.group(1).upper() if celex_code_match else None
    eli_match = _STANDALONE_ELI.search(body)
    eli = html.unescape(eli_match.group(1)).strip() if eli_match else None
    title = _primary_title(body)
    keys = _identity_keys(celex, eli, title)
    aliases = _aliases(title, keys)
    return DocumentMetadata(
        path.stem,
        celex,
        eli,
        title,
        tuple(sorted(aliases)),
        tuple(sorted(keys)),
    )


def normalize_alias(value: str) -> str:
    value = html.unescape(value).casefold()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return _SPACE.sub(" ", value).strip()


def _primary_title(body: str) -> str | None:
    description = _DC_DESCRIPTION.search(body)
    if description:
        return _clean_text(description.group(1)) or None
    parts: list[str] = []
    for match in _PRIMARY_TITLE.finditer(body):
        part = _clean_text(match.group(1))
        if not part:
            continue
        if parts and re.match(r"^(annex|chapter|title\s+[ivx])\b", part, re.IGNORECASE):
            break
        parts.append(part)
        if len(parts) == 4:
            break
    return " ".join(parts) or None


def _clean_text(value: str) -> str:
    return _SPACE.sub(" ", html.unescape(_TAG.sub(" ", value))).strip()


def _identity_keys(celex: str | None, eli: str | None, title: str | None) -> set[str]:
    keys: set[str] = set()
    if celex:
        keys.add("celex:" + celex.casefold())
    if eli:
        normalized_eli = eli.casefold().rstrip("/")
        keys.add("eli:" + normalized_eli)
        keys.add("eli:" + normalized_eli.split("/corrigendum/", 1)[0])
        eli_citation = re.search(r"/eli/([^/]+)/(\d{4})/(\d+)/", normalized_eli)
        if eli_citation:
            keys.add(_citation_key(eli_citation.group(1), eli_citation.group(2), eli_citation.group(3)))
    if title:
        match = _INSTRUMENT_NUMBER.search(title[:300])
        if match and match.start() <= 40:
            kind, _jurisdiction, year, number = _citation_parts(match)
            keys.add(_citation_key(kind, year, number))
    return keys


def _aliases(title: str | None, keys: set[str]) -> set[str]:
    aliases: set[str] = set()
    for key in keys:
        if key.startswith("citation:"):
            _, kind, year, number = key.split(":", 3)
            aliases.add(normalize_alias(f"{kind} {year}/{number}"))
            aliases.add(normalize_alias(f"{year}/{number}"))
    if not title:
        return aliases
    normalized_title = normalize_alias(title)
    if normalized_title:
        aliases.add(normalized_title)
    for value in _PARENTHETICAL.findall(title[:500]):
        if re.search(r"\b(act|regulation|directive|decision|code)\b", value, re.IGNORECASE):
            alias = normalize_alias(value)
            aliases.add(alias)
            words = alias.split()
            acronym = "".join(word[0] for word in words if word)
            if 2 <= len(acronym) <= 8:
                aliases.add(acronym)
            if len(words) >= 3 and words[-1] in {"act", "regulation", "directive", "decision"}:
                prefix = "".join(word[0] for word in words[:-1])
                aliases.add(normalize_alias(prefix + " " + words[-1]))
    return {alias for alias in aliases if alias and (len(alias) >= 4 or alias.isalpha())}


def _canonical_keys_from_text(text: str) -> set[str]:
    keys: set[str] = set()
    for match in _QUERY_CITATION.finditer(text):
        kind, _jurisdiction, year, number = _citation_parts(match)
        keys.add(_citation_key(kind, year, number))
    for value in _ELI_IN_TEXT.findall(text):
        normalized = value.casefold().rstrip("/")
        keys.add("eli:" + normalized)
        keys.add("eli:" + normalized.split("/corrigendum/", 1)[0])
    for code in _CELEX_IN_TEXT.findall(text):
        keys.add("celex:" + code.casefold())
    return keys


def _citation_parts(match: re.Match[str]) -> tuple[str, str | None, str, str]:
    kind = match.group(1).casefold()
    jurisdiction = match.group(2).casefold() if match.group(2) else None
    if match.group(3):
        year, number = match.group(3), str(int(match.group(4)))
    else:
        number = str(int(match.group(5)))
        raw_year = match.group(6)
        year = raw_year if len(raw_year) == 4 else ("19" + raw_year if int(raw_year) >= 50 else "20" + raw_year)
    return kind, jurisdiction, year, number


def _citation_key(kind: str, year: str, number: str) -> str:
    eli_kinds = {
        "reg": "regulation",
        "reg_impl": "regulation",
        "reg_del": "regulation",
        "dir": "directive",
        "dec": "decision",
        "dec_impl": "decision",
        "reco": "recommendation",
    }
    return f"citation:{eli_kinds.get(kind.casefold(), kind.casefold())}:{int(year)}:{int(number)}"


def _alias_ngrams(normalized: str) -> list[str]:
    words = normalized.split()
    candidates = {word for word in words if 4 <= len(word) <= 10 and word.isalpha()}
    for size in range(2, min(10, len(words)) + 1):
        candidates.update(" ".join(words[index:index + size]) for index in range(len(words) - size + 1))
    return sorted(candidates)


def _stable_alias_keys(records: list[DocumentMetadata]) -> set[str]:
    """Resolve an alias only when its metadata identifies one stable instrument.

    The normal case remains an intersection across every matching record.  A
    unique strict majority is also accepted so a base act and its corrigendum
    can outvote a document that merely mentions the act's familiar name in its
    title.  Ties and one-off collisions remain unresolved rather than guessed.
    """
    key_sets = [set(record.canonical_keys) for record in records if record.canonical_keys]
    if not key_sets:
        return set()
    common = set.intersection(*key_sets)
    citation_keys = {key for key in common if key.startswith("citation:")}
    if citation_keys or common:
        return citation_keys or common

    support: dict[str, int] = {}
    for keys in key_sets:
        for key in {value for value in keys if value.startswith("citation:")}:
            support[key] = support.get(key, 0) + 1
    if not support:
        return set()
    best = max(support.values())
    winners = {key for key, count in support.items() if count == best}
    if len(winners) == 1 and best > len(key_sets) / 2:
        return winners
    return set()


def _row_to_metadata(row: tuple[object, ...]) -> DocumentMetadata:
    return DocumentMetadata(
        document_id=str(row[0]),
        celex=str(row[1]) if row[1] is not None else None,
        eli=str(row[2]) if row[2] is not None else None,
        title=str(row[3]) if row[3] is not None else None,
        aliases=tuple(json.loads(str(row[4]))),
        canonical_keys=tuple(json.loads(str(row[5]))),
    )
