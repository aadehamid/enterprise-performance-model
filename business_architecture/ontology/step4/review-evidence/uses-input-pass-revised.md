# Revised `uses-input` pass — 2026-09-26 (third revision, corrected)

Responds to Hamid's feedback. **Nothing applied** — approval requested.
Replaces the second revision (which had a corrupted hold list and no
affirmative/exclusion split).

## Population (verified)

152 emitting `uses-input` rows: 149 ordinary + 3 contradiction retentions
(REL-00862, REL-01029, REL-01061). Every row below was verified
verb=`uses-input` (identity-scope-rule5-flags.csv) and currently
supporting a fact in canonical-facts.csv (emitting).

## Citation classification (Hamid's affirmative condition)

Strict slug test found 64 rows with the target cited in the source's
scope note. Each of the 125 citation contexts was read and classified:

- **AFFIRMATIVE (33)** — the scope note describes the source consuming,
  receiving, taking, deriving from, or assembling from the target's
  output; or names the target as the counterpart whose
  outputs/contracts/decisions the source orchestrates, operates under,
  or coordinates through.
- **EXCLUSION (31)** — the slug appears only in "Excludes…"/"Out of
  scope…" lists, pure ownership statements ("owned by", "are owned by"
  — REL-00009 precedent), or boundary delineations. These do not
  qualify and move to the hold list.

**33 affirmative (promote):** REL-00030, REL-00145, REL-00269,
REL-00270, REL-00278, REL-00279, REL-00369, REL-00370, REL-00380,
REL-00404, REL-00410, REL-00442, REL-00443, REL-00446, REL-00450,
REL-00470, REL-00474, REL-00483, REL-00487, REL-00549, REL-00563,
REL-00621, REL-00650, REL-00662, REL-00696, REL-00697, REL-00759,
REL-00824, REL-00836, REL-01127, REL-01136, REL-01276, REL-01292.

**31 exclusion (hold):** REL-00012, REL-00048, REL-00064, REL-00101,
REL-00117, REL-00181, REL-00225, REL-00242, REL-00261, REL-00293,
REL-00361, REL-00373, REL-00378, REL-00390, REL-00849, REL-00935,
REL-00941, REL-00972, REL-01007, REL-01044, REL-01062, REL-01076,
REL-01114, REL-01162, REL-01164, REL-01165, REL-01180, REL-01220,
REL-01246, REL-01264, REL-01278.

Per-context classifications are recorded in
`review-evidence/uses-input-citation-classification.csv`.

## Other routes

- **REL-00256** promotes via PR #119 ("Establish & Maintain Delegation
  Of Authority (DOA)" → CM-1-2-2-3-2) + sibling nearness. PR #110 gives
  no route (0 of the 85 match CM-1-1-4/CM-1-1-7). No other decision-log
  identity resolutions exist.
- **REL-00862, REL-01029** retained via **scope-note label citation,
  unique label** (recorded as a separate route from slug citations):
  00862's scope note names "Maintain Price & Discount Master Data";
  01029's names "Manage Credit Card Transactions". Each label is unique.
- **REL-01061** held. Scope note cites CM-1-3-8-1-3 (a different
  concept sharing the "Determine Taxability" label), not the row's
  target CM-1-3-8-4-5. Backlog: CM-1-3-8-1-3 recorded as the probable
  intended target for the source author to confirm; no retargeting at
  emission. Pair C fully held (REL-01065 was already held).

## Knock-on k (revised)

The affirmative condition moves 10 G1a supporters from promote to hold
(vs the second revision). **k = 43** (was 33). All 43 attached `enables`
mentions currently emit and have no other fact. G1a emitting: 75 → **32**.

## Proposed disposition

