# 3-2-1 Crack Spread KPI Definition (MPC Economics, internal)

**Status:** Evidence, tier 1 · **Provided by:** the decision owner, 2026-10-20 (`answers-2026-10-20-crack-spread-source.md`) · **Used for:** the `market-data` module (EPM-DEC-001-0066)

The decision owner supplied this definition and set it as the primary source for the crack spread, ahead of MPC's public filings, peers and other references. The text below is the definition as supplied, with three parts left out by the decision owner's choice ("Definition + series IDs"): the governance section (owners and validators), the SharePoint link in §4.2, and the implementation detail of §5 (table and view names, SQL, and the Synapse and Databricks paths). Each omission is marked `[omitted: …]`. The averaging and substitution rules of §5 are kept, because they say what the published number means.

---

## 1. Purpose

Establish a single definition for the 3-2-1 Crack Spread, eliminate reporting drift, and give implementers a clear guide. What the number means, which published MPR IDs to select, how to extract them, and who validates the result.

## 2. Functional definition

The 3-2-1 Crack Spread is an industry-standard metric used to estimate the **gross refining margin**. It simulates refining three barrels of crude into two barrels of gasoline and one barrel of distillate (diesel).

| | |
|---|---|
| **Ratio** | 3 : 2 : 1 (crude : gasoline : diesel) |
| **Unit** | Dollars per barrel ($/bbl) |
| **What it represents** | Value added by refining, finished-product market value minus crude cost |

The 3-2-1 ratio is the common U.S. market convention. U.S. refineries typically yield roughly twice as much gasoline as distillate. Other published ratios (1:1, 2:1:1, 5:3:2) exist in the market. They are not this KPI.

The metric view contains **127+ crack spread series** across multiple regions and types. The six primary regional 3-2-1 KPI series cover **USGC, Chicago, Group 3 (Tulsa), LA, PNW, and SLC**. Additional series include NYMEX cracks, MPC Blended cracks, 6-3-2-1 cracks, individual leg cracks, and regional variants (NYH, El Paso, San Francisco, USWC, etc.). The focus is the broader market, not a refinery-specific crack.

It is a **market-marker** estimate. It is not:

- Realized gross refining margin (actual yields, actual barrels)
- Net margin after operating cost, other than the optional RVO treatment below
- Capture rate, R&M margin in $MM, or PIMS COP / BEV / Incentive

There is also a NYMEX 3-2-1 industry benchmark (WTI / RBOB / Heating Oil) and an MPC-weighted roll-up of three regional 3-2-1s. Published results for both are available in the metric view as named series (see §4).

## 3. Calculation

These treatments are Economics context. The catalog and Gold hold many published MPR/MIPS crack series (127+ in the metric view).

Markers used for history and forecast are aligned with IR, Finance, and Clean Products. Product prices in MPR (Price Master) are in **$/gallon**. Crude is in **$/barrel**. The formulas below assume those units. They state what the published number represents.

Two treatments of RVO (Renewable Volume Obligation) are defined. **With RVO in the result (Inc-RVO)** is closer to a gross margin. **Without RVO (Ex-RVO)** is closer to a net margin. Both may be produced. **Ex-RVO is the one Economics focuses on.**

> **Terminology note:** The business term is "Ex-RVO" (excluding the Renewable Volume Obligation) and "Inc-RVO" (including). In the actual data, the equivalent label is "ex-RIN" (excluding Renewable Identification Numbers). "Ex-RVO" and "ex-RIN" mean the same thing. The metric view's `Price_Master_Name` and `MIPS_Groups_Text` columns use "ex-RIN".

### 3.1 Conversions

| | |
|---|---|
| Gallons to barrels | × 42 |
| Normalize to per-barrel of crude | ÷ 3 |

### 3.2 Core formulas

**A. 3-2-1 Ex-RVO (excluding RVO), closer to net margin**

```text
3-2-1 Ex-RVO, $/bbl
  = ((CBOB × 42 × 2) + (ULSD × 42 × 1)) / 3 − Crude − (RVO × 42)

Equivalent form (same result):

((2 × CBOB − 2 × RVO + ULSD − RVO) × 42 / 3) − Crude
```

**B. 3-2-1 Inc-RVO (including RVO), closer to gross margin**

```text
3-2-1 Inc-RVO, $/bbl
  = ((CBOB × 42 × 2) + (ULSD × 42 × 1)) / 3 − Crude
```

