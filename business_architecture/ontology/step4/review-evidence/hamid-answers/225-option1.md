<!-- Hamid's words, verbatim from https://github.com/aadehamid/enterprise-performance-model/pull/225#issuecomment-6115615577 (fetched 2026-10-12). Do not edit; scripts/epm_facts.py quotes checks quotes against this file. -->

Option 1: close all 13 batch 1 rows as not emitted. Keep core:precedes locked as a process-level finish-to-start. Define a scoped sequence relation for these answers before the core 1.0.0 release, tracked in its own issue under #207.
