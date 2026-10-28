<!-- The decision owner's words, verbatim from the Claude Code session of 2026-10-28. Context (Claude's words, kept in this comment so they do not enter the quote corpus). The body has 5 blocks.
Block 1: while Claude prepared to research exe.dev hosting for the pricing demo's source databases, the decision owner sent this, unprompted.
Block 2: Claude asked what to do with that VM. The option read: "Copy the six databases, repoint the demo, verify counts; local container stays as fallback." The decision owner chose it.
Block 3: Claude asked where the six databases go on the VM, recommending six databases owned by a new login role `demo` with a generated password kept only in the demo's local .env, the VM's other databases untouched. The decision owner typed this reply (option 1 is that recommendation).
Block 4: Claude pointed out that RightAngle is already the demo's ctrm database, proposed ctrm -> rightangle, planning -> aspen_pims, kittyhawk -> reference_data_hub, mips -> price_assessment, mpr -> price_reference, prodacct -> production_accounting, and recommended renaming the databases and replica schemas only, keeping the silver and gold names of the shared asset. The option read: "Six public or generic database names; silver and gold keep the shared asset's names." The decision owner chose it.
Block 5: after the renamed run, Claude asked whether to drop the six old replica schemas in the demo's Databricks catalog (replica_mips and the others), which held the internal names. The decision owner typed this reply.
Do not edit; scripts/epm_facts.py quotes checks quotes against this file. -->

I have already created a vm for postgress on exe.dev

Move demo there, keep local (Recommended)

Option 1. Also can we use a puckly available name for the systems. Use RightAngle instead of Kittyhawk, chnae mips, mpr, and proacct if this is a system name form this session

Databases and replicas only (Recommended)

drop tehm
