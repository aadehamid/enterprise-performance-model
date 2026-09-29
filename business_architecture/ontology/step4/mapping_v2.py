#!/usr/bin/env python3
"""Mapping v2 builder: canonical predicate assignment, canonical facts,
mirror merges, contradiction report, and the requires/assures/enables
review tables.
"""
import csv, json, os
from collections import defaultdict, Counter

BASE = os.path.dirname(os.path.abspath(__file__))
# Proposal outputs go here — never overwrite the governed CSVs.
# canonical-facts.csv, contradictions.csv, enables-review.csv at BASE are the
# Step 4 source of truth (Hamid 2026-09-28: PR #167 HOLD). The script is a
# proposal generator until its verdict logic is brought current.
OUT = os.path.join(BASE, "proposal")
os.makedirs(OUT, exist_ok=True)
SHA = open(f"{BASE}/PINNED_SHA.txt").read().strip()
imap = {r["slug"]: r for r in json.load(open(f"{BASE}/baseline/step2-identity-map.json"))}
v2 = list(csv.DictReader(open(f"{BASE}/target-report/target-dispositions-v2.csv")))
ctx = {r["row_id"]: r["outcome"] for r in csv.DictReader(open(f"{BASE}/target-report/context-pass.csv"))}

# ---- emitting mentions: ResolvedToConcept + promoted SoleCandidate ----
# Property rule (Hamid 2026-09-24): for properties that allow mutual pairs
# (informedBy, dependsOnOutputOf), both directions emit only if EACH has its
# own evidence. A direction promoted on nearness alone is held here — this is
# a mapping-level hold, not a context outcome change.
#
# Mutual enabledBy (Hamid verdicts 2026-09-24): enablement is not reciprocal by
# default. REL-01303 and REL-01056 approved for emission (removed from holds).
# REL-01312 and REL-01053 held for source-workbook correction — the reverse
# direction means control/constraint or close-feed consumption, not capability
# enablement. See source-workbook-backlog.md.
PROPERTY_RULE_HOLDS = {
    "REL-00503": ("mutual-informedBy with REL-00500: this direction B-only "
                  "(structural nearness); held per property rule — REL-00500 (A+B) emits"),
    "REL-01312": ("Hamid 2026-09-24: HOLD for source correction. Market Risk "
                  "Management establishes risk limits and delegated authority within "
                  "which trade capture operates — governance/constraint, not "
                  "reciprocal enablement. No core:enables triple; correct the "
                  "source relationship through reviewed workbook authoring."),
    "REL-01053": ("Hamid 2026-09-24: HOLD for source correction. Period-End "
                  "Processing verifies and consumes AR reconciliation evidence; it "
                  "does not enable the reconciliation capability. No reciprocal "
                  "core:enables triple; correct the source relationship through "
                  "reviewed workbook authoring."),
    # Hamid 2026-09-25: enables sample review verdicts. These B-only rows are
    # held because "enables" flattens "informs"/"supports" — not genuine
    # capability enablement. The promotion layer must not silently translate
    # enables into informs; rows are held for workbook correction.
    "REL-00758": ("Hamid 2026-09-25: HOLD for source correction. External "
                  "research collaboration may support but is not required for "
                  "internal research. Correct to informs or a future supports "
                  "relation via reviewed workbook authoring."),
    "REL-01094": ("Hamid 2026-09-25: HOLD for source correction. Infrastructure "
                  "performance evidence informs the technology roadmap; it does "
                  "not enable technology management. Correct to informs via "
                  "reviewed workbook authoring."),
    "REL-01131": ("Hamid 2026-09-25: HOLD for source correction. Participation "
                  "analysis informs commercial/supply scoping; operational demand "
                  "management runs without it. Correct to informs via reviewed "
                  "workbook authoring."),
    "REL-01192": ("Hamid 2026-09-25: HOLD for source correction. Brand "
                  "positioning may influence channel direction but is not a "
                  "prerequisite for channel strategy. Correct to informs via "
                  "reviewed workbook authoring."),
    # Hamid 2026-09-25: held for source classification review — the business
    # must confirm whether customer-profitability analysis is plan-based
    # (dependsOnOutputOf) or actual-data-based (informs). Not rewritten in Step 4.
    "REL-00936": ("Hamid 2026-09-25: HOLD for source classification review. The "
                  "revenue plan is not demonstrated as necessary for customer "
                  "profitability analysis (which consumes actual revenue, "
                  "cost-to-serve, terms, rebates, credit data). Likely informs; "
                  "dependsOnOutputOf only if the business confirms plan-based "
                  "analysis."),
    # Hamid 2026-09-25: HOLD for source correction ("enables" flattening
    # "informed-by"). A trading-side feedstock slate/run-rate recommendation
    # feeds the binding plan without setting it — informational, not
    # enablement. Per the PTC-002 principle (Refinery Planning and Optimization
    # decides; Supply & Trading advises), the workbook verb must be corrected
    # through reviewed authoring, not reinterpreted in promotion.
    "REL-00445": ("Hamid 2026-09-25: HOLD for source correction. Recommend "
                  "Feedstock Slate and Run Rate provides a trading-side "
                  "recommendation that informs Refinery Planning and "
                  "Optimization; it does not make the planning capability able "
                  "to operate and does not set, approve, or revise the binding "
                  "plan. Correct enables to informed-by in the workbook."),
    # Hamid 2026-09-26: HOLD for workbook correction. Crude/Feed Supply
    # Management manages the feedstock supply position and associated risks; it
    # does not assure Crude/Feed Demand Management. The relationship may
    # represent coordination, fulfillment, balance, or dependency, but its
    # intended semantics and direction require workbook-author correction.
    # Remove the existing core:assuredBy fact; emit no substitute; require a
    # fresh verdict after source correction.
    "REL-01106": ("Hamid 2026-09-26: HOLD for workbook correction. Supply "
                  "position management does not assure demand management."),
    # Hamid 2026-09-26: dependsOnOutputOf contradiction resolution. A symmetric
    # core:dependsOnOutputOf pair collapses producer/consumer direction; retain
    # at most one direction per pair. REL-00917: maintaining price/discount
    # records is not shown to consume the operational output of an implemented
    # rebate arrangement (plausibly upstream master-data or co-managed config).
    # REL-00884: reconciliation outputs exposing differences do not establish
    # an essential consumed output of card-transaction management (may be
    # exception feedback / remediation loop). REL-01065: taxability assessment
    # does not consume reconciled indirect-tax reporting outputs (may be
    # feedback / reporting-impact consideration). Each needs author
    # clarification; do not reverse dependencies at promotion time.
    "REL-00917": ("Hamid 2026-09-26: HOLD for workbook correction. "
                  "dependsOnOutputOf contradiction pair A: retain REL-00862 "
                  "direction only."),
    "REL-00884": ("Hamid 2026-09-26: HOLD for workbook correction. "
                  "dependsOnOutputOf contradiction pair B: retain REL-01029 "
                  "direction only."),
    "REL-01065": ("Hamid 2026-09-26: HOLD for workbook correction. "
                  "dependsOnOutputOf contradiction pair C: retain REL-01061 "
                  "direction only."),
    # Hamid 2026-09-26: ancestor/descendant hierarchy holds. Each asserts a
    # relationship between a descendant activity and its ancestor/parent
    # capability; the hierarchy already represents composition and scope, and
    # the definitions establish no independent cross-cutting governance,
    # output-dependency, or capability-enablement relationship. Facts removed
    # (each verified unique); REL-01309 remains an already-approved exception
    # and is untouched.
    "REL-00002": ("Hamid 2026-09-26: HOLD. Hierarchy restatement: "
                  "Produce Demand Forecast <-> Prepare Master Data To Create "
                  "Demand Forecast is parent/child composition; no independent "
                  "enabledBy evidence. Fact removed."),
    "REL-00013": ("Hamid 2026-09-26: HOLD. Hierarchy restatement: "
                  "Produce Demand Forecast <-> Monitor Demand Forecasting "
                  "Performance and Reporting is parent/child composition; no "
                  "independent enabledBy evidence. Fact removed."),
    "REL-00466": ("Hamid 2026-09-26: HOLD. Hierarchy restatement: "
                  "Supply Network Participation Analysis <-> Evaluate Market "
                  "Attractiveness is parent/child composition; no independent "
                  "enabledBy evidence. Fact removed."),
    "REL-00469": ("Hamid 2026-09-26: HOLD. Hierarchy restatement: "
                  "Supply Network Participation Analysis <-> Assess "
                  "Cost-to-Serve Performance is parent/child composition; no "
                  "independent output-dependency evidence. Fact removed."),
    "REL-00764": ("Hamid 2026-09-26: HOLD. Hierarchy restatement: "
                  "Determine & Allocate Sales Targets <-> Sales Planning "
                  "governedBy merely restates containment. Fact removed."),
    "REL-00768": ("Hamid 2026-09-26: HOLD. Hierarchy restatement: "
                  "Develop & Agree Demand Forecasting Process <-> Sales "
                  "Planning governedBy merely restates containment. "
                  "Fact removed."),
    "REL-00773": ("Hamid 2026-09-26: HOLD. Hierarchy restatement: "
                  "Sales Planning <-> Analyze Gaps Between Forecast & Actual "
                  "Margins is parent/child composition; no independent "
                  "enabledBy evidence. Fact removed."),
    "REL-00912": ("Hamid 2026-09-26: HOLD. Hierarchy restatement: "
                  "Conduct Commercial Audit <-> Commercial Agreement "
                  "Compliance Management governedBy adds no separate "
                  "relationship evidence. Fact removed."),
    "REL-00923": ("Hamid 2026-09-26: HOLD. Hierarchy restatement: "
                  "Maintain Commercial Workflow Configuration <-> Manage "
                  "Commercial Master Data Stewardship governedBy adds no "
                  "separate relationship evidence. Fact removed."),
    "REL-00152": ("Hamid 2026-09-26: HOLD. Advisory/recommendation pattern "
                  "(REL-00445 family): asset optimization recommends to strategy "
                  "management; strategy management retains decision authority. "
                  "Remove this row's evidence from the fact; the fact is "
                  "preserved via the independent approved row REL-00214."),
    "REL-00262": ("Hamid 2026-09-26: HOLD. Advisory pattern: advanced "
                  "analytics recommends methodology/limit/control changes; "
                  "risk-limit management decides and administers. Fact removed."),
    "REL-00458": ("Hamid 2026-09-26: HOLD. Advisory pattern: source "
                  "recommends mitigations to accountable owners and submits "
                  "approved hedging requirements; does not enable Trading "
                  "Management as a capability. Fact removed."),
    "REL-01122": ("Hamid 2026-09-26: HOLD. Advisory pattern: the source "
                  "definition says its economic targets and allowance "
                  "recommendations inform the production schedule. Fact removed."),
    "REL-01129": ("Hamid 2026-09-26: HOLD. Advisory pattern: supply-network "
                  "participation analysis recommends where and whom to serve; "
                  "Regional Optimization is the plan-making decision process. "
                  "Fact removed."),
    "REL-00263": ("Hamid 2026-09-26: HOLD. Ambiguous enables: analytics "
                  "recommends methodology/limit/control changes, not an "
                  "operational prerequisite for governed risk reporting. Fact "
                  "removed; no emission-time remap."),
    "REL-00436": ("Hamid 2026-09-26: HOLD. Ambiguous enables: source "
                  "assertion is enables but stored as dependsOnOutputOf; a "
                  "plausible output dependency is not authorized at emission. "
                  "Remove this row's evidence; the fact is preserved via the "
                  "independent approved row REL-00447."),
    "REL-00440": ("Hamid 2026-09-26: HOLD. Ambiguous enables: coordination "
                  "may request a trade but trade capture is a controlled "
                  "authorization/recording process; likely lifecycle/input/ "
                  "handoff semantics need author confirmation. Fact removed."),
    "REL-00455": ("Hamid 2026-09-26: HOLD. Ambiguous enables: arrival "
                  "planning may inform actualization but does not clearly "
                  "make actualization capable of being performed. Fact removed."),
    "REL-00712": ("Hamid 2026-09-26: HOLD. Ambiguous enables: "
                  "approval-ready implementation recommendations do not "
                  "establish a required capability base for concept/"
                  "feasibility work. Fact removed."),
    "REL-00750": ("Hamid 2026-09-26: HOLD. Ambiguous enables: "
                  "recommendations go to delegated authorities; target "
                  "implements approved decisions; exact relationship needs "
                  "explicit correction. Fact removed."),
    "REL-01064": ("Hamid 2026-09-26: HOLD. Ambiguous enables: source "
                  "proposes treatment for Tax approval; approved changes may "
                  "feed master-data maintenance but not source-supported "
                  "enablement. Fact removed."),
    "REL-01206": ("Hamid 2026-09-26: HOLD. Ambiguous enables: lifecycle "
                  "recommendations inform delegated decisions; target governs "
                  "and implements approved changes. Fact removed."),
    "REL-00925": ("Hamid 2026-09-26: HOLD. Hierarchy restatement: "
                  "Maintain Commercial Policy Content and Approved Parameters "
                  "<-> Manage Commercial Master Data Stewardship governedBy "
                  "adds no separate relationship evidence. Fact removed."),
    # Hamid 2026-09-25: HOLD for workbook correction. The asserted requires
    # relation is not sufficiently supported as a prerequisite gate, and the
    # proposed remap to core:dependsOnOutputOf would alter source meaning at
    # emission time. Emit no triple — neither requires nor dependsOnOutputOf.
    "REL-00208": ("Hamid 2026-09-25: HOLD for workbook correction. Neither "
                  "core:requires nor core:dependsOnOutputOf may be emitted "
                  "from the present assertion; route for source-workbook "
                  "relationship review and correction"),
    # Hamid 2026-09-26: G1b no-verb-change verdict (D:hamid-verdict /
    # G1bNoVerbChange). The source assertion uses enables; the only paired
    # evidence is the reverse informed-by assertion, and there is no
    # independently approved uses-input assertion for the pair. The pipeline
    # had been storing these as core:dependsOnOutputOf on informed-by-only
    # reverse evidence - a silent verb change prohibited by Rule 11. Remove
    # the stored core:dependsOnOutputOf fact; retain the enables assertion
    # as non-emitting evidence; preserve the reverse core:informedBy fact on
    # its own source record. A corrected source assertion requires a fresh
    # verdict. REL-01224 (already held by the context-confirmation pass) is
    # governed by the same verdict but needs no code change.
    "REL-00140": ("Hamid 2026-09-26: HOLD under G1bNoVerbChange. "
                  "Source assertion uses enables; only paired evidence "
                  "is the reverse informed-by assertion; no independent "
                  "uses-input evidence exists. Stored core:dependsOnOutputOf "
                  "fact removed (Rule 11: no silent verb change); retain the "
                  "enables assertion as non-emitting evidence."),
    "REL-00499": ("Hamid 2026-09-26: HOLD under G1bNoVerbChange. "
                  "Source assertion uses enables; only paired evidence "
                  "is the reverse informed-by assertion; no independent "
                  "uses-input evidence exists. Stored core:dependsOnOutputOf "
                  "fact removed (Rule 11: no silent verb change); retain the "
                  "enables assertion as non-emitting evidence."),
    "REL-00565": ("Hamid 2026-09-26: HOLD under G1bNoVerbChange. "
                  "Source assertion uses enables; only paired evidence "
                  "is the reverse informed-by assertion; no independent "
                  "uses-input evidence exists. Stored core:dependsOnOutputOf "
                  "fact removed (Rule 11: no silent verb change); retain the "
                  "enables assertion as non-emitting evidence."),
    "REL-00648": ("Hamid 2026-09-26: HOLD under G1bNoVerbChange. "
                  "Source assertion uses enables; only paired evidence "
                  "is the reverse informed-by assertion; no independent "
                  "uses-input evidence exists. Stored core:dependsOnOutputOf "
                  "fact removed (Rule 11: no silent verb change); retain the "
                  "enables assertion as non-emitting evidence."),
    "REL-00679": ("Hamid 2026-09-26: HOLD under G1bNoVerbChange. "
                  "Source assertion uses enables; only paired evidence "
                  "is the reverse informed-by assertion; no independent "
                  "uses-input evidence exists. Stored core:dependsOnOutputOf "
                  "fact removed (Rule 11: no silent verb change); retain the "
                  "enables assertion as non-emitting evidence."),
    "REL-00709": ("Hamid 2026-09-26: HOLD under G1bNoVerbChange. "
                  "Source assertion uses enables; only paired evidence "
                  "is the reverse informed-by assertion; no independent "
                  "uses-input evidence exists. Stored core:dependsOnOutputOf "
                  "fact removed (Rule 11: no silent verb change); retain the "
                  "enables assertion as non-emitting evidence."),
    "REL-00732": ("Hamid 2026-09-26: HOLD under G1bNoVerbChange. "
                  "Source assertion uses enables; only paired evidence "
                  "is the reverse informed-by assertion; no independent "
                  "uses-input evidence exists. Stored core:dependsOnOutputOf "
                  "fact removed (Rule 11: no silent verb change); retain the "
                  "enables assertion as non-emitting evidence."),
    "REL-00973": ("Hamid 2026-09-26: HOLD under G1bNoVerbChange. "
                  "Source assertion uses enables; only paired evidence "
                  "is the reverse informed-by assertion; no independent "
                  "uses-input evidence exists. Stored core:dependsOnOutputOf "
                  "fact removed (Rule 11: no silent verb change); retain the "
                  "enables assertion as non-emitting evidence."),
    "REL-00974": ("Hamid 2026-09-26: HOLD under G1bNoVerbChange. "
                  "Source assertion uses enables; only paired evidence "
                  "is the reverse informed-by assertion; no independent "
                  "uses-input evidence exists. Stored core:dependsOnOutputOf "
                  "fact removed (Rule 11: no silent verb change); retain the "
                  "enables assertion as non-emitting evidence."),
    "REL-00977": ("Hamid 2026-09-26: HOLD under G1bNoVerbChange. "
                  "Source assertion uses enables; only paired evidence "
                  "is the reverse informed-by assertion; no independent "
                  "uses-input evidence exists. Stored core:dependsOnOutputOf "
                  "fact removed (Rule 11: no silent verb change); retain the "
                  "enables assertion as non-emitting evidence."),
    "REL-01108": ("Hamid 2026-09-26: HOLD under G1bNoVerbChange. "
                  "Source assertion uses enables; only paired evidence "
                  "is the reverse informed-by assertion; no independent "
                  "uses-input evidence exists. Stored core:dependsOnOutputOf "
                  "fact removed (Rule 11: no silent verb change); retain the "
                  "enables assertion as non-emitting evidence."),
    "REL-01112": ("Hamid 2026-09-26: HOLD under G1bNoVerbChange. "
                  "Source assertion uses enables; only paired evidence "
                  "is the reverse informed-by assertion; no independent "
                  "uses-input evidence exists. Stored core:dependsOnOutputOf "
                  "fact removed (Rule 11: no silent verb change); retain the "
                  "enables assertion as non-emitting evidence."),
    "REL-01148": ("Hamid 2026-09-26: HOLD under G1bNoVerbChange. "
                  "Source assertion uses enables; only paired evidence "
                  "is the reverse informed-by assertion; no independent "
                  "uses-input evidence exists. Stored core:dependsOnOutputOf "
                  "fact removed (Rule 11: no silent verb change); retain the "
                  "enables assertion as non-emitting evidence."),
    "REL-01151": ("Hamid 2026-09-26: HOLD under G1bNoVerbChange. "
                  "Source assertion uses enables; only paired evidence "
                  "is the reverse informed-by assertion; no independent "
                  "uses-input evidence exists. Stored core:dependsOnOutputOf "
                  "fact removed (Rule 11: no silent verb change); retain the "
                  "enables assertion as non-emitting evidence."),
    "REL-01154": ("Hamid 2026-09-26: HOLD under G1bNoVerbChange. "
                  "Source assertion uses enables; only paired evidence "
                  "is the reverse informed-by assertion; no independent "
                  "uses-input evidence exists. Stored core:dependsOnOutputOf "
                  "fact removed (Rule 11: no silent verb change); retain the "
                  "enables assertion as non-emitting evidence."),
    "REL-01181": ("Hamid 2026-09-26: HOLD under G1bNoVerbChange. "
                  "Source assertion uses enables; only paired evidence "
                  "is the reverse informed-by assertion; no independent "
                  "uses-input evidence exists. Stored core:dependsOnOutputOf "
                  "fact removed (Rule 11: no silent verb change); retain the "
                  "enables assertion as non-emitting evidence."),
    "REL-01184": ("Hamid 2026-09-26: HOLD under G1bNoVerbChange. "
                  "Source assertion uses enables; only paired evidence "
                  "is the reverse informed-by assertion; no independent "
                  "uses-input evidence exists. Stored core:dependsOnOutputOf "
                  "fact removed (Rule 11: no silent verb change); retain the "
                  "enables assertion as non-emitting evidence."),
    "REL-01191": ("Hamid 2026-09-26: HOLD under G1bNoVerbChange. "
                  "Source assertion uses enables; only paired evidence "
                  "is the reverse informed-by assertion; no independent "
                  "uses-input evidence exists. Stored core:dependsOnOutputOf "
                  "fact removed (Rule 11: no silent verb change); retain the "
                  "enables assertion as non-emitting evidence."),
    "REL-01194": ("Hamid 2026-09-26: HOLD under G1bNoVerbChange. "
                  "Source assertion uses enables; only paired evidence "
                  "is the reverse informed-by assertion; no independent "
                  "uses-input evidence exists. Stored core:dependsOnOutputOf "
                  "fact removed (Rule 11: no silent verb change); retain the "
                  "enables assertion as non-emitting evidence."),
    "REL-01197": ("Hamid 2026-09-26: HOLD under G1bNoVerbChange. "
                  "Source assertion uses enables; only paired evidence "
                  "is the reverse informed-by assertion; no independent "
                  "uses-input evidence exists. Stored core:dependsOnOutputOf "
                  "fact removed (Rule 11: no silent verb change); retain the "
                  "enables assertion as non-emitting evidence."),
    "REL-01213": ("Hamid 2026-09-26: HOLD under G1bNoVerbChange. "
                  "Source assertion uses enables; only paired evidence "
                  "is the reverse informed-by assertion; no independent "
                  "uses-input evidence exists. Stored core:dependsOnOutputOf "
                  "fact removed (Rule 11: no silent verb change); retain the "
                  "enables assertion as non-emitting evidence."),
    "REL-01225": ("Hamid 2026-09-26: HOLD under G1bNoVerbChange. "
                  "Source assertion uses enables; only paired evidence "
                  "is the reverse informed-by assertion; no independent "
                  "uses-input evidence exists. Stored core:dependsOnOutputOf "
                  "fact removed (Rule 11: no silent verb change); retain the "
                  "enables assertion as non-emitting evidence."),
    "REL-01230": ("Hamid 2026-09-26: HOLD under G1bNoVerbChange. "
                  "Source assertion uses enables; only paired evidence "
                  "is the reverse informed-by assertion; no independent "
                  "uses-input evidence exists. Stored core:dependsOnOutputOf "
                  "fact removed (Rule 11: no silent verb change); retain the "
                  "enables assertion as non-emitting evidence."),
    "REL-01233": ("Hamid 2026-09-26: HOLD under G1bNoVerbChange. "
                  "Source assertion uses enables; only paired evidence "
                  "is the reverse informed-by assertion; no independent "
                  "uses-input evidence exists. Stored core:dependsOnOutputOf "
                  "fact removed (Rule 11: no silent verb change); retain the "
                  "enables assertion as non-emitting evidence."),
    "REL-01234": ("Hamid 2026-09-26: HOLD under G1bNoVerbChange. "
                  "Source assertion uses enables; only paired evidence "
                  "is the reverse informed-by assertion; no independent "
                  "uses-input evidence exists. Stored core:dependsOnOutputOf "
                  "fact removed (Rule 11: no silent verb change); retain the "
                  "enables assertion as non-emitting evidence."),
    "REL-01273": ("Hamid 2026-09-26: HOLD under G1bNoVerbChange. "
                  "Source assertion uses enables; only paired evidence "
                  "is the reverse informed-by assertion; no independent "
                  "uses-input evidence exists. Stored core:dependsOnOutputOf "
                  "fact removed (Rule 11: no silent verb change); retain the "
                  "enables assertion as non-emitting evidence."),
    "REL-01296": ("Hamid 2026-09-26: HOLD under G1bNoVerbChange. "
                  "Source assertion uses enables; only paired evidence "
                  "is the reverse informed-by assertion; no independent "
                  "uses-input evidence exists. Stored core:dependsOnOutputOf "
                  "fact removed (Rule 11: no silent verb change); retain the "
                  "enables assertion as non-emitting evidence."),
    "REL-01315": ("Hamid 2026-09-26: HOLD under G1bNoVerbChange. "
                  "Source assertion uses enables; only paired evidence "
                  "is the reverse informed-by assertion; no independent "
                  "uses-input evidence exists. Stored core:dependsOnOutputOf "
                  "fact removed (Rule 11: no silent verb change); retain the "
                  "enables assertion as non-emitting evidence."),
    # Hamid 2026-09-26: G3 Section A1 verdicts (D:hamid-verdict). Explicit
    # target reference is not enablement proof. These 6 rows fail the
    # capability-effect test: exclusion references, informational/evidence
    # feeds, or lifecycle/sequence assertions. Remove the stored
    # core:enabledBy fact (each verified unique, single-row, no independent
    # supporter); emit no substitute predicate; retain the enables assertion
    # as non-emitting evidence; route for source-workbook correction.
    "REL-00009": ("Hamid 2026-09-26: HOLD (G3-A1). Exclusion reference: the "
                  "source scope note expressly excludes the target's receipt "
                  "and case-assembly work. Boundary statement, not affirmative "
                  "enablement evidence. Stored core:enabledBy fact removed; "
                  "no remap to dependsOnOutputOf without a distinct "
                  "uses-input assertion."),
    "REL-00041": ("Hamid 2026-09-26: HOLD (G3-A1). Informational feed: "
                  "per-movement outturn reconciliation feeds periodic "
                  "book-to-physical reconciliation, but 'feeds' is an "
                  "information/evidence contribution, not demonstrated "
                  "capability enablement. Stored core:enabledBy fact removed."),
    "REL-00054": ("Hamid 2026-09-26: HOLD (G3-A1). The source explicitly "
                  "excludes replenishment management, independently owned by "
                  "the target. Policy evidence does not establish that policy "
                  "development makes replenishment operationally capable. No "
                  "inferred governedBy/constrainedBy at emission. Stored "
                  "core:enabledBy fact removed."),
    "REL-00077": ("Hamid 2026-09-26: HOLD (G3-A1). Exclusion reference: the "
                  "source expressly excludes plan-vs-actual variance analysis "
                  "owned by the target. Performance monitoring may feed "
                  "improvement work; neither independent enablement nor basis "
                  "for an alternate predicate. Stored core:enabledBy fact "
                  "removed."),
    "REL-00118": ("Hamid 2026-09-26: HOLD (G3-A1). Input/evidence relationship: "
                  "the source's daily production balance feeds the target's "
                  "periodic reconciliation while explicitly excluding ownership "
                  "of that reconciliation. Not proven enablement. Stored "
                  "core:enabledBy fact removed."),
    "REL-00176": ("Hamid 2026-09-26: HOLD (G3-A1). Lifecycle relation: contract "
                  "termination/novation requires obligations settled or queued, "
                  "but this does not evidence that termination enables the "
                  "independent settlements capability; dependency points the "
                  "other lifecycle way. No remap authorized. Stored "
                  "core:enabledBy fact removed."),
    # Hamid 2026-09-26: G3 Section A2 verdicts (D:hamid-verdict). Explicit
    # target reference is not enablement proof. These 6 rows fail the
    # capability-effect test: analytical advice, output contribution,
    # operational feedback, informational feed, excluded scope, or
    # documentation contribution. Remove the stored core:enabledBy fact
    # (each verified unique, single-row, no independent supporter); emit no
    # substitute predicate; retain the enables assertion as non-emitting
    # evidence; route for source-workbook correction.
    "REL-00232": ("Hamid 2026-09-26: HOLD (G3-A2). Analytical advice: "
                  "portfolio-level analytics findings feed limit structures "
                  "but do not establish that credit-limit management cannot "
                  "operate without the analytics capability. Analysis/advice "
                  "to a decision authority, not demonstrated enablement. "
                  "Stored core:enabledBy fact removed; no remap to informedBy "
                  "or dependsOnOutputOf at emission."),
    "REL-00294": ("Hamid 2026-09-26: HOLD (G3-A2). Output contribution: "
                  "position and P&L analysis delivers the official economic "
                  "P&L that accounting reconciliation uses. Strong output/data "
                  "relationship, but the source assertion is enables and must "
                  "not be silently converted to dependsOnOutputOf. Stored "
                  "core:enabledBy fact removed; retained as non-emitting "
                  "evidence pending workbook correction."),
    "REL-00409": ("Hamid 2026-09-26: HOLD (G3-A2). Operational feedback: "
                  "exception patterns may feed policy improvement, but "
                  "exception management does not make the policy-development "
                  "capability able to operate. Feedback/learning, not a "
                  "maintained enabling foundation. Stored core:enabledBy fact "
                  "removed."),
    "REL-00479": ("Hamid 2026-09-26: HOLD (G3-A2). Informational feed: an "
                  "operational demand forecast informs replenishment "
                  "fulfillment, but the target receives quantities and timing "
                  "from the accountable replenishment decision owner. "
                  "Forecasting supplies neither authorization, supply source, "
                  "nor executable fulfillment capability. Stored "
                  "core:enabledBy fact removed."),
    "REL-00493": ("Hamid 2026-09-26: HOLD (G3-A2). Excluded scope: the source "
                  "explicitly excludes secondary delivery scheduling, owned by "
                  "the target. Customer-facing delivery terms may constrain "
                  "or inform delivery operations but do not prove enablement "
                  "of the target capability. Stored core:enabledBy fact "
                  "removed."),
    "REL-00517": ("Hamid 2026-09-26: HOLD (G3-A2). Documentation contribution: "
                  "documenting governed findings supplies reusable evidence to "
                  "insight stewardship; an information/documentation "
                  "contribution, not independently demonstrated enablement. "
                  "No change to dependsOnOutputOf without a separately "
                  "asserted and approved source relationship. Stored "
                  "core:enabledBy fact removed."),
    # Hamid 2026-09-26: G3 Section A3 verdicts (D:hamid-verdict). Reconciled
    # count: 12 approved / 13 held (row-level table authoritative; the
    # "14/11" summary text was a counting error). These 13 rows fail the
    # capability-effect test: documentation feeds, analytical feedback,
    # informational outputs, partitioned ownership boundaries, or
    # hierarchy-adjacent scope rather than genuine enablement. Remove the
    # stored core:enabledBy fact (each verified unique, single-row, no
    # independent supporter); emit no substitute predicate; retain the
    # enables assertion as non-emitting evidence; route for source-workbook
    # correction.
    "REL-00528": ("Hamid 2026-09-26: HOLD (G3-A3). Documentation feed: source "
                  "documents and distributes governed company findings and "
                  "maintains a reusable findings library — evidence management "
                  "and information distribution, not a separately demonstrated "
                  "enabling capability. Stored core:enabledBy fact removed; "
                  "no silent conversion to output dependency."),
    "REL-00539": ("Hamid 2026-09-26: HOLD (G3-A3). Documentation feed: source "
                  "documents consumer findings and maintains the findings "
                  "library — information distribution, not enablement of "
                  "insight stewardship. Stored core:enabledBy fact removed."),
    "REL-00551": ("Hamid 2026-09-26: HOLD (G3-A3). Documentation feed: source "
                  "documents customer/marketer findings — evidence management, "
                  "not a separately demonstrated enabling capability. Stored "
                  "core:enabledBy fact removed."),
    "REL-00562": ("Hamid 2026-09-26: HOLD (G3-A3). Documentation feed: source "
                  "documents competitor findings — information distribution, "
                  "not enablement. Stored core:enabledBy fact removed."),
    "REL-00665": ("Hamid 2026-09-26: HOLD (G3-A3). Partitioned ownership: the "
                  "source develops channel design and engagement-model "
                  "structure but explicitly excludes partner-management "
                  "execution, which the target performs. Approved design "
                  "direction may inform the target but does not establish a "
                  "maintained capability base or prerequisite enabling the "
                  "target process. Stored core:enabledBy fact removed."),
    "REL-00811": ("Hamid 2026-09-26: HOLD (G3-A3). Forecast input, not "
                  "enablement: the promotional event calendar is a forecast "
                  "input to the demand-forecasting process, not a capability "
                  "that makes the target able to operate. Stored "
                  "core:enabledBy fact removed; no change to dependsOnOutputOf "
                  "or informedBy at promotion."),
    "REL-00818": ("Hamid 2026-09-26: HOLD (G3-A3). Analytical feedback: "
                  "marketing spend analysis informs future resource "
                  "allocation; the target operates on approved strategy and "
                  "delegated authority. Analysis is feedback, not independent "
                  "enablement. Stored core:enabledBy fact removed."),
    "REL-00820": ("Hamid 2026-09-26: HOLD (G3-A3). Analytical feedback: "
                  "campaign ROI analysis informs mix-model decisions; not an "
                  "enabling prerequisite. Stored core:enabledBy fact removed."),
    "REL-00834": ("Hamid 2026-09-26: HOLD (G3-A3). Forecast input, not "
                  "enablement: sales pipeline evidence is explicitly an input "
                  "to the forecast-input process; it does not enable the "
                  "process as a maintained operating capability. Stored "
                  "core:enabledBy fact removed."),
    "REL-00843": ("Hamid 2026-09-26: HOLD (G3-A3). Hierarchy-adjacent: Develop "
                  "Quote is part of the target capability's stated scope; the "
                  "supplied definitions do not establish that the source "
                  "enables the broader target capability. Stored "
                  "core:enabledBy fact removed."),
    "REL-00846": ("Hamid 2026-09-26: HOLD (G3-A3). Partitioned ownership: the "
                  "source definition partitions commercial stewardship from "
                  "target-owned transactional order and fulfillment records; "
                  "definitions do not establish enablement. Stored "
                  "core:enabledBy fact removed."),
    "REL-00851": ("Hamid 2026-09-26: HOLD (G3-A3). Informational contribution: "
                  "sales-execution reporting provides evidence to planning "
                  "feedback loops — an informational contribution, not "
                  "enablement of gap analysis. Stored core:enabledBy fact "
                  "removed."),
    "REL-00852": ("Hamid 2026-09-26: HOLD (G3-A3). Informational contribution: "
                  "sales-execution reporting feeds marketing-performance "
                  "feedback — an informational contribution, not enablement. "
                  "Stored core:enabledBy fact removed."),
    # Hamid 2026-09-26: G3 Section A4 verdicts (D:hamid-verdict). Reconciled
    # count: 16 approved / 9 held (row-level table authoritative; the
    # "13/12" summary text was a counting error — the table's verdict rows
    # plus per-row hold narratives all say 16/9). These 9 rows fail the
    # capability-effect test: transaction/data feeds, operational outputs,
    # specialist accounting outcomes, lifecycle handoffs, boundary-limited
    # coordination, or informational contributions rather than genuine
    # enablement. Remove the stored core:enabledBy fact (each verified
    # unique, single-row, no independent supporter); emit no substitute
    # predicate; retain the enables assertion as non-emitting evidence;
    # route for source-workbook correction.
    "REL-00857": ("Hamid 2026-09-26: HOLD (G3-A4). Deployment/data-consumption: "
                  "the source coordinates deployment of approved price changes "
                  "and lists invoicing as a downstream consumer — not evidence "
                  "that price implementation makes the billing capability able "
                  "to operate. Stored core:enabledBy fact removed; no remap."),
    "REL-00886": ("Hamid 2026-09-26: HOLD (G3-A4). Operational-data feed: "
                  "loyalty-program operation produces records that analysis "
                  "consumes, but the target explicitly performs performance "
                  "analysis 'never as program operation'. Not enablement. "
                  "Stored core:enabledBy fact removed."),
    "REL-00889": ("Hamid 2026-09-26: HOLD (G3-A4). Boundary statement: card "
                  "billing coordination supplies validated data and statement "
                  "requirements while invoice creation, correction, reversal, "
                  "and distribution stay under the target's own controls — an "
                  "informational/billing-readiness contribution, not "
                  "enablement. Stored core:enabledBy fact removed."),
    "REL-00898": ("Hamid 2026-09-26: HOLD (G3-A4). Input/data relationship: "
                  "delinquency and collections-referral activity supplies "
                  "portfolio and collection-status data for bad-debt "
                  "assessment; Finance-controlled expected-credit-loss "
                  "estimation and write-off are distinct decision/accounting "
                  "processes. Stored core:enabledBy fact removed."),
    "REL-01038": ("Hamid 2026-09-26: HOLD (G3-A4). Exception/lifecycle "
                  "handoff: receivables disputes release invalid disputes to "
                  "collection but do not provide the maintained operational "
                  "base making collections capable of operating. Stored "
                  "core:enabledBy fact removed; no remap at promotion."),
    "REL-01072": ("Hamid 2026-09-26: HOLD (G3-A4). Output/input relationship: "
                  "royalty/fee/contribution administration creates specialized "
                  "financial outcomes or source data, but does not enable the "
                  "general billing capability. Stored core:enabledBy fact "
                  "removed; remains non-emitting until source correction."),
    "REL-01073": ("Hamid 2026-09-26: HOLD (G3-A4). Output/input relationship: "
                  "royalty/fee/contribution administration supplies outcomes "
                  "to close, but does not enable the period-end-close "
                  "capability. Stored core:enabledBy fact removed; remains "
                  "non-emitting until source correction."),
    "REL-01082": ("Hamid 2026-09-26: HOLD (G3-A4). Coordination/support: the "
                  "source coordinates workplace needs, upkeep, moves, and "
                  "compliance with corporate owners; it does not own "
                  "facilities capability or establish a maintained operating "
                  "base for service operations. Stored core:enabledBy fact "
                  "removed."),
    "REL-01092": ("Hamid 2026-09-26: HOLD (G3-A4). Evidence/output "
                  "relationship: service-event completion supplies confirmed "
                  "fulfilment evidence and billable event data — evidence for "
                  "billing, not an independent enabling capability. Stored "
                  "core:enabledBy fact removed; no silent conversion to "
                  "dependsOnOutputOf."),
    # Hamid 2026-09-26: G3 Section A5 verdicts (D:hamid-verdict). Reconciled
    # count: 14 approved / 11 held (row-level table authoritative; the
    # "13/12" summary text was a counting error). These 11 rows fail the
    # capability-effect test: analytical/evidence feeds, operational outputs,
    # forecast inputs, lifecycle handoffs, cross-capability partitions, or
    # coordination functions rather than genuine enablement. Remove the
    # stored core:enabledBy fact (each verified unique, single-row, no
    # independent supporter); emit no substitute predicate; retain the
    # enables assertion as non-emitting evidence; route for source-workbook
    # correction.
    "REL-01157": ("Hamid 2026-09-26: HOLD (G3-A5). Analysis/evidence feed: "
                  "marketing performance analysis produces evidence that "
                  "sales planning may use, but does not establish a maintained "
                  "enabling foundation. Stored core:enabledBy fact removed; "
                  "no conversion to output dependency without an independently "
                  "asserted and approved source relationship."),
    "REL-01163": ("Hamid 2026-09-26: HOLD (G3-A5). Output/evidence feed: "
                  "service delivery supplies billable fulfilment evidence to "
                  "invoicing — an output/evidence feed, not an enabling "
                  "capability. Stored core:enabledBy fact removed."),
    "REL-01171": ("Hamid 2026-09-26: HOLD (G3-A5). Output/lifecycle "
                  "relation: secondary distribution management supplies "
                  "delivery outcomes for Distribution Backcasting, which owns "
                  "plan-variance analysis. Stored core:enabledBy fact removed."),
    "REL-01178": ("Hamid 2026-09-26: HOLD (G3-A5). Analysis feed: company "
                  "analysis produces evidence that insight stewardship may "
                  "synthesize — information/analytical-feed relationship, not "
                  "enablement. Stored core:enabledBy fact removed."),
    "REL-01182": ("Hamid 2026-09-26: HOLD (G3-A5). Analysis feed: consumer "
                  "analysis produces evidence for insight stewardship, not a "
                  "maintained enabling foundation. Stored core:enabledBy fact "
                  "removed."),
    "REL-01185": ("Hamid 2026-09-26: HOLD (G3-A5). Analysis feed: customer and "
                  "marketer analysis produces evidence for insight "
                  "stewardship — analytical feed, not enablement. Stored "
                  "core:enabledBy fact removed."),
    "REL-01210": ("Hamid 2026-09-26: HOLD (G3-A5). Partitioned coordination: "
                  "R&D Collaboration coordinates governed channels, "
                  "confidentiality, and intake but explicitly excludes "
                  "development work — supports collaboration without becoming "
                  "the capability that enables development. Stored "
                  "core:enabledBy fact removed."),
    "REL-01216": ("Hamid 2026-09-26: HOLD (G3-A5). Forecast input: "
                  "promotional calendars feed the demand-forecast-input "
                  "process — a forecast input, not enablement. Stored "
                  "core:enabledBy fact removed."),
    "REL-01254": ("Hamid 2026-09-26: HOLD (G3-A5). Cross-capability "
                  "partition: commercial terms/quoting are adjacent O2C "
                  "controls; the source explicitly excludes order capture "
                  "and fulfilment, which the target owns. Not independent "
                  "enablement. Stored core:enabledBy fact removed."),
    "REL-01257": ("Hamid 2026-09-26: HOLD (G3-A5). Output/lifecycle "
                  "relation: order/fulfilment management supplies completion "
                  "evidence to billing; it does not enable billing as a "
                  "capability. Stored core:enabledBy fact removed."),
    "REL-01262": ("Hamid 2026-09-26: HOLD (G3-A5). Non-enabling "
                  "coordination: customer requests/inquiries can route or "
                  "communicate disputes, but receivables-dispute adjudication "
                  "is independently owned and not enabled by customer-service "
                  "capability. Stored core:enabledBy fact removed."),
    # Hamid 2026-09-26: G3 Section A6 verdicts (D:hamid-verdict). Final
    # explicit-reference section: 4 approvals / 2 holds (table is
    # authoritative; no count conflict). These 2 rows fail the
    # capability-effect test: adjacent/independent functions rather than
    # genuine enablement. Remove the stored core:enabledBy fact (each
    # verified unique, single-row, no independent supporter); emit no
    # substitute predicate; retain the enables assertion as non-emitting
    # evidence; route for source-workbook correction.
    "REL-01277": ("Hamid 2026-09-26: HOLD (G3-A6). Adjacent execution: "
                  "Sales Execution produces pipeline, opportunities, "
                  "key-account activity, quotes, contracts, and qualified "
                  "outcomes that hand into controlled transaction processes — "
                  "it is a consumer or participant in the broader O2C "
                  "commercial-control capability, not a maintained enabling "
                  "base for it. Stored core:enabledBy fact removed."),
    "REL-01299": ("Hamid 2026-09-26: HOLD (G3-A6). Independent-function "
                  "exclusion: Confirmations Management independently "
                  "confirms, matches, documents, modifies, reports, and "
                  "resolves discrepancies in executed trade confirmations; "
                  "the reference excerpt explicitly excludes deal-level "
                  "confirmation from Contract Management's scope. Contract "
                  "terms may be a relevant input, but the evidence does not "
                  "establish a distinct enablement relation. Stored "
                  "core:enabledBy fact removed; no remap at promotion."),
    # Hamid 2026-09-26: G3 Section B1 verdicts (D:hamid-verdict). The first
    # nearness-only chunk: all 15 rows HELD. Each candidate target was
    # selected solely by classifier nearness (unique label matching), with
    # no stable identifier, explicit target name, or source-definition /
    # scope-note evidence linking the source to that target. Per the
    # locked G3 decision test, target identity must be explicit and valid
    # before predicate review is even reached: 13 rows have plausible but
    # unconfirmed targets (identity verdict: plausible/unconfirmed); 2 rows
    # (REL-00164, REL-00239) have the candidate target rejected as
    # semantically misaligned. Remove the stored core:enabledBy fact (each
    # verified unique, single-row, no independent supporter); no retarget
    # or remap at promotion; retain the enables assertion as non-emitting
    # evidence; route for source-workbook target clarification.
    "REL-00032": ("Hamid 2026-09-26: HOLD (G3-B1). Target identity "
                  "unconfirmed: nearness-only candidate; no source-level "
                  "evidence identifies the target. Stored core:enabledBy "
                  "fact removed; no emission without workbook-author target "
                  "confirmation and fresh verdict."),
    "REL-00044": ("Hamid 2026-09-26: HOLD (G3-B1). Target identity "
                  "unconfirmed: lot/batch records may relate to inventory "
                  "reconciliation, but the source definition does not name "
                  "periodic book-to-physical reconciliation as the target. "
                  "Stored core:enabledBy fact removed."),
    "REL-00046": ("Hamid 2026-09-26: HOLD (G3-B1). Target identity "
                  "unconfirmed: third-party storage positions may relate to "
                  "inventory reconciliation, but the source does not name it. "
                  "Stored core:enabledBy fact removed."),
    "REL-00059": ("Hamid 2026-09-26: HOLD (G3-B1). Target identity "
                  "unconfirmed: likely output/evidence semantics for "
                  "distribution backcasting (which owns plan-vs-actual "
                  "distribution analysis), not source-named enablement. "
                  "Stored core:enabledBy fact removed."),
    "REL-00061": ("Hamid 2026-09-26: HOLD (G3-B1). Target identity "
                  "unconfirmed: consignment ownership may relate to "
                  "inventory reconciliation, but the source definition does "
                  "not establish it as the target. Stored core:enabledBy "
                  "fact removed."),
    "REL-00063": ("Hamid 2026-09-26: HOLD (G3-B1). Target identity "
                  "unconfirmed: commingled allocation records may relate to "
                  "inventory reconciliation, but the source does not name it. "
                  "Stored core:enabledBy fact removed."),
    "REL-00075": ("Hamid 2026-09-26: HOLD (G3-B1). Target identity "
                  "unconfirmed: scheduling master data proximity to order "
                  "generation; likely input/constraint/coordination, not "
                  "confirmed enablement. Stored core:enabledBy fact removed."),
    "REL-00121": ("Hamid 2026-09-26: HOLD (G3-B1). Target identity "
                  "unconfirmed: scheduling master data proximity to "
                  "production-wheel review; predicate not confirmed. "
                  "Stored core:enabledBy fact removed."),
    "REL-00133": ("Hamid 2026-09-26: HOLD (G3-B1). Target identity "
                  "unconfirmed: interface management proximity to sequencing "
                  "plan creation; no source-level target evidence. Stored "
                  "core:enabledBy fact removed."),
    "REL-00138": ("Hamid 2026-09-26: HOLD (G3-B1). Target identity "
                  "unconfirmed: energy-balance targets proximity to daily "
                  "execution planning; no source-level target evidence. "
                  "Stored core:enabledBy fact removed."),
    "REL-00148": ("Hamid 2026-09-26: HOLD (G3-B1). Target identity "
                  "unconfirmed: renewable forecasts could inform asset "
                  "optimization, but the target is not evidenced; likely "
                  "informational input rather than enablement. Stored "
                  "core:enabledBy fact removed."),
    "REL-00156": ("Hamid 2026-09-26: HOLD (G3-B1). Target identity "
                  "unconfirmed: generation forecasts could inform asset "
                  "optimization, but the target is not evidenced; likely "
                  "output dependency rather than enablement. Stored "
                  "core:enabledBy fact removed."),
    "REL-00164": ("Hamid 2026-09-26: HOLD (G3-B1). Target identity REJECTED: "
                  "monitoring contracts surfaces obligations/expiries/breaches "
                  "— it does not provide the governed strategy-definition, "
                  "authority, or operating base needed to develop and steward "
                  "trading strategies. Candidate selection rests only on "
                  "nearness/label matching. No retargeting or inference of "
                  "an alternative. Stored core:enabledBy fact removed."),
    "REL-00166": ("Hamid 2026-09-26: HOLD (G3-B1). Target identity "
                  "unconfirmed: counterparty records may be necessary for "
                  "trade capture, but the source does not identify Trade "
                  "Capture — could relate to onboarding, credit, compliance, "
                  "settlement, or master-data controls. Stored "
                  "core:enabledBy fact removed."),
    "REL-00239": ("Hamid 2026-09-26: HOLD (G3-B1). Target identity REJECTED: "
                  "credit-risk reporting may inform strategy review but does "
                  "not enable the strategy-management capability. Candidate "
                  "selection rests only on nearness/label matching. No "
                  "retargeting or inference of an alternative. Stored "
                  "core:enabledBy fact removed."),
    # Hamid 2026-09-26: G3 Section B2 verdicts (D:hamid-verdict). Second
    # nearness-only chunk: all 15 rows HELD at the target-identity gate —
    # no predicate review reached. 13 rows have plausible but unconfirmed
    # targets; 2 rows (REL-00266, REL-00285) have the candidate target
    # rejected as semantically misaligned. Remove the stored
    # core:enabledBy fact (each verified unique, single-row, no
    # independent supporter); no retarget or remap at promotion; retain
    # the enables assertion as non-emitting evidence; route for
    # source-workbook target clarification.
    "REL-00253": ("Hamid 2026-09-26: HOLD (G3-B2). Target identity "
                  "unconfirmed: nearness-only candidate; confirmation "
                  "disputes may affect settlement readiness but the target "
                  "is not source-evidenced. Stored core:enabledBy fact "
                  "removed."),
    "REL-00257": ("Hamid 2026-09-26: HOLD (G3-B2). Target identity "
                  "unconfirmed: risk-policy compliance may contribute to "
                  "risk reporting but the target is not source-evidenced. "
                  "Stored core:enabledBy fact removed."),
    "REL-00259": ("Hamid 2026-09-26: HOLD (G3-B2). Target identity "
                  "unconfirmed: scenarios/risk controls may relate to risk "
                  "limit management but the target is not source-evidenced. "
                  "Stored core:enabledBy fact removed."),
    "REL-00260": ("Hamid 2026-09-26: HOLD (G3-B2). Target identity "
                  "unconfirmed: month-end risk controls may relate to risk "
                  "reporting but the target is not source-evidenced. "
                  "Stored core:enabledBy fact removed."),
    "REL-00266": ("Hamid 2026-09-26: HOLD (G3-B2). Target identity REJECTED: "
                  "risk reporting provides controlled information to "
                  "management and committees — it does not provide an "
                  "operating basis that enables Trading Strategy "
                  "Management's define/approve/steward/review/retire "
                  "function. Candidate selection rests only on "
                  "nearness/label matching. No retargeting or inference. "
                  "Stored core:enabledBy fact removed."),
    "REL-00283": ("Hamid 2026-09-26: HOLD (G3-B2). Target identity "
                  "unconfirmed: risk-policy compliance may relate to risk "
                  "reporting but the target is not source-evidenced. "
                  "Stored core:enabledBy fact removed."),
    "REL-00285": ("Hamid 2026-09-26: HOLD (G3-B2). Target identity REJECTED: "
                  "risk limits constrain strategy management and inform "
                  "compliance boundaries, but Trading Strategy Management "
                  "is not shown as the target of a valid enablement "
                  "relation; likely semantics are governance/constraint or "
                  "information, not enablement. Candidate selection rests "
                  "only on nearness/label matching. No retargeting or "
                  "inference. Stored core:enabledBy fact removed."),
    "REL-00362": ("Hamid 2026-09-26: HOLD (G3-B2). Target identity "
                  "unconfirmed: accruals may relate to trading sub-ledger "
                  "operations but the target is not source-evidenced. "
                  "Stored core:enabledBy fact removed."),
    "REL-00364": ("Hamid 2026-09-26: HOLD (G3-B2). Target identity "
                  "unconfirmed: taxes may relate to trading sub-ledger "
                  "operations but the target is not source-evidenced. "
                  "Stored core:enabledBy fact removed."),
    "REL-00371": ("Hamid 2026-09-26: HOLD (G3-B2). Target identity "
                  "unconfirmed: production/inventory accounting may relate "
                  "to trading sub-ledger but the target is not "
                  "source-evidenced. Stored core:enabledBy fact removed."),
    "REL-00387": ("Hamid 2026-09-26: HOLD (G3-B2). Target identity "
                  "unconfirmed: financial-system configuration may relate "
                  "to AR/AP operations but the target is not "
                  "source-evidenced. Stored core:enabledBy fact removed."),
    "REL-00392": ("Hamid 2026-09-26: HOLD (G3-B2). Target identity "
                  "unconfirmed: compliance policies may shape internal "
                  "compliance monitoring but the target is not "
                  "source-evidenced. Stored core:enabledBy fact removed."),
    "REL-00405": ("Hamid 2026-09-26: HOLD (G3-B2). Target identity "
                  "unconfirmed: RIN reporting may relate to external "
                  "compliance monitoring but the target is not "
                  "source-evidenced. Stored core:enabledBy fact removed."),
    "REL-00428": ("Hamid 2026-09-26: HOLD (G3-B2). Target identity "
                  "unconfirmed: feedstock-data quality plausibly underpins "
                  "term-slate quality screening, but the target was "
                  "selected solely by classifier nearness with no "
                  "source-backed target identification; the 2026-09-25 "
                  "plausibility-based approval is superseded. No retarget "
                  "or remap at promotion. Stored core:enabledBy fact "
                  "removed; removed from EN_ENABLEDBY_OVERRIDE."),
    "REL-00431": ("Hamid 2026-09-26: HOLD (G3-B2). Target identity "
                  "unconfirmed: LP-model integrity may support development "
                  "of a term procurement slate but the target is not "
                  "source-evidenced. Stored core:enabledBy fact removed."),
    # Hamid 2026-09-26: G3 Section B3 verdicts (D:hamid-verdict). Third
    # nearness-only chunk: all 15 rows HELD at the target-identity gate —
    # no predicate review reached. 14 rows are TargetIdentityUnconfirmed;
    # REL-00770 carries a formal supersession of its 2026-09-25 approval
    # (predicate plausibility cannot substitute for source-backed target
    # identity under the Hamid-approved nearness-only identity rule).
    # Remove the stored core:enabledBy fact (each verified unique,
    # single-row, no independent supporter); no retarget or remap at
    # promotion; retain the enables assertion as non-emitting evidence;
    # route for source-workbook target clarification.
    "REL-00437": ("Hamid 2026-09-26: HOLD (G3-B3). Target identity "
                  "unconfirmed: nearness-only candidate; no source-backed "
                  "evidence identifies the target. Stored core:enabledBy "
                  "fact removed."),
    "REL-00494": ("Hamid 2026-09-26: HOLD (G3-B3). Target identity "
                  "unconfirmed: nearness-only candidate; no source-backed "
                  "evidence identifies the target. Stored core:enabledBy "
                  "fact removed."),
    "REL-00506": ("Hamid 2026-09-26: HOLD (G3-B3). Target identity "
                  "unconfirmed: nearness-only candidate; no source-backed "
                  "evidence identifies the target. Stored core:enabledBy "
                  "fact removed."),
    "REL-00681": ("Hamid 2026-09-26: HOLD (G3-B3). Target identity "
                  "unconfirmed: nearness-only candidate; no source-backed "
                  "evidence identifies the target. Stored core:enabledBy "
                  "fact removed."),
    "REL-00683": ("Hamid 2026-09-26: HOLD (G3-B3). Target identity "
                  "unconfirmed: nearness-only candidate; no source-backed "
                  "evidence identifies the target. Stored core:enabledBy "
                  "fact removed."),
    "REL-00687": ("Hamid 2026-09-26: HOLD (G3-B3). Target identity "
                  "unconfirmed: nearness-only candidate; no source-backed "
                  "evidence identifies the target. Stored core:enabledBy "
                  "fact removed."),
    "REL-00699": ("Hamid 2026-09-26: HOLD (G3-B3). Target identity "
                  "unconfirmed: nearness-only candidate; no source-backed "
                  "evidence identifies the target. Stored core:enabledBy "
                  "fact removed."),
    "REL-00753": ("Hamid 2026-09-26: HOLD (G3-B3). Target identity "
                  "unconfirmed: nearness-only candidate; no source-backed "
                  "evidence identifies the target. Stored core:enabledBy "
                  "fact removed."),
    "REL-00755": ("Hamid 2026-09-26: HOLD (G3-B3). Target identity "
                  "unconfirmed: nearness-only candidate; no source-backed "
                  "evidence identifies the target. Stored core:enabledBy "
                  "fact removed."),
    "REL-00756": ("Hamid 2026-09-26: HOLD (G3-B3). Target identity "
                  "unconfirmed: nearness-only candidate; no source-backed "
                  "evidence identifies the target. Stored core:enabledBy "
                  "fact removed."),
    "REL-00762": ("Hamid 2026-09-26: HOLD (G3-B3). Target identity "
                  "unconfirmed: nearness-only candidate; no source-backed "
                  "evidence identifies the target. Stored core:enabledBy "
                  "fact removed."),
    "REL-00766": ("Hamid 2026-09-26: HOLD (G3-B3). Target identity "
                  "unconfirmed: nearness-only candidate; no source-backed "
                  "evidence identifies the target. Stored core:enabledBy "
                  "fact removed."),
    "REL-00767": ("Hamid 2026-09-26: HOLD (G3-B3). Target identity "
                  "unconfirmed: nearness-only candidate; no source-backed "
                  "evidence identifies the target. Stored core:enabledBy "
                  "fact removed."),
    "REL-00770": ("Hamid 2026-09-26: HOLD (G3-B3) / TargetIdentityUnconfirmed "
                  "/ Supersedes2026-09-25Approval. The 2026-09-25 approval "
                  "recognized a plausible semantic relationship (account "
                  "planning provides account-level objectives, opportunity "
                  "maps, action plans, and resource assumptions that Sales "
                  "Execution may use), but the original source assertion "
                  "does not identify Sales Execution as its target. Under "
                  "the subsequently approved nearness-only identity rule, "
                  "predicate plausibility cannot substitute for "
                  "source-backed target identity. Supersede the prior "
                  "row-level approval (retained in provenance as "
                  "superseded, not deleted); remove the current "
                  "core:enabledBy fact; emit no substitute or retargeted "
                  "fact; require source-workbook target clarification and "
                  "a fresh verdict."),
    "REL-00837": ("Hamid 2026-09-26: HOLD (G3-B3). Target identity "
                  "unconfirmed: nearness-only candidate; no source-backed "
                  "evidence identifies the target. Stored core:enabledBy "
                  "fact removed."),
    # Hamid 2026-09-26: G3 Section B4 verdicts (D:hamid-verdict). Fourth
    # nearness-only chunk: all 15 rows HELD at the target-identity gate.
    # 13 rows are TargetIdentityUnconfirmed; REL-00960 is
    # TargetIdentityRejected (order-book tracking has nothing to do with
    # running the customer self-service portal — neither definition
    # supports the label-matched candidate); REL-00939 carries a formal
    # supersession of its 2026-09-25 approval (plausibility cannot stand
    # in for a named target under the identity rule). Remove the stored
    # core:enabledBy fact (each verified unique, single-row, no
    # independent supporter); no retarget or remap at promotion; retain
    # the enables assertion as non-emitting evidence; route for
    # source-workbook target clarification.
    "REL-00867": ("Hamid 2026-09-26: HOLD (G3-B4). Target identity unconfirmed: nearness-only candidate; no source-backed evidence identifies the target. Stored core:enabledBy fact removed."),
    "REL-00871": ("Hamid 2026-09-26: HOLD (G3-B4). Target identity unconfirmed: nearness-only candidate; no source-backed evidence identifies the target. Stored core:enabledBy fact removed."),
    "REL-00906": ("Hamid 2026-09-26: HOLD (G3-B4). Target identity unconfirmed: nearness-only candidate; no source-backed evidence identifies the target. Stored core:enabledBy fact removed."),
    "REL-00914": ("Hamid 2026-09-26: HOLD (G3-B4). Target identity unconfirmed: nearness-only candidate; no source-backed evidence identifies the target. Stored core:enabledBy fact removed."),
    "REL-00919": ("Hamid 2026-09-26: HOLD (G3-B4). Target identity unconfirmed: nearness-only candidate; no source-backed evidence identifies the target. Stored core:enabledBy fact removed."),
    "REL-00924": ("Hamid 2026-09-26: HOLD (G3-B4). Target identity unconfirmed: nearness-only candidate; no source-backed evidence identifies the target. Stored core:enabledBy fact removed."),
    "REL-00929": ("Hamid 2026-09-26: HOLD (G3-B4). Target identity unconfirmed: nearness-only candidate; no source-backed evidence identifies the target. Stored core:enabledBy fact removed."),
    "REL-00938": ("Hamid 2026-09-26: HOLD (G3-B4). Target identity unconfirmed: nearness-only candidate; no source-backed evidence identifies the target. Stored core:enabledBy fact removed."),
    "REL-00942": ("Hamid 2026-09-26: HOLD (G3-B4). Target identity unconfirmed: nearness-only candidate; no source-backed evidence identifies the target. Stored core:enabledBy fact removed."),
    "REL-00996": ("Hamid 2026-09-26: HOLD (G3-B4). Target identity unconfirmed: nearness-only candidate; no source-backed evidence identifies the target. Stored core:enabledBy fact removed."),
    "REL-00999": ("Hamid 2026-09-26: HOLD (G3-B4). Target identity unconfirmed: nearness-only candidate; no source-backed evidence identifies the target. Stored core:enabledBy fact removed."),
    "REL-01009": ("Hamid 2026-09-26: HOLD (G3-B4). Target identity unconfirmed: nearness-only candidate; no source-backed evidence identifies the target. Stored core:enabledBy fact removed."),
    "REL-01013": ("Hamid 2026-09-26: HOLD (G3-B4). Target identity unconfirmed: nearness-only candidate; no source-backed evidence identifies the target. Stored core:enabledBy fact removed."),
    "REL-00939": ("Hamid 2026-09-26: HOLD (G3-B4) / TargetIdentityUnconfirmed / Supersedes2026-09-25Approval. The 2026-09-25 approval found that approved financing/payment methods, terms, eligibility, and commercial rules are governed prerequisites for billing — which may well be true — but the source row never names Manage Customer Invoicing and Billing as its target. Under the nearness-only identity rule, a plausible relationship cannot stand in for a named target. Supersede the prior approval (retained in provenance as superseded, not deleted); remove the current core:enabledBy fact; emit no substitute or retargeted fact; require source-workbook target clarification and a fresh verdict."),
    "REL-00960": ("Hamid 2026-09-26: HOLD (G3-B4) / TargetIdentityRejected. Tracking the order book and forecasting order volumes gives scheduling and supply their planning basis; it has nothing to do with running the customer self-service portal. The label match reads the source order-tracking work as operating the portal, and neither definition supports that. Candidate selection rests only on nearness/label matching. No retargeting or inference. Stored core:enabledBy fact removed."),
    # Hamid 2026-09-26: G3 Section B5 — prior-approval sweep supersessions
    # (D:hamid-verdict). Nine earlier approvals whose targets were matched
    # by nearness only. Each approval judged relationship plausibility, not
    # target identity; no source row evidences which target was meant.
    # All nine superseded under the nearness-only identity rule; prior
    # decisions retained in provenance as superseded, not deleted.
    "REL-00129": ("Hamid 2026-09-26: HOLD (G3-B5) / TargetIdentityUnconfirmed / Supersedes2026-09-25Review32Approval. Prior approval: review32 2026-09-25 (Approved as core:enables: schedule exceptions produce exception records/causes that performance measurement explicitly analyzes) + G2 ExistingRowLevelApproval exception. Target: Measure Production Scheduling Performance.. approval judged the relationship plausible; the source row gives no evidence of which target was meant; superseded under the nearness-only identity rule. The G2 disguised-sequence exception also goes: the enables fact is absent; the independently recorded precedes/follows facts stay. Stored core:enabledBy fact removed (verified unique); no substitute; assertion retained as non-emitting evidence; route for source-workbook target clarification and a fresh verdict."),
    "REL-00243": ("Hamid 2026-09-26: HOLD (G3-B5) / TargetIdentityUnconfirmed / Supersedes2026-09-25Review32Approval. Prior approval: review32 2026-09-25 (Approved as core:enables: confirmation templates and controlled wording are direct prerequisites for confirmation generation). Target: Generate Confirms.. approval judged the relationship plausible; the source row gives no evidence of which target was meant; superseded under the nearness-only identity rule. G1a merged_with_rows blank; no merge and no other approved supporter confirmed before removal. Stored core:enabledBy fact removed (verified unique); no substitute; assertion retained as non-emitting evidence; route for source-workbook target clarification and a fresh verdict."),
    "REL-00304": ("Hamid 2026-09-26: HOLD (G3-B5) / TargetIdentityUnconfirmed / Supersedes2026-09-25Review32Approval. Prior approval: review32 2026-09-25 (Approved as core:enables: vessel/barge actualization produces actualized movement evidence used to identify demurrage/despatch/detention). Target: Identify Potential Demurrage.. approval judged the relationship plausible; the source row gives no evidence of which target was meant; superseded under the nearness-only identity rule. G1a merged_with_rows blank; no merge and no other approved supporter confirmed before removal. Stored core:enabledBy fact removed (verified unique); no substitute; assertion retained as non-emitting evidence; route for source-workbook target clarification and a fresh verdict."),
    "REL-00489": ("Hamid 2026-09-26: HOLD (G3-B5) / TargetIdentityUnconfirmed / Supersedes2026-09-26STApproval. Prior approval: st-enables 2026-09-26 (reviewer-approved predicate change overriding the G1-redundant proposal: exchange utilization operates against the entitlement rules, differentials, contractual imbalance calculations, and governed agreement terms). Target: Manage Refined Product Exchanges.. approval judged the relationship plausible; the source row gives no evidence of which target was meant; superseded under the nearness-only identity rule. Quick-confirmation candidate: the target's own scope description names the source process (REL-00475 communicates utilization requirements to the agreement owner CM-1-2-7-1-1) — placed at the top of the workbook backlog with that evidence attached; if the source author confirms, it returns with a proper identity override and a fresh verdict. Also resolves this row's G1b 'leave unchanged' listing — that decision is now superseded. Stored core:enabledBy fact removed (verified unique); no substitute; assertion retained as non-emitting evidence; route for source-workbook target clarification and a fresh verdict."),
    "REL-00728": ("Hamid 2026-09-26: HOLD (G3-B5) / TargetIdentityUnconfirmed / Supersedes2026-09-25Review32Approval. Prior approval: review32 2026-09-25 (Approved as core:enables: IP framework defines the classification/handling basis under which protection operates) + G2 ExistingRowLevelApproval exception. Target: Protect Intellectual Assets.. approval judged the relationship plausible; the source row gives no evidence of which target was meant; superseded under the nearness-only identity rule. The G2 disguised-sequence exception also goes: the enables fact is absent; the independently recorded precedes/follows facts stay. Stored core:enabledBy fact removed (verified unique); no substitute; assertion retained as non-emitting evidence; route for source-workbook target clarification and a fresh verdict."),
    "REL-01006": ("Hamid 2026-09-26: HOLD (G3-B5) / TargetIdentityUnconfirmed / Supersedes2026-09-25Review32Approval. Prior approval: review32 2026-09-25 (Approved as core:enables: validated self-billing records are necessary inputs to revenue recognition, cutoff, accounting). Target: Perform Revenue Accounting.. approval judged the relationship plausible; the source row gives no evidence of which target was meant; superseded under the nearness-only identity rule. G1a merged_with_rows blank; no merge and no other approved supporter confirmed before removal. Stored core:enabledBy fact removed (verified unique); no substitute; assertion retained as non-emitting evidence; route for source-workbook target clarification and a fresh verdict."),
    "REL-01016": ("Hamid 2026-09-26: HOLD (G3-B5) / TargetIdentityUnconfirmed / Supersedes2026-09-25Review32Approval. Prior approval: review32 2026-09-25 (Approved as core:enables: corrected billing documents are necessary to accurate receivables, cash application, revenue accounting); member of EN_ENABLEDBY_OVERRIDE. Target: Manage Cash Application, A/R & Revenue Accounting.. approval judged the relationship plausible; the source row gives no evidence of which target was meant; superseded under the nearness-only identity rule. Removed from EN_ENABLEDBY_OVERRIDE. Stored core:enabledBy fact removed (verified unique); no substitute; assertion retained as non-emitting evidence; route for source-workbook target clarification and a fresh verdict."),
    "REL-01124": ("Hamid 2026-09-26: HOLD (G3-B5) / TargetIdentityUnconfirmed / Supersedes2026-09-26STApproval. Prior approval: st-enables 2026-09-26 (APPROVE: the validated feedstock-demand signal and coordinated requirements make relevant feedstock-trading action executable within the supply plan); S&T stored control. Target: Trading Management.. approval judged the relationship plausible; the source row gives no evidence of which target was meant; superseded under the nearness-only identity rule. S&T stored control removed. Stored core:enabledBy fact removed (verified unique); no substitute; assertion retained as non-emitting evidence; route for source-workbook target clarification and a fresh verdict."),
    "REL-01174": ("Hamid 2026-09-26: HOLD (G3-B5) / TargetIdentityUnconfirmed / Supersedes2026-09-26STApproval. Prior approval: st-enables 2026-09-26 (APPROVE: quality-screened slates and validated quality information make execution of feedstock trading requirements feasible); S&T stored control. Target: Coordinate Feedstock Trading.. approval judged the relationship plausible; the source row gives no evidence of which target was meant; superseded under the nearness-only identity rule. S&T stored control removed. Stored core:enabledBy fact removed (verified unique); no substitute; assertion retained as non-emitting evidence; route for source-workbook target clarification and a fresh verdict."),

    # Hamid 2026-09-26: G3 Section B5 — 33-row class verdict (D:hamid-verdict).
    # Every row confirmed nearness-only (SoleCandidate) with no source-backed
    # identity override and no prior approval. HOLD / TargetIdentityUnconfirmed
    # / ClassVerdict-B-2026-09-26. Stored core:enabledBy facts removed
    # (each verified unique, single-row); no substitutes; assertions retained
    # as non-emitting evidence; routed for source-workbook target clarification.
    "REL-01049": ("Hamid 2026-09-26: HOLD (G3-B5) / TargetIdentityUnconfirmed / ClassVerdict-B-2026-09-26. Nearness-only candidate (SoleCandidate); no source-backed target identity and no prior approval. Stored core:enabledBy fact removed (verified unique); no substitute; assertion retained as non-emitting evidence; route for source-workbook target clarification and a fresh verdict."),
    "REL-01085": ("Hamid 2026-09-26: HOLD (G3-B5) / TargetIdentityUnconfirmed / ClassVerdict-B-2026-09-26. Nearness-only candidate (SoleCandidate); no source-backed target identity and no prior approval. Stored core:enabledBy fact removed (verified unique); no substitute; assertion retained as non-emitting evidence; route for source-workbook target clarification and a fresh verdict."),
    "REL-01093": ("Hamid 2026-09-26: HOLD (G3-B5) / TargetIdentityUnconfirmed / ClassVerdict-B-2026-09-26. Nearness-only candidate (SoleCandidate); no source-backed target identity and no prior approval. Stored core:enabledBy fact removed (verified unique); no substitute; assertion retained as non-emitting evidence; route for source-workbook target clarification and a fresh verdict."),
    "REL-01095": ("Hamid 2026-09-26: HOLD (G3-B5) / TargetIdentityUnconfirmed / ClassVerdict-B-2026-09-26. Nearness-only candidate (SoleCandidate); no source-backed target identity and no prior approval. Stored core:enabledBy fact removed (verified unique); no substitute; assertion retained as non-emitting evidence; route for source-workbook target clarification and a fresh verdict."),
    "REL-01096": ("Hamid 2026-09-26: HOLD (G3-B5) / TargetIdentityUnconfirmed / ClassVerdict-B-2026-09-26. Nearness-only candidate (SoleCandidate); no source-backed target identity and no prior approval. Stored core:enabledBy fact removed (verified unique); no substitute; assertion retained as non-emitting evidence; route for source-workbook target clarification and a fresh verdict."),
    "REL-01099": ("Hamid 2026-09-26: HOLD (G3-B5) / TargetIdentityUnconfirmed / ClassVerdict-B-2026-09-26. Nearness-only candidate (SoleCandidate); no source-backed target identity and no prior approval. Stored core:enabledBy fact removed (verified unique); no substitute; assertion retained as non-emitting evidence; route for source-workbook target clarification and a fresh verdict."),
    "REL-01104": ("Hamid 2026-09-26: HOLD (G3-B5) / TargetIdentityUnconfirmed / ClassVerdict-B-2026-09-26. Nearness-only candidate (SoleCandidate); no source-backed target identity and no prior approval. Stored core:enabledBy fact removed (verified unique); no substitute; assertion retained as non-emitting evidence; route for source-workbook target clarification and a fresh verdict."),
    "REL-01115": ("Hamid 2026-09-26: HOLD (G3-B5) / TargetIdentityUnconfirmed / ClassVerdict-B-2026-09-26. Nearness-only candidate (SoleCandidate); no source-backed target identity and no prior approval. Stored core:enabledBy fact removed (verified unique); no substitute; assertion retained as non-emitting evidence; route for source-workbook target clarification and a fresh verdict."),
    "REL-01139": ("Hamid 2026-09-26: HOLD (G3-B5) / TargetIdentityUnconfirmed / ClassVerdict-B-2026-09-26. Nearness-only candidate (SoleCandidate); no source-backed target identity and no prior approval. Stored core:enabledBy fact removed (verified unique); no substitute; assertion retained as non-emitting evidence; route for source-workbook target clarification and a fresh verdict."),
    "REL-01142": ("Hamid 2026-09-26: HOLD (G3-B5) / TargetIdentityUnconfirmed / ClassVerdict-B-2026-09-26. Nearness-only candidate (SoleCandidate); no source-backed target identity and no prior approval. Stored core:enabledBy fact removed (verified unique); no substitute; assertion retained as non-emitting evidence; route for source-workbook target clarification and a fresh verdict."),
    "REL-01146": ("Hamid 2026-09-26: HOLD (G3-B5) / TargetIdentityUnconfirmed / ClassVerdict-B-2026-09-26. Nearness-only candidate (SoleCandidate); no source-backed target identity and no prior approval. Stored core:enabledBy fact removed (verified unique); no substitute; assertion retained as non-emitting evidence; route for source-workbook target clarification and a fresh verdict."),
    "REL-01156": ("Hamid 2026-09-26: HOLD (G3-B5) / TargetIdentityUnconfirmed / ClassVerdict-B-2026-09-26. Nearness-only candidate (SoleCandidate); no source-backed target identity and no prior approval. Stored core:enabledBy fact removed (verified unique); no substitute; assertion retained as non-emitting evidence; route for source-workbook target clarification and a fresh verdict."),
    "REL-01161": ("Hamid 2026-09-26: HOLD (G3-B5) / TargetIdentityUnconfirmed / ClassVerdict-B-2026-09-26. Nearness-only candidate (SoleCandidate); no source-backed target identity and no prior approval. Stored core:enabledBy fact removed (verified unique); no substitute; assertion retained as non-emitting evidence; route for source-workbook target clarification and a fresh verdict."),
    "REL-01167": ("Hamid 2026-09-26: HOLD (G3-B5) / TargetIdentityUnconfirmed / ClassVerdict-B-2026-09-26. Nearness-only candidate (SoleCandidate); no source-backed target identity and no prior approval. Stored core:enabledBy fact removed (verified unique); no substitute; assertion retained as non-emitting evidence; route for source-workbook target clarification and a fresh verdict."),
    "REL-01169": ("Hamid 2026-09-26: HOLD (G3-B5) / TargetIdentityUnconfirmed / ClassVerdict-B-2026-09-26. Nearness-only candidate (SoleCandidate); no source-backed target identity and no prior approval. Stored core:enabledBy fact removed (verified unique); no substitute; assertion retained as non-emitting evidence; route for source-workbook target clarification and a fresh verdict."),
    "REL-01176": ("Hamid 2026-09-26: HOLD (G3-B5) / TargetIdentityUnconfirmed / ClassVerdict-B-2026-09-26. Nearness-only candidate (SoleCandidate); no source-backed target identity and no prior approval. Stored core:enabledBy fact removed (verified unique); no substitute; assertion retained as non-emitting evidence; route for source-workbook target clarification and a fresh verdict."),
    "REL-01179": ("Hamid 2026-09-26: HOLD (G3-B5) / TargetIdentityUnconfirmed / ClassVerdict-B-2026-09-26. Nearness-only candidate (SoleCandidate); no source-backed target identity and no prior approval. Stored core:enabledBy fact removed (verified unique); no substitute; assertion retained as non-emitting evidence; route for source-workbook target clarification and a fresh verdict."),
    "REL-01187": ("Hamid 2026-09-26: HOLD (G3-B5) / TargetIdentityUnconfirmed / ClassVerdict-B-2026-09-26. Nearness-only candidate (SoleCandidate); no source-backed target identity and no prior approval. Stored core:enabledBy fact removed (verified unique); no substitute; assertion retained as non-emitting evidence; route for source-workbook target clarification and a fresh verdict."),
    "REL-01195": ("Hamid 2026-09-26: HOLD (G3-B5) / TargetIdentityUnconfirmed / ClassVerdict-B-2026-09-26. Nearness-only candidate (SoleCandidate); no source-backed target identity and no prior approval. Stored core:enabledBy fact removed (verified unique); no substitute; assertion retained as non-emitting evidence; route for source-workbook target clarification and a fresh verdict."),
    "REL-01201": ("Hamid 2026-09-26: HOLD (G3-B5) / TargetIdentityUnconfirmed / ClassVerdict-B-2026-09-26. Nearness-only candidate (SoleCandidate); no source-backed target identity and no prior approval. Stored core:enabledBy fact removed (verified unique); no substitute; assertion retained as non-emitting evidence; route for source-workbook target clarification and a fresh verdict."),
    "REL-01204": ("Hamid 2026-09-26: HOLD (G3-B5) / TargetIdentityUnconfirmed / ClassVerdict-B-2026-09-26. Nearness-only candidate (SoleCandidate); no source-backed target identity and no prior approval. Stored core:enabledBy fact removed (verified unique); no substitute; assertion retained as non-emitting evidence; route for source-workbook target clarification and a fresh verdict."),
    "REL-01209": ("Hamid 2026-09-26: HOLD (G3-B5) / TargetIdentityUnconfirmed / ClassVerdict-B-2026-09-26. Nearness-only candidate (SoleCandidate); no source-backed target identity and no prior approval. Stored core:enabledBy fact removed (verified unique); no substitute; assertion retained as non-emitting evidence; route for source-workbook target clarification and a fresh verdict."),
    "REL-01219": ("Hamid 2026-09-26: HOLD (G3-B5) / TargetIdentityUnconfirmed / ClassVerdict-B-2026-09-26. Nearness-only candidate (SoleCandidate); no source-backed target identity and no prior approval. Stored core:enabledBy fact removed (verified unique); no substitute; assertion retained as non-emitting evidence; route for source-workbook target clarification and a fresh verdict."),
    "REL-01231": ("Hamid 2026-09-26: HOLD (G3-B5) / TargetIdentityUnconfirmed / ClassVerdict-B-2026-09-26. Nearness-only candidate (SoleCandidate); no source-backed target identity and no prior approval. Stored core:enabledBy fact removed (verified unique); no substitute; assertion retained as non-emitting evidence; route for source-workbook target clarification and a fresh verdict."),
    "REL-01237": ("Hamid 2026-09-26: HOLD (G3-B5) / TargetIdentityUnconfirmed / ClassVerdict-B-2026-09-26. Nearness-only candidate (SoleCandidate); no source-backed target identity and no prior approval. Stored core:enabledBy fact removed (verified unique); no substitute; assertion retained as non-emitting evidence; route for source-workbook target clarification and a fresh verdict."),
    "REL-01245": ("Hamid 2026-09-26: HOLD (G3-B5) / TargetIdentityUnconfirmed / ClassVerdict-B-2026-09-26. Nearness-only candidate (SoleCandidate); no source-backed target identity and no prior approval. Stored core:enabledBy fact removed (verified unique); no substitute; assertion retained as non-emitting evidence; route for source-workbook target clarification and a fresh verdict."),
    "REL-01248": ("Hamid 2026-09-26: HOLD (G3-B5) / TargetIdentityUnconfirmed / ClassVerdict-B-2026-09-26. Nearness-only candidate (SoleCandidate); no source-backed target identity and no prior approval. Stored core:enabledBy fact removed (verified unique); no substitute; assertion retained as non-emitting evidence; route for source-workbook target clarification and a fresh verdict."),
    "REL-01250": ("Hamid 2026-09-26: HOLD (G3-B5) / TargetIdentityUnconfirmed / ClassVerdict-B-2026-09-26. Nearness-only candidate (SoleCandidate); no source-backed target identity and no prior approval. Stored core:enabledBy fact removed (verified unique); no substitute; assertion retained as non-emitting evidence; route for source-workbook target clarification and a fresh verdict."),
    "REL-01259": ("Hamid 2026-09-26: HOLD (G3-B5) / TargetIdentityUnconfirmed / ClassVerdict-B-2026-09-26. Nearness-only candidate (SoleCandidate); no source-backed target identity and no prior approval. Stored core:enabledBy fact removed (verified unique); no substitute; assertion retained as non-emitting evidence; route for source-workbook target clarification and a fresh verdict."),
    "REL-01287": ("Hamid 2026-09-26: HOLD (G3-B5) / TargetIdentityUnconfirmed / ClassVerdict-B-2026-09-26. Nearness-only candidate (SoleCandidate); no source-backed target identity and no prior approval. Stored core:enabledBy fact removed (verified unique); no substitute; assertion retained as non-emitting evidence; route for source-workbook target clarification and a fresh verdict."),
    "REL-01288": ("Hamid 2026-09-26: HOLD (G3-B5) / TargetIdentityUnconfirmed / ClassVerdict-B-2026-09-26. Nearness-only candidate (SoleCandidate); no source-backed target identity and no prior approval. Stored core:enabledBy fact removed (verified unique); no substitute; assertion retained as non-emitting evidence; route for source-workbook target clarification and a fresh verdict."),
    "REL-01304": ("Hamid 2026-09-26: HOLD (G3-B5) / TargetIdentityUnconfirmed / ClassVerdict-B-2026-09-26. Nearness-only candidate (SoleCandidate); no source-backed target identity and no prior approval. Stored core:enabledBy fact removed (verified unique); no substitute; assertion retained as non-emitting evidence; route for source-workbook target clarification and a fresh verdict."),
    "REL-01318": ("Hamid 2026-09-26: HOLD (G3-B5) / TargetIdentityUnconfirmed / ClassVerdict-B-2026-09-26. Nearness-only candidate (SoleCandidate); no source-backed target identity and no prior approval. Stored core:enabledBy fact removed (verified unique); no substitute; assertion retained as non-emitting evidence; route for source-workbook target clarification and a fresh verdict."),











}
emitting = []
for r in v2:
    if r["row_id"] in PROPERTY_RULE_HOLDS:
        continue
    cands = r["candidate_slugs"].split(" | ") if r["candidate_slugs"] else []
    if r["disposition"] == "ResolvedToConcept" and len(cands) == 1:
        emitting.append((r, cands[0]))
    elif r["disposition"] == "SoleCandidate" and len(cands) == 1 and ctx.get(r["row_id"]) == "PROMOTE":
        emitting.append((r, cands[0]))