The same pair of formulas applies in every region. Only the MPR IDs change.

Compute **daily**, then average the dailies in a month for the monthly series. Do not invent a second monthly formula from monthly-average legs.

## 4. Regional and other MPR IDs

### 4.1 Six primary published crack series

These are the six primary regional 3-2-1 KPI series in the metric view, verified against the actual data:

| Price Master ID | Name | Region | MIPS Group |
|---|---|---|---|
| 43870 | USGC 3-2-1 MEH Crack, ex-RIN | USGC | USGC 3-2-1 MEH Crack, ex-RIN |
| 37438 | CHI 3-2-1 Crack WTI, ex-RIN | Chicago | CHI 3-2-1 WTI Crack, ex-RIN |
| 37439 | Group 3-2-1 Crack WTI, ex-RIN | Group (Tulsa) | Group 3-2-1 WTI Crack, ex-RIN |
| 36855 | LA 3-2-1 Crack ANS, ex-RIN | LA | LA 3-2-1 ANS Crack, ex-RIN |
| 37443 | PNW 3-2-1 Crack, ex-RIN | PNW | PNW 3-2-1 ANS Crack, ex-RIN |
| 37471 | SLC 3-2-1 Crack WTI, ex-RIN | SLC | SLC 3-2-1 WTI Crack, ex-RIN |

### 4.2 Regional input leg IDs (Economics reference)

Formula structure is the same everywhere. These input Price Master IDs explain how the published crack values are calculated. They are not the published crack series themselves.

> **Note:** The six input-leg regions below (Chicago, Gulf Coast, Group 3, LA, NYH, El Paso) are not identical to the six primary published-series regions in §4.1 (USGC, Chicago, Group/Tulsa, LA, PNW, SLC). NYH and El Paso have input-leg definitions but are not among the six primary published series. PNW and SLC are primary published series but their input-leg IDs are not listed here. This reflects how Economics defines input formulas for a broader set of regions than the six selected for the primary KPI extract.

| Region | CBOB (gas) | ULSD (diesel) | Crude | RVO |
|---|---|---|---|---|
| Chicago | 16475 | 16477 | 747 | 13056 |
| Gulf Coast | 11926 | 12838 | 14133 | 13056 |
| Group 3 | 13076 | 9408 | 747 | 13056 |
| LA | 9660 | 9657 | 4055 | 13056 |
| NYH | 10808 | 9448 | 572 | 13056 |
| El Paso | 16791 | 16794 | 14133 | 13056 |

RVO is ID 13056 in every region. Crude 747 is shared by Chicago and Group 3. Crude 14133 is shared by Gulf Coast and El Paso.

Economics maintains MPR parameters for these IDs, and the MPR IDs used in STPO / ELTO forecasts. [omitted: the SharePoint link]

### 4.3 Industry benchmark: NYMEX 3-2-1

| Leg | Marker |
|---|---|
| Crude | NYMEX WTI |
| Gasoline | NYMEX RBOB |
| Diesel | NYMEX Heating Oil |

Available in the metric view as Price Master IDs 39998 (NYMEX 3-2-1 Crack), 44934 (NYMEX ULSD Crack), and 44935 (NYMEX Gas Crack).

### 4.4 MPC-weighted 3-2-1

Approximates a realized MPC 3-2-1 from three regional 3-2-1s only: USGC, Chicago, and LA.

```text
Before 5 May 2024:  (USGC × 0.40) + (Chicago × 0.40) + (LA × 0.20)
After  5 May 2024:  (USGC × 0.42) + (Chicago × 0.40) + (LA × 0.18)
```

Available in the metric view as Price Master IDs 37464 (Blended 3-2-1 Crack, ex-RIN) and 42023 (MPC Internal Blended 3-2-1 Crack, ex-RIN).

## 5. Implementation (rules only)

[omitted: data sourcing detail, table and view names, SQL, and the compile path]

### 5.3 Aggregation

The published daily settle is the number. Monthly is the arithmetic mean of those daily published values. [omitted: the metric view measure and column names]

### 5.4 Variance management

The six primary KPI series (§4.1) are the core extract. The metric view also contains 127+ additional series (see §4). Do not substitute the Economics input IDs (§4.2) in place of the published crack series in a report. The input IDs explain what the published values mean. They are not the compile filter.

## 6. Governance

[omitted by the decision owner's instruction: "Dont add the governance portion of the text"]
