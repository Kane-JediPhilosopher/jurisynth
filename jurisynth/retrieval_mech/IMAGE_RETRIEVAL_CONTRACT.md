# Auxiliary image retrieval contract

## Scope

`image_index` is a per-batch FAISS index over concise visual descriptions. It
is a discovery and corroboration aid, analogous to table retrieval; it is not
a separate source of legal assertions.

## Candidate record

An image candidate must retain `image_id`, `document_id`, `relative_path`,
`mime_type`, `sha256`, `source_url`, description, visual type, legible text,
and similarity score. The stored path is relative to its batch, so an
aggregator can remap it without losing provenance.

## Retrieval policy

1. Run image retrieval only for visual-intent questions (for example,
   questions about a diagram, logo, chart, scan, figure, or an image named in
   the document) or as a low-priority corroboration pass.
2. Rank caption embeddings with FAISS, then retain the underlying document and
   image reference. A caption never independently supports a legal claim.
3. Text/RDF evidence remains authoritative. If an image is material, the
   report must state that it is auxiliary visual evidence and expose its source
   document and image reference.
4. Do not send image bytes to Nemotron Ultra by default. Surface the image to
   the UI; route a genuinely visual follow-up through a dedicated vision step.

## EvidenceBundle and UI change (deferred)

Add a separate `image_evidence` collection rather than mixing images into
assertion evidence. Each UI evidence drawer item should show a thumbnail,
description, document ID, source URL, similarity, and an **auxiliary visual
evidence** badge. The final answer must not cite an image caption as proof of
a legal obligation.

## Acceptance tests before enabling it

- a visual-intent query surfaces the expected image/document;
- a normal legal query does not add visual noise;
- every displayed thumbnail resolves only within the configured corpus root;
- a caption failure leaves text/RDF retrieval operational.