| Group | Rows |
|---|---|
| 33 affirmative slug citations | promote |
| REL-00256 (PR #119 + sibling) | promote |
| REL-00862, REL-01029 (label citation) | retain |
| 84 no-citation, no-decision-evidence | HOLD |
| 31 exclusion-citation | HOLD |
| REL-01061 | HOLD |

Facts removed: **116** (73 sole-evidence + 43 G1a-shared).
`enables` mentions emitting → held: **k = 43**.

## Proposed totals (re-derived)

| | Emitting | Held | Facts |
|---|---|---|---|
| Current | 917 | 386 | 716 |
| After pass | **758** | **545** | **600** |
| Delta | −159 (116 rows + 43 mentions) | +159 | −116 |

Conservation: 758 + 545 = 1303 = 917 + 386. ✓
G1a emitting: 75 → 32. The 26 stable-ID G1a supporters stand.

## Rule 6 samples (per domain, fixed seed 42)

34 automatic promotions (33 citation + REL-00256), split by source domain:

- **CM-1-1:** 1 promotion → sample 1: REL-00030. ✓
- **CM-1-2:** 22 promotions → sample 10: REL-00145, REL-00269,
  REL-00270, REL-00278, REL-00369, REL-00370, REL-00380, REL-00404,
  REL-01127, REL-01292. ✓
- **CM-1-3:** 11 promotions → sample 10: REL-00549, REL-00563,
  REL-00621, REL-00650, REL-00662, REL-00697, REL-00759, REL-00824,
  REL-00836, REL-01276. ✓

All 21 sampled rows verified: affirmative citation present, target
identity matches the row's resolved slug. (REL-00256's PR #119 route
verified separately.)

## REL-00873 re-check

- Strict **slug** test: target CM-1-3-7-4-2 NOT cited in definition or
  scope note. FAIL.
- **Label** test: scope note names "Establish Credit Limit & Risk Code"
  — the exact unique prefLabel of CM-1-3-7-4-2 — affirmatively ("it
  requests governed record creation and consumes the outcomes"). PASS
  under the approved "scope-note label citation, unique label" route.
- **Recommendation:** reverse the supersession and restore the fact,
  per the conditional order. **Awaiting Hamid's confirmation before
  executing** (reversing an ordered supersession).

## Repin

PINNED_SHA.txt now `a73d313ba922e323ccfeaad667efef42c194e4b8`. The
step3-taxonomy.ttl blob is byte-identical at 6ab2197 and a73d313 (git
blob `093294cb1946fc5366320163d04f69e12f6949c4`, verified against the
local file), so the citation test stands as run.

## 116-row hold list

84 no-citation: REL-00047, REL-00066, REL-00150, REL-00151, REL-00153,
REL-00213, REL-00214, REL-00222, REL-00229, REL-00231, REL-00234,
REL-00237, REL-00238, REL-00258, REL-00264, REL-00287, REL-00288,
REL-00290, REL-00377, REL-00381, REL-00384, REL-00415, REL-00429,
REL-00447, REL-00457, REL-00465, REL-00468, REL-00481, REL-00564,
REL-00864, REL-00866, REL-00868, REL-00870, REL-00878, REL-00879,
REL-00887, REL-00916, REL-00931, REL-00934, REL-00943, REL-00946,
REL-00954, REL-00959, REL-00964, REL-00976, REL-00998, REL-01001,
REL-01002, REL-01004, REL-01010, REL-01015, REL-01022, REL-01027,
REL-01030, REL-01036, REL-01040, REL-01050, REL-01057, REL-01058,
REL-01069, REL-01071, REL-01077, REL-01083, REL-01125, REL-01135,
REL-01160, REL-01218, REL-01221, REL-01238, REL-01239, REL-01251,
REL-01252, REL-01261, REL-01279, REL-01293, REL-01308, REL-01314.
31 exclusion: listed above. Plus REL-01061.

## Notes

- The second revision's 84-row list and 799/504/631 totals are
  superseded by this revision. The 64-row citation list from the second
  revision stands; only the affirmative/exclusion split is new.
- Nothing has been applied. Awaiting approval of the numbers and the
  REL-00873 reversal decision.