print("emitting mentions:", len(emitting))

# mention graph for enables grouping (single-candidate rows incl. held, for evidence)
graph = defaultdict(set)
for r in v2:
    cands = r["candidate_slugs"].split(" | ") if r["candidate_slugs"] else []
    if len(cands) == 1 and r["disposition"] in ("ResolvedToConcept", "SoleCandidate"):
        graph[(r["source_slug"], cands[0])].add(r["verb"])

def enables_group(r, tgt):
    src = r["source_slug"]
    sibs = imap.get(src, {}).get("parent_slug") == imap.get(tgt, {}).get("parent_slug") \
        and imap.get(src, {}).get("parent_slug")
    seq = bool((graph.get((src, tgt), set()) | graph.get((tgt, src), set())) & {"precedes", "follows"})
    dep = bool(graph.get((tgt, src), set()) & {"uses-input", "informed-by"})
    if sibs and seq: return "G2-disguised-sequence"
    if dep: return "G1-redundant-output-dep"
    return "G3-genuine-enablement"

# REQUIRES_REMAP retired 2026-09-25: Hamid held REL-00208 for workbook
# correction (no remap at emission). Any future treatment needs a fresh verdict.

# Hamid 2026-09-25: row-level verdicts "approved as core:enables" override the
# G1/G2/G3 group proposal for these rows. Stored as (target, core:enabledBy,
# source); core:enables is available as its inverse. If Hamid later revisits
# any of these in the G1-split/G2 review, update this set.
EN_ENABLEDBY_OVERRIDE = {"REL-01303", "REL-01056"}
# 2026-09-26: sweep supersessions (G3-B5). Seven prior approvals on
# nearness-only targets removed from the override set:
# REL-00129, REL-00243, REL-00304, REL-00728, REL-01006, REL-01016
# (review32 2026-09-25 approvals; REL-00129/REL-00728 also G2
# ExistingRowLevelApproval exceptions) — superseded by Hamid's 2026-09-26
# verdicts (D:hamid-verdict / TargetIdentityUnconfirmed /
# Supersedes2026-09-25Review32Approval). Each approval judged the
# relationship plausible; no source row gives evidence of which target was
# meant. Prior decisions retained in provenance as superseded.
# REL-00489 removed separately (Supersedes2026-09-26STApproval).
# 2026-09-26: REL-00939 removed from the override set — superseded by
# Hamid's G3-B4 verdict (D:hamid-verdict / TargetIdentityUnconfirmed /
# Supersedes2026-09-25Approval). Its 2026-09-25 row-level approval
# ("approved financing/payment methods, terms, eligibility, commercial
# rules are governed prerequisites for billing", review32-enables-batch)
# recognized a plausible relationship, but the source row never names
# Manage Customer Invoicing and Billing as its target. Under the
# nearness-only identity rule, a plausible relationship cannot stand in
# for a named target. Prior decision retained in provenance as superseded.
# 2026-09-26: REL-00770 removed from the override set — superseded by
# Hamid's G3-B3 verdict (D:hamid-verdict / TargetIdentityUnconfirmed /
# Supersedes2026-09-25Approval). Its 2026-09-25 row-level approval ("Account
# planning explicitly feeds Sales Execution with account-level objectives,
# opportunity maps, actions, evidence", review32-enables-batch) recognized
# a plausible semantic relationship, but the original source assertion does
# not identify Sales Execution as its target. Under the subsequently
# approved nearness-only identity rule, predicate plausibility cannot
# substitute for source-backed target identity. Prior decision remains in
# provenance as superseded, not deleted.
# 2026-09-26: REL-00428 removed from the override set — superseded by
# Hamid's G3-B2 verdict (D:hamid-verdict / TargetIdentityUnconfirmed). Its
# 2026-09-25 row-level approval rested on semantic plausibility
# (review32-enables-batch), but the nearness-only identity rule (B1,
# Hamid-approved) requires source-backed target identity before any
# predicate verdict; the B2 row-level verdict is later and authoritative.
# REL-00059 and REL-00133 were never row-level approved (corrected G3-B1).

