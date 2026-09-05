# Jurisynth design-choice checklist

Answer briefly and honestly.  `UNKNOWN`, `NOT DECIDED`, and `I NEED TO READ`
are good research answers when accompanied by a next step.  Do not write what
you think a reviewer wants to hear.

## 1. Research problem and contribution

- [ ] What failure of ordinary legal-document search is Jurisynth trying to
  reduce?
- [ ] What is the smallest defensible contribution: a system, an architecture,
  an evaluation protocol, or a combination?
- [ ] What would falsify the claim that provenance-linked KG retrieval adds
  value over chunk-only retrieval?
- [ ] Why EU legislation, and what does this corpus *not* let you claim?

## 2. Knowledge representation

- [ ] Why represent extracted statements as assertion resources in addition to
  semantic triples?
- [ ] Why must every answerable assertion retain a source chunk?
- [ ] Why are tables minimal RDF resources rather than cell/row RDF graphs?
- [ ] Which extraction errors are most damaging: wrong entity, predicate,
  object, modifier, or provenance? Why?

## 3. Retrieval and communities

- [ ] Why use E-R matching plus RDF traversal instead of vector retrieval alone?
- [ ] Why keep direct chunk hits even when structured retrieval is ambiguous?
- [ ] Why are communities soft guidance rather than hard filters?
- [ ] What does bounded novelty contribute, and what noise risk does it create?
- [ ] When should Jurisynth say `insufficient_evidence` rather than infer an
  answer from model knowledge?

## 4. Agentic reasoning

- [ ] Why use QCompiler decomposition rather than one monolithic answer call?
- [ ] What makes two leaves genuinely dependent rather than merely related?
- [ ] Why are Claim IDs and evidence IDs validated deterministically?
- [ ] What should the system do when a required dependency fails?

## 5. Evaluation and limitations

- [ ] Which current measurements are plumbing/integrity diagnostics, and which
  would support an external performance claim?
- [ ] Why is Batch 0009 useful, and why is it insufficient as a final benchmark?
- [ ] What human judgement is indispensable in your evaluation protocol?
- [ ] What would you report as a negative result without trying to explain it
  away?

## 6. Thesis integrity check

- [ ] Can you explain every architecture arrow without reading my prose?
- [ ] Can you trace every numerical result to a command and artifact?
- [ ] Have you separated what the system does from what you hope it will do?
- [ ] Have you stated one strong limitation for every major contribution?

## Reply format

Use headings `1` through `6`.  Bullet fragments are enough.  I will turn your
answers into an evidence-led outline, identify unsupported claims, and ask only
the follow-up questions that matter.
