# R1 source-JSON structural diff

682 → 683 nodes (2026-09-22). The file framing (leading blank line, 2-space indent, trailing newline) is preserved, so the textual diff below shows only structural moves.

| slug | before (level, parent) | after (level, parent) | note |
|---|---|---|---|
| `CM-1-1-4` | (3, 'CM-1-1') | (2, 'L1-refining') | renamed 'Refinery Planning and Optimization', subtree shifted up one level |
| `CM-1-1-7` | (3, 'CM-1-1') | (2, 'L1-refining') | renamed 'Refinery Production Planning and Scheduling', subtree shifted up one level |
| `CM-1-1-4-6` | (4, 'CM-1-1-4') | (3, 'CM-1-1') | tombstone re-anchored under CM-1-1 (still deprecated) |
| `CM-1-1-4-6-1` | (5, 'CM-1-1-4-6') | (4, 'CM-1-1-4-6') | PTC-001-B hold: unchanged owner, shifted with tombstone |
| `L2-refinery-asset-reliability-and-turnaround-coordination` | None | (2, 'L1-refining') | new Candidate L2 (initially unpopulated) |
