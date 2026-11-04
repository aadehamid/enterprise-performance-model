<!-- The decision owner's words, verbatim excerpts from the viewer request of 2026-11-03. These are instructions supplied before the scope interview. No scope recommendation has yet been accepted. -->

The owner wants the viewer shipped inside the shared release, through the cut; record that decision first.

Start with a grill-with-docs round on the viewer's scope. Then build it as the plan says: one release (share/epm-1.0 at 81f2f63b), from its Turtle or JSON-LD, no store, with the design-taste-frontend skill's app-screen route and its inspector. Every change goes through a PR with check.sh, the independent review and the Cursor verdict.

GitHub refuses Actions on the private repositories (billing). Ask me before making a repository public, and make it private again when the work is done.

Rules: name no person in tracked files; the customer model stays out of main; all repositories end private. Give me an update after each logical group of work.

<!-- Scope interview, round 1, 2026-11-03. Questions and recommendations in full, with Markdown formatting removed:

First scope round. Each “yes” accepts the recommendation.

1. Who is the viewer for? Should business reviewers be the primary audience, with technical details available on demand? I recommend plain labels and definitions first, with IRIs, predicates and provenance expandable.

2. Include the customer schema? Its entities are OWL classes, so “definitions only” could include them. I recommend a separate logical-model view showing entities, attributes, keys and ontology links. Generate it during the cut; keep customer data out of main.

3. What counts as a term? I recommend classes, properties, concepts, concept schemes and designed individuals, including system attributes. Show evidence nodes within relationship details, with separate counts. Exclude technical-graph records and example datasets.

4. How much graph appears at once? I recommend the selected term and its immediate relationships, with controls to expand further. Every term remains searchable and reachable through hierarchy or module navigation.

5. Does reviewing include writing feedback? I recommend a read-only first release: browse, search, inspect and copy term identifiers. Comments, editing and saved review work stay outside this version.

The decision owner's answer, verbatim:
-->

1. aligned
2. A viwier should be able to view all the ontology using the viewer. We do not have to exclude anything except the tecchnical graph
3. aligned
4. aligned
5. aligned

<!-- Scope interview, round 2, 2026-11-03. Question and recommendation in full, with Markdown formatting removed:

Q6. Does “exclude the technical graph” mean exclude its records, while keeping its vocabulary?

The vocabulary defines terms such as tables, pipelines and quality checks. The records describe actual tables, pipeline runs and check results.

I recommend keeping the vocabulary and excluding the records, as the existing plan specifies. A “yes” confirms this boundary and completes the scope round.

The decision owner's answer, verbatim:
-->

keep the vocabulary

<!-- Source clarification, 2026-11-03. The decision owner's words, verbatim: -->

by the way only released ontology in the private release repo will be viewed from the user. makes sesne

<!-- Value-stream navigation, 2026-11-03. The decision owner's words, verbatim: -->

for value stream, can we make sure that we can list the two value streams that we have. and then be able to drill into each one of the value stream

<!-- Viewer heading, 2026-11-03. The decision owner's words, verbatim: -->

Can we change the title below to
"MPC Business Process and Architecture Ontology"
What are the other useful information to add to the heading?

EPM ontology
One release · definitions and relationships

<!-- Customer navigation, 2026-11-03. The decision owner's words, verbatim, including the preceding explanation quoted in the request: -->

do you think we can do below. not easy to see at the moment
The conceptual model is currently browsable term by term; there is no dedicated whole-model diagram yet. Likewise, the lifecycle lacks a prominent entry point. Both need clearer navigation to make them easy to find.

<!-- Design-review cadence and subtitle, 2026-11-03. The decision owner's words, verbatim: -->

I think we should do a review before we do repository checks. Validation that everything exists in the viewer is important. But we should be able to review at a faster iteration. Once we align on a design we can do full validation and repository check before we pubslish and cut a new release with the viewer.

by the way remove "One release" from the heading

<!-- Grouped navigation request, 2026-11-03. The decision owner's words, verbatim: -->

This great I like it. Can we also have the same top tab for Order to Cash (OTC) and Commercial Hydrocarbon Lifecycle value chaisn. That way in additoon to the navigation pane we can also select them at the top of he page.
can we even generalize this for each module of the ontology.. so that the top navigation provide a way to see an overview of the modules .. we cn them drill down. We should some separate the mdoules from value streams and the customer lifecylces and conceptual data model

let us discuiss

<!-- Navigation implementation instruction, 2026-11-03. The decision owner's words, verbatim: -->

Can you go ahead an implement all of this. again let me review before we do repo wide test . Once we align on the design we can do a final comprehensive checks and repo restig and make another release that will include the viewer. makes sesne?

<!-- Temporary repository visibility permission, 2026-11-03. The decision owner's words, verbatim: -->

you can swithc the repo to public while working. Switch back to private when you are done working

<!-- Final design feedback and release authorization, 2026-11-03. The decision owner's words, verbatim: -->

Looks great! Any other improvement you will suggest or should we release this.

go ahead and cut a new release. Once this is done do we have anything else that is outstanding or is this it?
