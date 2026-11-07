# EPM-DEC-001-0114: An offline Party/Core reference and a documentation-only release

| Field | Value |
|---|---|
| Status | Decided (the decision owner, 2026-11-07) |
| Date | 2026-11-07 |
| Questions | An offline Party/Core pilot, its guide, usability, and publication without ontology or store changes |
| Source | Codex session of 2026-11-07; `answers-2026-11-07-horoi.md` |

## Context

The decision owner proposed Horoi as another way to document the ontology, in a separate `horoi_viewer/` folder. The agent inspected Horoi's source and the Brick site. Horoi supplies a readable reference-page design, but its original term renderer does not cover the project's SKOS concepts, definitions, or supporting nodes. The agent recommended a Party/Core pilot with a short usage guide and links to the existing full viewer. Brick supplied navigation ideas; adoption of another explorer remains undecided.

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
- Add the generated documentation to a copy of the release. Compare every existing path, file hash and executable mode against the baseline. No existing release file may change.
- Test navigation, search, cross-module links, source fidelity, malformed inputs, and desktop, tablet and phone layouts through `file:` with HTTP requests blocked.
- Follow the existing independent-review and Cursor-verdict process. Keep both repositories private. No new authority over business or modeling decisions is granted.

Implementation and publication are pending at this decision.

The decision owner later requested a preview review before the final release.
Publication waits for that feedback.

## Alternatives considered

- A hosted-only viewer was not selected; the accepted requirement is offline use without a server.
- A second new explorer remains deferred until the Party/Core pilot can be assessed.
- Rebuilding the ontology or reloading stores is outside the documentation-only scope.

## The decision owner's recorded words

From `business_architecture/ontology/step4/review-evidence/decision-owner-answers/answers-2026-11-07-horoi.md`:

> Let us go with your recommendation. And alos we are not chnaging the ontology so we should not have to relaod or remove the data or projection. we only need to work on the docs in the original repo and then release the docs as a new release with only the docs added to the release repo.

> yes to both.

> make this a goal until it is done and well tested

> alos use clear writing and night runs skill as well

> The most importatn thing is usability for the viewer. The user must be able to clearly undrestand the ontology and must be easy for him to underatnd the different layesr and connections withing and between modules

> let me review before the final release so that I can provide feedback as needed

## Evidence

- Horoi source at `33caa8cc916e7efb767a5c2831216ff1cb11c509`, retrieved 2026-11-07: https://github.com/kvistgaard/horoi/tree/33caa8cc916e7efb767a5c2831216ff1cb11c509. Its changelog dates the first release, 0.1.0, to 2026-11-03. The selected commit includes later changes.
- Brick's live HTML, read 2026-11-07: https://ontology.brickschema.org/. It loads RDF Garden's version-2 explorer and compressed ontology data. The browser inspection returned HTTP 429; interactive behaviour was not verified. The implementation uses no RDF Garden code.
- The existing viewer's source boundary and navigation: `business_architecture/ontology/viewer/README.md`.
- The full-cut sequence being avoided for this release: `scripts/share_release/README.md`.
