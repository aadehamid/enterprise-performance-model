# Enterprise Business Architecture
**Artifact ID:** EPM-FOUND-001  
**Version:** 2.0 Draft  
**Status:** Working baseline  
**Last updated:** August 4, 2026  

*Domains, value streams, capabilities, processes, activities, and decisions*

**Foundation navigation:** [EPM-FOUND-000](EPM-FOUND-000.md) | [EPM-FOUND-001](EPM-FOUND-001.md) | [EPM-FOUND-002](EPM-FOUND-002.md) | [EPM-FOUND-003](EPM-FOUND-003.md) | [EPM-FOUND-004](EPM-FOUND-004.md) | [EPM-FOUND-005](EPM-FOUND-005.md) | [EPM-FOUND-006](EPM-FOUND-006.md)

## Purpose
This artifact defines the business context required to interpret downstream measurements and KPIs. It deliberately separates **value flow** from **organizational ability**.

A value stream is not a sequence of capabilities. A value stream consists of outcome-oriented stages. Each stage uses one or more capabilities, and each capability can support multiple stages.

## Core concepts
### Enterprise

The whole organization and its strategic direction.

### Business domain

A major area of business responsibility, expertise, language, data, and decision-making.

Illustrative downstream domains:

- Commercial
- Refining
- Midstream
- Retail
- Corporate
- Health, Safety, Security, and Environment
- Digital and Technology

A domain is not necessarily identical to an organizational department. It is a durable partition of business meaning and accountability.

### Value stream

An end-to-end flow that begins with a trigger or need and ends with value delivered to a stakeholder.

A value stream asks:

> How does value move from an initial opportunity or need to a realized outcome?

Illustrative Commercial value stream:

```text
Sense Market and Customer Demand
        ↓
Form Commercial Plan
        ↓
Secure Supply and Market Position
        ↓
Fulfill Product Commitment
        ↓
Invoice and Settle
        ↓
Evaluate and Optimize Performance
```

### Value-stream stage

A major outcome-oriented step within a value stream. Stages should be phrased as value-creating outcomes, not merely department or capability names.

### Capability

An enduring ability the enterprise must possess.

A capability asks:

> What must the organization be able to do?

Examples:

- Market Intelligence
- Demand Forecasting
- Physical Trading
- Pricing Management
- Transportation Management
- Inventory Management
- Commercial Risk Management
- Refinery Reliability Management

Capabilities are relatively stable even when organizations, systems, or processes change.

### Sub-capability

A capability decomposed beneath a broader capability. Capability and sub-capability are the same type of concept at different levels of abstraction.

Example:

```text
Commercial Risk Management
├── Market Risk Management
├── Credit Risk Management
├── Liquidity Risk Management
├── Position and Exposure Management
├── Risk Limit Management
├── Valuation Management
└── P&L Attribution
```

### Business process

An ordered flow of work with a trigger, inputs, activities, outputs, owner, and end condition.

A process asks:

> How is the capability performed in a defined context?

Example:

```text
Calculate and Publish Rack Prices
1. Acquire market prices
2. Validate market inputs
3. Calculate proposed prices
4. Apply governed adjustments
5. Approve prices
6. Publish prices
7. Confirm distribution
8. Resolve exceptions
```

### Business activity

A discrete unit of work performed by a person, team, system, or combination of them.

Examples:

- Validate OPIS price timestamp
- Submit pipeline nomination
- Assign carrier
- Approve rack-price override
- Reconcile freight invoice

### Business decision

A choice among alternatives that changes business action, resource allocation, exposure, or outcome.

Examples:

- Increase diesel yield
- Export product rather than retain it domestically
- Change supply source
- Reroute a shipment
- Reprice a rack market
- Hedge a regional basis exposure

## Capability versus process
| Test | Capability | Process |
|---|---|---|
| Core question | What must we be able to do? | How do we do it? |
| Typical wording | Noun or noun phrase | Verb-led flow |
| Stability | Relatively stable | Changes with policy, technology, and operating design |
| Sequence | No inherent sequence | Has a beginning, flow, and end |
| Example | Transportation Management | Plan and Execute Product Movement |
| Technology relationship | Enabled by systems | Executed through steps using systems |

A practical stopping rule for capability decomposition: stop when the capability is distinct, meaningful to an owner, measurable, supported by identifiable processes and technology, and still larger than an individual task.

## Value stream versus capability
```text
Value Stream
    ↓ contains
Value-Stream Stages
    ↕ use
Capabilities
    ↓ realized through
Processes
    ↓ contain
Activities
    ↓ support
Decisions
```

This is a many-to-many model:

- One value-stream stage uses many capabilities.
- One capability supports many value streams or stages.
- Capabilities should not be arranged as though they were process steps.

## Commercial example
| Business architecture element | Example |
|---|---|
| Domain | Commercial |
| Value stream | Convert Market Opportunity into Realized Commercial Value |
| Stage | Fulfill Product Commitment |
| Capabilities used | Supply Scheduling, Transportation Management, Inventory Management, Terminal Operations |
| Process | Plan and Execute Product Movement |
| Activities | Submit nomination, assign carrier, create loading order, track movement, confirm delivery |
| Decisions | Reroute product, expedite delivery, substitute supply location, prioritize customer |
| Potential KPIs | OTIF, Supply Reliability, Logistics Cost per Gallon, Demurrage Cost |
| Supporting metrics | Transit time, late-load count, freight cost, terminal inventory, capacity utilization |

## Relationship rules
| Relationship | Meaning |
|---|---|
| domain contains capability | A capability is primarily governed within a domain |
| value stream contains stage | A stage contributes to the end-to-end flow of value |
| stage uses capability | A stage depends on an enduring organizational ability |
| capability decomposes into sub-capability | A broader ability is divided into coherent component abilities |
| capability is realized through process | The ability is operationalized through repeatable work |
| process contains activity | The process is executed through discrete work steps |
| activity supports decision | The activity provides information or action needed for a choice |
| decision affects outcome | The choice influences operational, financial, customer, risk, or strategic results |

## Modeling guidance
- Do not use the same label at multiple levels without qualification.
- Prefer outcome language for value-stream stages.
- Prefer noun phrases for capabilities.
- Prefer verb-led names for processes and activities.
- Do not treat organization units as capabilities unless the name genuinely describes an enduring ability.
- Do not treat applications as capabilities.
- A KPI may measure a value stream, stage, capability, process, or outcome; it is not a structural child of the activity hierarchy.

---
Part of the Enterprise Performance Model Foundation Version 2.