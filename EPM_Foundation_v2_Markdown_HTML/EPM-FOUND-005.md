# Enterprise Measurement and KPI Model
**Artifact ID:** EPM-FOUND-005  
**Version:** 2.0 Draft  
**Status:** Working baseline  
**Last updated:** August 4, 2026  

*Classification, governance, promotion, and Tableau extraction rules*

**Foundation navigation:** [EPM-FOUND-000](EPM-FOUND-000.md) | [EPM-FOUND-001](EPM-FOUND-001.md) | [EPM-FOUND-002](EPM-FOUND-002.md) | [EPM-FOUND-003](EPM-FOUND-003.md) | [EPM-FOUND-004](EPM-FOUND-004.md) | [EPM-FOUND-005](EPM-FOUND-005.md) | [EPM-FOUND-006](EPM-FOUND-006.md)

## Purpose
This artifact creates a precise measurement taxonomy so that extracted report calculations can be classified consistently and only a small, governed subset becomes enterprise KPIs.

## Core distinctions
### Measurement

An observed or calculated value describing a business object, event, condition, or result.

Examples:

- 120,000 gallons shipped
- $18,000 transportation cost
- 42 late deliveries
- 98,000 barrels inventory
- six hours of unit downtime

A measurement normally has a value, unit, time, and dimensional context.

### Metric

A measurement or calculation with a repeatable business definition used to describe, compare, monitor, or diagnose performance.

Examples:

- Transportation Cost per Gallon
- Inventory Days of Supply
- Average Delivery Cycle Time
- Forecast Error
- Refinery Utilization

### KPI

A governed metric selected to evaluate progress toward an objective or critical outcome and to trigger accountability or action.

Examples:

- Gasoline Netback CPG
- OTIF Delivery
- Three-Month-Out Forecast Accuracy
- Unplanned Refinery Downtime

## Taxonomy
| Class | Purpose | Example |
|---|---|---|
| Raw Measurement | Directly observed from an event or system | Gallons delivered |
| Derived Measurement | Calculated from other measurements | Delivery delay minutes |
| Operational Metric | Monitors routine operation | Terminal throughput |
| Diagnostic Metric | Explains why performance changed | Freight cost variance |
| Performance Indicator | Important monitored measure, not yet enterprise-governed | Pricing publication timeliness |
| Candidate KPI | Proposed measure undergoing governance review | Forecast Hit Rate |
| Approved Enterprise KPI | Governed indicator with objective, owner, target, and response | Gasoline Netback CPG |
| External Benchmark | Market or reference input | OPIS rack benchmark |
| Technical Calculation | Data-processing helper | Null-handling flag |
| Presentation Calculation | Visual-only helper | Dynamic chart label |
| Duplicate | Equivalent to an existing governed item | Alternate Netback calculation |
| Obsolete or Retired | No longer valid or used | Legacy Tableau-only calculation |

## Promotion test
A candidate normally becomes an approved KPI only when most or all of the following are true:

1. It measures progress toward a defined objective or critical outcome.
2. It has an accountable business owner.
3. It has an agreed business definition.
4. It has an approved calculation and dimensional behavior.
5. It has a target, expected range, or explicit evaluation rule.
6. It has warning and critical thresholds where appropriate.
7. It is reviewed through an established management cadence.
8. A material change causes a decision, intervention, or escalation.
9. It is sufficiently important or reusable to govern centrally.
10. Required data can be supplied with acceptable quality and timeliness.

Failure to qualify as a KPI does not imply low value. The item may remain an important governed metric.

## Worked example: delivery performance
### Measurements

- Planned delivery timestamp
- Actual delivery timestamp
- Ordered gallons
- Delivered gallons
- Freight cost
- Delivery status

### Derived measurements

- Delivery delay minutes
- On-time flag
- In-full flag
- Cost per delivery

### Metrics

- On-time delivery rate
- In-full delivery rate
- Average delay duration
- Freight cost per gallon
- Failed delivery count

### KPI

**OTIF Delivery Performance**, when it is formally used to evaluate the objective of reliably fulfilling customer commitments and has an owner, target, threshold, cadence, and corrective response.

## Worked example: forecasting
### Measurements

- Forecast quantity
- Actual quantity

### Derived measurements

- Forecast error
- Absolute error
- Percentage error

### Metrics

- MAPE
- WAPE
- Forecast bias
- Accuracy by product
- Accuracy by region
- Forecast hit rate

### Potential KPIs

- Three-Month-Out Forecast Accuracy
- Forecast Bias

These become KPIs only through governance and management use—not because they are mathematically sophisticated.

## Tableau XML classification pipeline
```text
Legacy Tableau calculation
        ↓
Technical extraction and parsing
        ↓
Normalization and dependency analysis
        ↓
Duplicate and near-duplicate detection
        ↓
Mapping to current Power BI implementation
        ↓
Business-context assignment
        ↓
Measurement classification
        ↓
Candidate KPI assessment
        ↓
Owner and steward review
        ↓
Approved metric, approved KPI, local measure,
technical calculation, duplicate, or retired item
        ↓
Implementation in data product, KPI Store,
semantic view, Power BI model, or report
```

## Required inventory fields
Each extracted item should capture:

- workbook, dashboard, worksheet, and field name;
- original formula and normalized formula;
- dependencies, parameters, filters, and usage count;
- source fields and systems;
- grain, unit, dimensions, and time behavior;
- domain, value stream, stage, capability, process, activity, and decision;
- candidate classification;
- duplicate group;
- current Power BI equivalent;
- supporting data product;
- candidate KPI relationship;
- business owner and steward;
- validation status and disposition.

## KPI Store boundary
The KPI Store receives only approved KPI values and governance metadata.

The Measurement Catalog receives normalized reusable measurements and metrics.

The semantic layer exposes approved consumer contracts.

Power BI reports should not recreate governed KPI logic locally.

---
Part of the Enterprise Performance Model Foundation Version 2.