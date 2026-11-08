# EPM-DEC-001-0114: An offline Party/Core reference and a documentation-only release

| Field | Value |
|---|---|
| Status | Decided (the decision owner, 2026-11-07) |
| Date | 2026-11-07 |
| Questions | An offline Party/Core pilot, its guide, usability, and publication without ontology or store changes |
| Source | Codex session of 2026-11-07; `answers-2026-11-07-horoi.md` |

## Context

The decision owner proposed evaluating Horoi and, if used, placing it in a separate `horoi_viewer/` folder. The initial proposal is quoted below. The agent inspected Horoi's source and the Brick site. Horoi supplies a readable reference-page design, but its original term renderer does not cover the project's SKOS concepts, definitions, or supporting nodes. The agent recommended a Party/Core pilot with a short usage guide and links to the existing full viewer. Brick supplied navigation ideas; adoption of another explorer was undecided at this initial decision. The later amendments below authorize guided explorers within the same reference.

## Decision

The decision owner accepted both questions with "yes to both." The questions and recommendations are saved in the source answers file, with Markdown removed:

1. "Should the new documentation work by unzipping and opening it, with no server or internet?" Recommendation: "I recommend yes, matching the existing viewer."
2. "Should we build the Party/Core reference pilot first, with a short usage guide, and judge the need for another explorer after seeing it?" Recommendation: "I recommend yes."

The earlier instruction authorizes work on the documentation in the original repository, followed by a new release that adds only documentation to the release repository. It excludes changes to the ontology, data and projection, including reload or removal. For this documentation-only release, that instruction takes precedence over the full-cut rebuild and reload sequence in EPM-DEC-001-0110. Other kinds of release keep their existing workflow.

The later instruction makes usability the priority. Readers must be able to understand the ontology's different layers and the connections within and between modules. The goal continues until the work is done and well tested. Clear-writing and night-run apply.

## Implementation plan

These are the agent's implementation choices within the approved scope, not additional decisions attributed to the owner:

- Keep the build code, adapted page design, usage guide and tests in `horoi_viewer/` in the original repository.
- Read the published release at `8307c88d8896504d342a0d44880271ed4e6846ab`. The fetched private release branch still named that commit on 2026-11-07. Check source bytes, package manifests and hashes before building.
- Separate business concepts, vocabulary, and rules and evidence as reading groups. Preserve the predicates' meanings and distinguish module dependencies from business relationships.
- Add the generated documentation to a copy of the release. Compare every existing path, file hash and permission mode against the baseline. No existing release file may change.
- Test navigation, search, cross-module links, source fidelity, malformed inputs, and desktop, tablet and phone layouts through `file:` with HTTP requests blocked.
- Follow the existing independent-review and Cursor-verdict process. Keep the release repository private. No new authority over business or modeling decisions is granted.

Implementation and publication are pending at this decision.

The decision owner later requested a preview review before the final release.
The final approval amendment below records that feedback and authorizes publication of the reviewed candidate.

## Alternatives considered

- A hosted-only viewer was not selected; the accepted requirement is offline use without a server.
- A second new explorer was deferred until the Party/Core pilot could be assessed. The later amendments below authorize guided views within the same reference.
- Rebuilding the ontology or reloading stores is outside the documentation-only scope.

## The decision owner's recorded words

From `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-11-07-horoi.md`:

> can you take a look at and see if we can use it to document the ontology and how we can use it. If we happen to use this I am thinking we should create a new folder called horoi_viewer that contains this viewer separate from what we originally have. let us discuss

> Let us go with your recommendation. And alos we are not chnaging the ontology so we should not have to relaod or remove the data or projection. we only need to work on the docs in the original repo and then release the docs as a new release with only the docs added to the release repo.

> yes to both.

> make this a goal until it is done and well tested

> alos use clear writing and night runs skill as well

> The most importatn thing is usability for the viewer. The user must be able to clearly undrestand the ontology and must be easy for him to underatnd the different layesr and connections withing and between modules

> let me review before the final release so that I can provide feedback as needed

## Amendment, 2026-11-07: explorers, full coverage and review order

The decision owner requested improvements to the existing reference, including a customer lifecycle view and a way to walk down from a business process to its connected items. The decision owner then chose full module coverage for the final release and asked to review the improvements before that expansion. These words are saved in the same source answers file:

> in such a way that you can start from the business process and walk down everything else that is connected from the top of the tree to the lowest part of the tree.

> I love what you had. We are just making improvemnet to it. let us do that. We should also have one for customer lifecycle. Once we do this do we plan to now build for all modules in the ontology before we release?

> cover all modules for ful release

> let us review the improvement first before we go full module release.

The initial Party/Core implementation merged in PR #500. This amendment expands the final release scope; the original pilot decision remains its starting point. At this amendment, the improvements, full module expansion and final publication were pending. The final approval amendment below records the completed implementation and candidate review. The plan at this amendment was to prepare Process and Customer lifecycle entry points inside the existing reference, using its unchanged released RDF. At this amendment, the owner requested review of those improvements before expansion. The later instruction below authorizes proceeding with all modules. At this amendment, publication required a later review of the final candidate. The final approval below satisfies that requirement for the named candidate. No ontology, data or projection change is authorized.

