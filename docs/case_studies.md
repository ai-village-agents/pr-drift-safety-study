# Case-study appendix: PR drift and safety signals

These examples are drawn from the collected GitHub metadata/comments. They are **not** final manual adjudications; they illustrate the kinds of incidents the weak labels are intended to surface for audit.

## 1. Green or mechanically mergeable is not the same as semantically safe

- PR: [#433 Batch: Ultra High Energy Cosmic Rays](https://github.com/ai-village-agents/the-universe/pull/433)
- Outcome in metadata: merged.
- Comment signal: a reviewer noted that checks passed and the PR was mechanically mergeable, but the two-dot diff inserted new entries before an already-merged tail, shifting the intended numbering rather than appending after current main.
- Research relevance: this is the central “green checks can miss PR drift” pattern. The safety issue was not syntax; it was semantic ordering relative to rapidly advancing main.

## 2. Placeholder entries can make a branch unsafe even if it parses

- PR: [#370 Batch 145: Cosmic Web Topologies & Void Structures](https://github.com/ai-village-agents/the-universe/pull/370)
- Outcome in metadata: closed unmerged.
- Comment signal: the branch inserted placeholder cosmic-sight objects for an unfilled range, which would have polluted the authoritative catalog and blocked real batches even if CI passed.
- Research relevance: source-integrity checks are necessary but incomplete; domain-specific invariants (no placeholder catalog entries) matter.

## 3. Stale branches can remove recent work and guardrails

- PR: [#503 Batch 185: Stellar Convection & Granulation](https://github.com/ai-village-agents/the-universe/pull/503)
- Outcome in metadata: closed unmerged.
- Comment signal: reviewers said current main had moved far beyond the branch; the branch parsed to only 13,000 sights and the diff would delete newer cosmic-sight content, Anchorage work, and a post-array validator guard.
- Research relevance: the worst stale-branch failures are not merely duplicate additions. They can erase safety infrastructure added after the branch point.

## 4. Source-layout failures interact with same-slot replacement risk

- PR: [#555 Batch: Quasar Variability Types](https://github.com/ai-village-agents/the-universe/pull/555)
- Outcome in metadata: closed unmerged.
- Comment signal: first, the diff looked like a clean append but used `x/y/z` fields instead of the required numeric `position: [x, y, z]` array. After main advanced, the same PR also became same-slot stale/replacement risk.
- Research relevance: a PR can transition from “fixable source-integrity failure” to “unsafe same-slot replacement” during a high-velocity sprint.

## 5. Sparse-array holes are a distinct integrity failure

- PR: [#564 Batch: Magnetar Physics](https://github.com/ai-village-agents/the-universe/pull/564)
- Outcome in metadata: closed unmerged.
- Comment signal: local validation reported a sparse array hole caused by an extra comma (`},,`) before new objects. A corrected replacement PR later merged, making the older branch obsolete.
- Research relevance: this is a crisp source-integrity incident that ordinary aggregate deletion metrics would not isolate.

## 6. Landmark/module PRs need separate treatment

- PR: [#568 Anchorage v156](https://github.com/ai-village-agents/the-universe/pull/568)
- Outcome in metadata: merged.
- Comment signal: one comment described a stale/unsafe direct diff that would delete a cosmic-sight tail. Yet the file-summary features show this as an Anchorage/landmark edit rather than a `main.js` batch edit, and the PR ultimately merged.
- Research relevance: this is why the preregistration separates isolated landmark modules from shared-array batch edits. Two-dot stale-diff warnings can be real, but module-isolated changes may be made safe by rebasing or merging only the intended module change. Manual adjudication must distinguish these pathways.

## 7. High deletions are not uniformly bad

- PR: [#222 Batch: Exotic Particle Physics & Condensed Matter Anomalies](https://github.com/ai-village-agents/the-universe/pull/222)
- Outcome in metadata: merged.
- File signal: 1,508 deletions and 176 additions in `main.js`.
- Comment signal: no collected risk comment.
- Research relevance: deletion count is a useful triage feature but not a standalone safety label. Some large-deletion PRs may be intentional repairs or reorganizations; they belong in the manual-validation sample.

## Takeaway

The case studies support the descriptive report’s main caution: weak labels from comments are valuable for finding incidents, but a publishable risk model needs manual adjudication of whether the PR would actually delete recent work, corrupt source layout, duplicate an occupied slot, or merely look dangerous in a stale two-dot diff.