# Hamid 2026-09-26: G2 no-separate-enables-fact verdicts. These 13 enables
# assertions are disguised sequence (same-parent siblings with an
# independently recorded precedes/follows fact); the enables mention emits
# no triple and is recorded as non-emitting evidence. REL-00129 and REL-00728
# keep their row-level core:enabledBy approvals above — group classification
# never overrides a row-level verdict.
G2_NO_SEPARATE_FACT = {"REL-00122", "REL-00135", "REL-00174", "REL-00216",
    "REL-00375", "REL-00698", "REL-00727", "REL-00731", "REL-00955",
    "REL-00983", "REL-00992", "REL-01024", "REL-01090"}

def stored_fact(r, tgt):
    """Proposed canonical (subject, predicate, object). Returns (s, p, o, note)."""
    s, v = r["source_slug"], r["verb"]
    if v == "uses-input":   return (s, "core:dependsOnOutputOf", tgt, "")
    if v == "informed-by":  return (s, "core:informedBy", tgt, "")
    if v == "informs":      return (tgt, "core:informedBy", s, "inverse of raw informs")
    if v == "requires":
        return (s, "core:requires", tgt, "")
    if v == "precedes":     return (s, "core:precedes", tgt, "")
    if v == "follows":      return (tgt, "core:precedes", s, "canonicalized from follows")
    if v == "governed-by":  return (s, "core:governedBy", tgt, "")
    if v == "constrained-by": return (s, "core:constrainedBy", tgt, "")
    if v == "constrains":   return (tgt, "core:constrainedBy", s, "inverse of raw constrains")
    if v == "triggers":     return (tgt, "core:triggeredBy", s, "inverse of raw triggers")
    if v == "assures":      return (tgt, "core:assuredBy", s, "inverse of raw assures")
    if v == "enables":
        if r["row_id"] in EN_ENABLEDBY_OVERRIDE:
            return (tgt, "core:enabledBy", s, "Hamid verdict: approved as core:enables (row-level, overrides group)")
        g = enables_group(r, tgt)
        if g == "G1-redundant-output-dep":
            return (tgt, "core:dependsOnOutputOf", s, "proposed merge into existing output-dependency fact")
        if g == "G2-disguised-sequence":
            return (None, None, None, "Hamid verdict 2026-09-26: no separate triple; sequence fact already recorded")
        return (tgt, "core:enabledBy", s, "inverse of raw enables")
    raise ValueError(v)

