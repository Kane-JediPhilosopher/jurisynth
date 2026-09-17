"""Print schemas for the read-only audit sidecars."""
from pathlib import Path
import sqlite3

for path in (
    Path("jurisynth/global_artifacts/community/er_index/er_metadata.sqlite"),
    Path("jurisynth/global_artifacts/community/community_metadata.sqlite"),
    Path("jurisynth/global_artifacts/chunk_index/chunk_metadata.sqlite"),
):
    connection = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)
    try:
        print(f"\n{path}")
        for name, sql in connection.execute(
            "SELECT name, sql FROM sqlite_master WHERE type='table' ORDER BY name"
        ):
            print(name, sql)
    finally:
        connection.close()
