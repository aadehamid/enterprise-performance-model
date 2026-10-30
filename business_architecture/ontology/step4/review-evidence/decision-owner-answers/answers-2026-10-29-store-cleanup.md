<!-- The decision owner's words, verbatim from the Claude Code session of 2026-10-29. Context (Claude's words, kept in this comment so they do not enter the quote corpus). A read-only audit of every store found no old or duplicate data, and these leftovers: 14 unnamed Docker volumes attached to no container (about 3.8 GB), two unused containers (practical_edison, pgadmin4_container), and three databases on the exe.dev VM owned by other logins ("Enterprise Performance Model", exedev, sales). The body has 2 blocks.
Block 1: the decision owner's instruction after the audit.
Block 2: asked which VM databases to drop, with each one's contents ("Enterprise Performance Model" empty; sales a small sample; exedev empty but the VM login's default database), the decision owner typed this reply. Claude then removed the 14 volumes and the two containers, dropped sales, and kept "Enterprise Performance Model" and exedev.
Do not edit; scripts/epm_facts.py quotes checks quotes against this file. -->

let us delete all unused volume. container and orphaned databases that we are not using on the vm before we warp up here

lets delete the sales one