## Further amendment, 2026-11-07: value-stream explorers

The decision owner requested Commercial Hydrocarbon Lifecycle and Order to Cash in the next preview, with easy navigation to their connected concepts. Review precedes the full release covering all ontology modules. From the same source answers file:

> this is awesome. can we alos have the two value stream - Commercial Hydrocarbob lifecyle, Order to Cash. Of course each concepts they connect to is easy to navigate too in an intutive way. Once we do this. I will review then we do a full release for all modules in the ontology

The plan at this amendment was to add both entry points inside the existing viewer and retain the connection trail. Stage order comes from the released value-stream sequence statements. This work remains part of the documentation-only scope. At this amendment, the expanded preview and full release were pending. The final approval amendment below records the completed preview review.

## Further amendment, 2026-11-07: proceed with all modules

After the value-stream preview, the decision owner authorized the expansion. From the same source answers file:

> Please go ahead and include all modules

The earlier requirement to review the explorer improvements before expansion is satisfied by this instruction. The plan at this amendment was to include every current module from the pinned release in the primary reference, search and connection views. The source ontology and existing release files remain unchanged. At this amendment, the final review was pending. The final approval below records its completion for the named candidate.

## Further amendment, 2026-11-08: measure navigation and final usability

The decision owner accepted the proposed relationship explanations, connection-group shortcuts and additional browser, keyboard and zoom checks. The same source answers file records the response and the requested measure journey:

> I am aligned with your recommendations.
> Also I am not seaing measure or KPI. is it not a module?

> so I can walk the measures wether KPI , operaytional metrics or something else to the process they measure , the data products, and the system. Basically anything they are connected with

The all-module reference and its earlier explorers merged in PR #501. The revision merged in PR #502. The final approval amendment below records the candidate review. PR #502 added a direct Measures and KPIs entry and lets readers follow a measure's asserted connections using the existing connection trail. Recorded measure kinds remain distinct; a KPI identifier or candidate flag does not itself change the classification. Relationship explanations use recorded definitions. Missing links remain missing, and a relationship such as `informsProcess` is not relabelled as measurement, ownership or computation. This revision changes the documentation only. At this amendment, the candidate review was pending. The final approval below records its completion and authorizes publication of the named candidate.

## Final approval, 2026-11-08: publish the reviewed documentation

The decision owner reviewed the combined viewer and authorized release. The same source answers file records the complete response:

> I have reviewed the viewer it looks great. I think we can release it. Any other usability improvement that you may think of?

The approved candidate includes every current module and the Process, Measures and KPIs, Customer lifecycle, Commercial Hydrocarbon Lifecycle and Order to Cash explorers. Source implementation PRs #500, #501 and #502 are merged. The candidate uses the viewer source merged in PR #502 at `506a2840d51422c69fdcaee47b5364c3e805dbbd`; its tested implementation head is `5bddff687512347bfbdc6a3dfe9799c6afd8a1a8`.

The approval applies to the reviewed HTML with SHA-256 `feeaa56bb0f1a9f872b2a736565db758fd7829ac1c0b24baa80c8a84afb94c41`, in the tested ZIP with SHA-256 `15474c4dff361b796bd4b9184195b9e33c5d68b1ee099cd227e35a5c653e7e5d`. These hashes bind the review to the candidate; the release retains the baseline at `8307c88d8896504d342a0d44880271ed4e6846ab` and adds only the generated `horoi_viewer/` files.

The final handoff disclosed unverified Firefox, Safari application and native 200% zoom coverage, plus an optional CI link-check job that failed while downloading its tool. Chrome and WebKit checks, required repository checks, exact-artifact recipient checks and independent review passed. The release evidence retains those limits.

This approval satisfies the requested final review for this candidate. Publication follows the existing documentation-only comparison and PR process. The question about other usability improvements authorizes discussion; no additional feature is part of the approved artifact. No ontology, data or projection change is authorized.

## Evidence

- Horoi source at `33caa8cc916e7efb767a5c2831216ff1cb11c509`, retrieved 2026-11-07: https://github.com/kvistgaard/horoi/tree/33caa8cc916e7efb767a5c2831216ff1cb11c509. Its changelog dates the first release, 0.1.0, to 2026-11-03. The selected commit includes later changes.
- Brick's live HTML, read 2026-11-07: https://ontology.brickschema.org/. It loads RDF Garden's version-2 explorer and compressed ontology data. The browser inspection returned HTTP 429; interactive behaviour was not verified. The implementation uses no RDF Garden code.
- The existing viewer's source boundary and navigation: `business_architecture/ontology/viewer/README.md`.
- The full-cut sequence being avoided for this release: `scripts/share_release/README.md`.
