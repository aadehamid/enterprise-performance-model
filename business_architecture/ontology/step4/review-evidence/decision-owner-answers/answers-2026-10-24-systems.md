<!-- The decision owner's words on the systems of item G, verbatim from the Claude Code session of 2026-10-24, as the store-tests handoff recorded them. Context (Claude's words, kept in this comment so they do not enter the quote corpus). The body has 8 blocks, separated by blank lines.
Block 1: Claude listed the systems the process map names and noted that none has a definition; the decision owner asked to add item G to the plan.
Block 2: the decision owner identified APS.
Block 3: the decision owner answered which product, or MPC-built system, CargoTracker, MAGIC, Allocation Manager, Quorum, DPO and OneSource are.
Block 4: the decision owner changed the answer for DPO.
Block 5: Claude drafted descriptions of CargoTracker, MAGIC and Allocation Manager from the repository; the decision owner approved them. The three drafts, as recorded in the store-tests handoff (system-identification-2026-10-24.md): CargoTracker, "an MPC-built application that supplies actual data, including actual product prices, used as inputs to the regional backcast."; MAGIC, "Marketing Applications Graphical Interface for Clients: an MPC-built integration that sets up new customer accounts. When SAP MDG creates a customer, MAGIC assigns the SAP MDG customer number and the KittyHawk territory manager to the account in Salesforce, and converts the prospect into a customer account. Every day it syncs the customer's number, name, address, FEIN, status, credit monitor and territory manager to Salesforce."; Allocation Manager, "an MPC-built application that derives operational decisions for a customer, such as locks and limits, from the customer data RightAngle sends it."
Block 6: Claude drafted a description of DPO from the process map and EPM-DEC-001-0040; the decision owner approved it. The draft, as recorded in the same handoff note: "an MPC-built optimization model and application that produces the distribution plan for the prompt month to M+3, across pipelines, marine and inventory. Planners build a base distribution plan in it, reconcile it with the XPIMS refinery plan, update its network constraints, and hand over the final distribution plan. It is also used in the distribution backcast, to evaluate actuals cases and optimization cases."
Block 7: the decision owner said that their "assume" answers in block 3 are answers.
Block 8: the decision owner described KittyHawk.
Do not edit; scripts/epm_facts.py quotes checks quotes against this file. -->

can we add this to the plan. Most of these systems are off the shlef and public. We can search for the definitions in the public.

APS is https://www.aspentech.com/en/products/msc/aspen-petroleum-scheduler

cargoTracker and MAGIC.. consider them MPC built. Allocation Manager is home grown/mpc built. Let us assume it is the same Quorum as the one that came back from the research. DPO and OneSource .. let assume it is the one from the research I shared.

DPO.. let us change that to MPC built. And give it the name "Distribution Planning Optimizer"

yes, record all three as drafted

yes, record that description for DPO

where I say assumed. Consider those the answer. you can scrape the word "assume"

KittyHawk is an MPC in-house application. It gets all of its data from RightAngle. Almost a replica of RightAngle. Kittyhawk is used by the Commercial orgainization