facts = defaultdict(list)  # (s,p,o) -> [row_ids]
dropped_enables = []
perverb = Counter()
for r, tgt in emitting:
    s, p, o, note = stored_fact(r, tgt)
    perverb[(r["verb"], p if p else "HELD-no-triple")] += 1
    if p is None:
        dropped_enables.append((r["row_id"], r["source_slug"], tgt, note))
    else:
        facts[(s, p, o)].append((r["row_id"], r["verb"], note))

print("canonical facts:", len(facts))
merges = {k: v for k, v in facts.items() if len(v) > 1}
print("facts with >1 mention (merged):", len(merges))
n_merged_mentions = sum(len(v) for v in merges.values())
print("mentions participating in merges:", n_merged_mentions)

# contradictions: (A,p,B) and (B,p,A) both present
factset = set(facts)
contras = []
seen = set()
for (a, p, b) in factset:
    if (b, p, a) in factset and (b, p, a, ) not in seen and (a, p, b) not in seen:
        # canonical ordering to dedupe
        key = tuple(sorted([(a, p, b), (b, p, a)]))
        if key not in seen:
            seen.add(key)
            contras.append(((a, p, b), (b, p, a)))
print("contradictions:", len(contras))
for (f1, f2) in contras:
    r1 = ";".join(r for r, _, _ in facts[f1]); r2 = ";".join(r for r, _, _ in facts[f2])
    print(f"  {f1[0]} {f1[1]} {f1[2]} [{r1}]  VS  {f2[0]} {f2[1]} {f2[2]} [{r2}]")

