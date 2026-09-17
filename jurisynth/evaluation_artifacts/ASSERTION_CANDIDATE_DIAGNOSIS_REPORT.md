# Assertion candidate-generation diagnosis

Date: 2026-09-17

## Scope and frozen configuration

This diagnostic replayed the 92 controlled assertion cases where the final
result recovered none of the expected subject, predicate, or object. It used
the repaired v2 artifacts and the exact deterministic benchmark path:

- raw-leaf `LeafQueryInterpreter` fallback;
- entity top-k 5 and relation top-k 5;
- maximum 50 quads per seed;
- no path expansion;
- maximum 60 structured evidence items;
- no NIM calls;
- no threshold, prompt, ranking, traversal, community, table, or image changes.

## Earliest failure stage

- Query Interpreter miss: **0/92 (0%)**
- E-R grounding miss: **92/92 (100%)**
- Graph expansion/candidate-generation miss: **0/92 (0%)**
- Candidate filtering/pruning miss: **0/92 (0%)**
- Ranking-only miss: **0/92 (0%)**
- Benchmark representation mismatch: **0/92 (0%)**

Every exact target assertion remains present in its expected repaired-v2 source
graph. Every query contains the expected subject and predicate cues. However,
the fallback interpreter emits one composite entity concept containing the
whole query and emits no relation concepts. None of the 92 target subjects,
predicates, or URI objects entered the production top-5 seed set. Therefore no
target assertion was generated, filtered, or ranked; it was already unreachable
at E-R grounding.

## E-R grounding subtypes

- 76/92 (82.61%): subject, predicate, and object representations are available
  in their relevant E-R/KG indices, but the composite-query top-5 seed search
  returns semantically related neighbours instead of the exact target.
- 8/92 (8.70%): subject and object are indexed, but the predicate is absent
  from the relation index.
- 4/92 (4.35%): predicate and object are indexed, but the subject is absent
  from the entity index.
- 4/92 (4.35%): both subject and predicate are absent; the object remains
  represented.

Across all 92 cases, the exact assertion exists in the KG. Subjects are present
in the entity index for 84 cases and predicates in the relation index for 80.
Seventy-one targets have URI objects; 21 use literals. Raw candidate pools
ranged from 4 to 66 items (median 8), but none contained the target assertion.

## Representative misses

### global_assertion_00001 — all components indexed

- Target: `actions` → `should_be_complementary_to` →
  `the_country-specific_recommendations`
- Exact assertion in expected source graph: yes.
- Interpreter: one whole-query entity concept; no relation concepts.
- Top entity matches: `complementary actions` 0.7379; `complementary action`
  0.7106; `these two complementary types of actions` 0.7057; `additional
  necessary supporting and complementary action` 0.6497; `the actions referred
  to in paragraph 2` 0.6351.
- Target seed: absent. Raw candidates: 8. Target generated: no.

### global_assertion_00028 — predicate absent from relation index

- Target: `aid` → `can_therefore_be_authorised` → literal `true`.
- Exact assertion in expected source graph: yes.
- Indexed: subject yes; predicate no; object/literal present.
- Interpreter: one whole-query entity concept; no relation concepts.
- Top entity matches: `about the level of aid that could be authorised` 0.8694;
  `the purpose for which the aid is expressly authorised` 0.8635; `the level of
  aid that could be authorised` 0.8450; `the authorised aid` 0.8174; `aid
  intensities authorised` 0.8145.
- Target seed: absent. Raw candidates: 5. Target generated: no.

### global_assertion_00049 — subject absent from entity index

- Target concerns direct debits used to settle card balances → `are_included`
  → literal `true`.
- Exact assertion in expected source graph: yes.
- Indexed: subject no; predicate yes; object/literal present.
- Top entity matches: `direct debit transactions` 0.6821; `direct debit
  payments` 0.6815; `direct debits` 0.6779; a delayed-debit-card credit concept
  0.6670; payment transactions allowing credit transfers/direct debits 0.6599.
- Target seed: absent. Raw candidates: 31. Target generated: no.

### global_assertion_00052 — subject and predicate absent

- Target concerns the Regulation 1600/1999 anti-dumping duty →
  `is_hereby_re-imposed` → literal `true`.
- Exact assertion in expected source graph: yes.
- Indexed: subject no; predicate no; object/literal present.
- The five seeds are different anti-dumping duties, scoring 0.8555, 0.8338,
  0.8302, 0.8245, and 0.8242.
- Target seed: absent. Raw candidates: 5. Target generated: no.

### global_assertion_00073 — close lexical neighbour displaces target

- Target: `federal_republic_of_germany` →
  `is_hereby_authorized_to_prohibit` → marketing-of-seed object.
- Exact assertion and all three components exist.
- Top entity matches: `law of the federal republic of germany` 0.7567; a
  Federal German Republic declaration 0.7332; `to the federal republic of
  germany` 0.7214; `the federal republic of germany` 0.7147; and `germans
  within the meaning ...` 0.7129.
- The exact URI without the leading article is not seeded.
- Raw candidates: 66; retained candidates: 60. The target was never generated,
  so this is not a ranking-cutoff failure.

## Successful-case comparison

Five exact-recall controls were replayed with the same configuration.

- All 5 exact assertions exist in their expected source graphs.
- All 5 placed the target subject URI inside the entity top 5.
- All 5 generated the target assertion directly from that subject seed.
- All 5 retained it in the final structured evidence pool.
- Target structured ranks were 1, 1, 3, 2, and 39.

Examples include the exact decision identifier at similarity 0.870, the exact
LCI formula subject at 0.836, `council resolution of 23 april 1996` at 0.819,
`ms nuria urquia fernandez` at 0.726, and `french government` at 0.690. This
contrasts directly with the misses: success occurs whenever the exact target
subject survives grounding, even at rank 39 after candidate generation.

## Smallest recommended fix — not implemented

Do not raise E-R top-k and do not change graph traversal or ranking. The
controlled benchmark currently feeds the entire templated question as one
entity concept and supplies zero relation concepts, even though the template
contains separately quoted subject and predicate labels.

The smallest fix is a **benchmark-only deterministic interpreter** for this
synthetic protocol: parse the two quoted fields already present in the query,
emit the first as an entity concept and the second as a relation concept, and
then rerun the same 200 fixed cases. This restores the intended fixed/captured
interpreter boundary and activates existing exact-label grounding. It does not
change the production NIM Query Interpreter prompt or Retrieval Mech semantics.

The 16 cases whose target subject and/or predicate are absent from the E-R
metadata should remain a separately reported index-representation limitation;
they must not be hidden by threshold or ranking changes.

Full per-case traces are persisted in
`jurisynth/evaluation_artifacts/assertion_candidate_diagnosis_92.json`.
