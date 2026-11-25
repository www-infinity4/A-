# A- weighted associative engine V1

A local experimental retrieval and recombination engine, not a trained LLM. Node 22; no dependencies. Run `node --test engine.test.mjs`.

`buildIndex(blocks,{projects,wiring,symbols})` indexes exact block hashes, character 2–4 grams, configured project names, explicitly supplied undirected project edges and user-defined symbols. `rank(model,query,{weights:{character,project,symbol}})` uses weighted character cosine similarity, direct/one-hop project matches and exact declared symbol matches. `recombine(model,query,{seed,steps,words,weights,association})` produces a reproducible chain of excerpts from distinct source blocks with exact offsets and hash IDs. `association` balances relevance and random exploration among up to 32 candidates. No model inference, training, credential access or execution is performed.

Only use reviewed, authorized text; this prototype does not sanitize secrets or private content. Do not feed the entire raw clipboard to external providers or publish generated excerpts. Outputs are marked synthetic associations, not facts or instructions. Project edges must be supplied explicitly; co-occurrence is a candidate relationship, not proof of a working integration. Default weights are initial design choices, not learned parameters. No live Bubbles integration is claimed.
