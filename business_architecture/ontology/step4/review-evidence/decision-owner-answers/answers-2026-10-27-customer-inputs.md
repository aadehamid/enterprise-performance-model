<!-- The decision owner's words, verbatim from the Claude Code session of 2026-10-27, about the customer inputs of that day. Context (Claude's words, kept in this comment so they do not enter the quote corpus). The inputs themselves (two images and two Dealer Master documents) are kept out of the repository (EPM-DEC-001-0108). The body has 12 blocks, separated by blank lines.
Block 1: Claude asked which of the seven boxes drawn as core systems in the first image is not one of the six core systems.
Block 2: Claude asked whether the arrows from RightAngle to the Gravitate customer portal and from SAP MDG to Star were right, after showing where the two boxes are.
Block 3: Claude asked how many core fields Salesforce has, since the second image prints 11 and lists 10.
Block 4: Claude asked whether to drop the repeated fields of Polaris, of SAP MDG and of Polaris's enrich list; the decision owner gave this answer for each.
Block 5: Claude asked whether the second image's TMT and the first image's TMR are one system.
Block 6: Claude then noted that the party module already holds TMT and TMR as separate systems.
Block 7: Claude asked which is right when the second image says jobbers originate in Dealer Master and both Dealer Master documents say they do not. The option chosen said the documents are right: jobbers are mastered in SAP MDG and RightAngle and replicated into Dealer Master, and what Dealer Master originates and sends to SAP MDG is the ship-to station, which SAP MDG numbers in the 20000 series.
Block 8: Claude asked which records the second image's direct dealers, which sync from SAP MDG into Dealer Master, are. The option chosen said they are the six-digit sold-to customers that SAP MDG and RightAngle replicate into Dealer Master.
Block 9: Claude asked whether the ontology should keep SAP MDG and SAP S/4HANA apart, when the second Dealer Master document draws them as one box. The option chosen keeps them apart, as both images show.
Block 10: Claude presented the plan page, customer-inputs-plan-2026-10-27.html (kept with the inputs, out of the repository): 13 modeling questions with Claude's recommendations, and the releases party 2.0.0 (major), system 1.5.0 (minor), an integration minor, and no core change. The decision owner answered.
Block 11: Claude asked which arrow of the first image the label for the new customer setup belongs to.
Block 12: Later the same day, Claude asked about the three gaps EPM-DEC-001-0108 left open: whether Marathon, ARCO and Tesoro, the brands the inputs name, can be values of the party module's Brand class; how Dealer Master's billing customer number relates to the SAP customer number; and whether Dealer Master's fuel volumes reach the Enterprise Data Lake. The decision owner answered the first and could not answer the other two.
Do not edit; scripts/epm_facts.py quotes checks quotes against this file. -->

MAGIC is not

both are correct

10

dedup

same system, TMR is correct

so TMT should be treated separate then

The docs (Recommended)

Replicated Sold-Tos (Recommended)

Keep them separate (Recommended)

I am aligned with all your recommendation in the input plan.

Terminal upload to Kittyhawk

yes those can be brand values. Others I cannot answer.