print("\nper-verb proposed predicate:")
for (v, p), n in sorted(perverb.items()):
    print(f"  {v:15s} -> {p:28s} {n}")

# Hamid 2026-09-26 (G1a verdict): duplicate-provenance attach. These rows are
# held (no independent emission) but their raw enables assertions are retained
# as duplicate provenance on independently-evidenced canonical facts. Each fact
# survives through its approved uses-input row; the enables rows add provenance
# only — no new fact, no predicate change, no direction change.
DUPLICATE_PROVENANCE_ATTACH = {
    "REL-00152": ("CM-1-2-1-4", "core:dependsOnOutputOf", "CM-1-2-1-1-4"),
    "REL-00436": ("CM-1-2-5-2-3", "core:dependsOnOutputOf", "CM-1-2-5-1-4"),
}
for _rid, _key in DUPLICATE_PROVENANCE_ATTACH.items():
    assert _key in facts, f"independent fact missing for {_rid}"
    assert _rid not in [r for r, _, _ in facts[_key]], f"{_rid} already attached"
    facts[_key].append((_rid, "enables",
        "Hamid 2026-09-26: G1a duplicate-provenance attach; fact independently evidenced via uses-input"))

# save (proposal only — governed CSVs at BASE are the source of truth)
with open(f"{OUT}/canonical-facts.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["subject", "predicate", "object", "mention_count", "row_ids", "raw_verbs", "notes"])
    for (s, p, o), ms in sorted(facts.items()):
        w.writerow([s, p, o, len(ms), ";".join(r for r, _, _ in ms),
                    ";".join(sorted(set(v for _, v, _ in ms))),
                    ";".join(sorted(set(n for _, _, n in ms if n)))])
with open(f"{OUT}/contradictions.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["fact_a", "fact_b", "rows_a", "rows_b"])
    for f1, f2 in contras:
        w.writerow([" ".join(f1), " ".join(f2),
                    ";".join(r for r, _, _ in facts[f1]),
                    ";".join(r for r, _, _ in facts[f2])])
print("\nwrote proposal/canonical-facts.csv, proposal/contradictions.csv")

# ---- enables review table: built from the pipeline's own enables_group ----
# Single source of truth: group comes from enables_group(); context from the
# corrected context pass; proposed follows (group x emitting). Never hand-edit.
ctxrows = {r["row_id"]: r for r in csv.DictReader(open(f"{BASE}/target-report/context-pass.csv"))}
EN_GROUP_LABEL = {"G1-redundant-output-dep": "G1-redundant-output-dep",
                  "G2-disguised-sequence": "G2-disguised-sequence",
                  "G3-genuine-enablement": "G3-genuine-enablement"}
emitting_ids = {r["row_id"] for r, _ in emitting}
en_rows = []
for r in v2:
    if r["verb"] != "enables":
        continue
    cands = r["candidate_slugs"].split(" | ") if r["candidate_slugs"] else []
    tgt = cands[0] if len(cands) == 1 else ""
    tgt_label = r["candidate_labels"].split(" | ")[0] if len(cands) == 1 and r["candidate_labels"] else ""
    c = ctxrows.get(r["row_id"])
    context = f"{c['outcome']}/{c['primary_test']}".strip("/") if c else ""
    emits = r["row_id"] in emitting_ids
    if len(cands) == 1:
        g = enables_group(r, tgt)
        if not emits:
            proposed = "no triple; held pending domain-batch review"
        elif g == "G1-redundant-output-dep":
            proposed = "proposed: merge into the existing core:dependsOnOutputOf fact"
        elif g == "G2-disguised-sequence":
            proposed = "proposed: no separate triple; sequence fact already recorded"
        else:
            proposed = "proposed: emit (target core:enabledBy source)"
    else:
        g, proposed = "HELD-ambiguous", "no triple; held for disambiguation"
    en_rows.append({"row_id": r["row_id"], "baseline_sha": SHA, "source": r["source_slug"],
                    "source_label": r["source_label"], "target": tgt,
                    "target_label": tgt_label, "disposition": r["disposition"],
                    "context": context, "group": EN_GROUP_LABEL.get(g, g),
                    "proposed": proposed, "decision": "", "reviewer_rationale": ""})
with open(f"{OUT}/enables-review.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["row_id", "baseline_sha", "source", "source_label",
                                      "target", "target_label", "disposition", "context",
                                      "group", "proposed", "decision", "reviewer_rationale"])
    w.writeheader()
    w.writerows(en_rows)
print(f"wrote proposal/enables-review.csv ({len(en_rows)} rows, from pipeline enables_group)")
