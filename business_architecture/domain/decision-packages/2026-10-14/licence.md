# The ontology licence, now that nothing will be hosted

*2026-10-18:* answered by the decision owner, "5. Make it propriatery" (EPM-DEC-001-0041).

Prepared for the decision owner on 2026-10-14. When prepared, nothing here was decided. The question ends with options, a recommendation and what happens on each answer.

On 2026-10-14 you decided not to host the namespace `https://w3id.org/lsc/ontology/`, because the domain may change: "we can use it as placeholder for now" (EPM-DEC-001-0039; your words in `ontology/step4/review-evidence/decision-owner-answers/namespace-hosting.md`). EPM-DEC-001-0037 "For the decision owner" item 3 asked you (until 2026-10-18) to "Choose where the files are hosted and under which license" (line 32). This package covers the licence half of that item.

## What you need to do

1. Decide whether the ontology needs a new licence now. Recommended: no. Keep it proprietary, all rights reserved, until you decide to publish it.

## What the repo says today

A licence policy already exists. The worklog has a section headed "License policy — decided 2026-09-18". It says the ontology artifacts are "proprietary, all rights reserved" and that you are the IP owner. Its reason is that the ontology describes LSC's actual operations. It adds "Can be opened later; cannot be un-opened." (`business_architecture/ontology/step4/playbook/ontology-worklog.md`, section "License policy — decided 2026-09-18".)

The ontology README states the same policy, at `business_architecture/ontology/README.md` lines 74 to 76:

```text
- **License:** this folder's contents are proprietary, all rights reserved.
  APQC-sourced material is used under the APQC/IBM license terms —
  attribution travels with every distribution (see `../reference/README.md`).
```

The released files say less than that policy:

- The `core` 1.0.0 and 2.0.0 headers carry `dcterms:license core:license`, which expands to `https://w3id.org/lsc/ontology/modules/core/license` (`releases/core/2.0.0/core.ttl` line 18290). `release/build_core.py` line 283 writes it. That IRI is in the placeholder namespace, and no file describes it, so it names no licence text.
- The organization 1.0.0 and `ref-mpc` 1.0.0 headers carry no licence and no rights statement.
- None of the four DCAT records (`releases/core/1.0.0/catalog.ttl`, `releases/core/2.0.0/catalog.ttl`, `releases/organization/1.0.0/catalog.ttl`, `releases/ref-mpc/1.0.0/catalog.ttl`) carries `dcterms:license` or `dcterms:rights`.
- No release header carries the `dcterms:rights` "© LSC. All rights reserved." statement that the worklog's example ontology header shows (search the worklog for `All rights reserved`).

One fact changes the picture. The GitHub repo `<owner>/enterprise-performance-model` is public, and it has no LICENSE file (`gh repo view --json visibility,licenseInfo` returns `PUBLIC` and `null`; 0 forks). So the ontology is not hosted, but anyone can read it. *2026-10-18:* the repository is now private, at the decision owner's instruction (EPM-DEC-001-0040). *2026-10-19:* public again temporarily, for the current goal (EPM-DEC-001-0050). GitHub's documentation says that without a licence "the default copyright laws apply, meaning that you retain all rights to your source code and no one may reproduce, distribute, or create derivative works from your work." It also says that other GitHub users "have the right to view and fork your repository" under GitHub's Terms of Service (https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository, read 2026-10-14).

## What third-party content the ontology carries

APQC. `core` 2.0.0 references APQC PCF elements by ID: 751 lines in `releases/core/2.0.0/core.ttl` cite an `apqc-pcf-7.2.2/element/` IRI. Each element node has only an ID and a title such as "APQC Downstream Petroleum PCF v7.2.2, element 10003" (line 10153). Some editorial notes quote an APQC element name, for example "APQC 10252 'Maintain master data'" (line 355). The APQC source node carries `dcterms:rights "Used with attribution per the APQC/IBM license."` (line 18260). No release file carries APQC's full attribution notice.

APQC's terms are in the "Copyright and Attribution" sheet of the workbook in the repo, `business_architecture/reference/APQC-PCF-Downstream-Petroleum-v7.2.2.xlsx` (version 7.2.2, published 2025-05-30, per https://www.apqc.org/resource-library/resource-listing/apqc-process-classification-framework-pcf-downstream-petroleum-1, read 2026-10-14). The sheet says: "©2025 APQC and IBM reserve all rights in this work except as expressly granted herein. APQC and IBM hereby grant you a perpetual, worldwide, royalty-free license to use, copy, publish, modify, and create derivative works of the PCF, provided that all copies of the PCF include this notice, and any derivative works contain the following attribution: This work is based in part on an Industry Process Classification Framework ("PCF"), an open standard developed by APQC and IBM ..." `business_architecture/reference/README.md` lines 10 to 22 repeat the attribution.

MPC and peers. `ref-mpc` 1.0.0 holds public facts about MPC and MPLX, each with a source. It cites MPC's 10-K for fiscal 2025 (`releases/ref-mpc/1.0.0/ref-mpc.ttl` line 168) and links MPC's LEI record at GLEIF (line 162). No released module names a peer company. Peer filings sit in `business_architecture/reference/downstream-peers/`, outside the release packages.

## Question 1: does the ontology need a new licence now?

Nothing is hosted, and a public catalog is not planned. The recorded policy of 2026-09-18 already covers the files, and GitHub's default is all rights reserved. A new licence decision is needed only before someone is meant to reuse the files.

### Options

- (A) Keep the ontology proprietary, all rights reserved, until you decide to publish it. (Recommended) Reason: nothing is published, the 2026-09-18 policy already says this, and the worklog notes that a licence "can be opened later; cannot be un-opened". If you choose this, `README.md` line 74 stays as it is. I add a dated note to EPM-DEC-001-0037 item 3 saying the licence waits for a publication decision. Hosting is already settled by EPM-DEC-001-0039. The released packages do not change, so the dangling `dcterms:license` IRI in `core` stays until the next `core` release. At that release, the builder can write a `dcterms:rights` statement that says all rights reserved and carries APQC's attribution, in place of the IRI.
- (B) License the ontology files under Creative Commons Attribution 4.0 (CC BY 4.0, https://creativecommons.org/licenses/by/4.0/legalcode.en, version 4.0). Reason: anyone could reuse the files, with credit to you. The CC BY grant is "irrevocable", and it covers only rights "that the Licensor has authority to license", so it would not cover APQC's own text. APQC's terms allow derivative works, provided the attribution travels with them. If you choose this, `README.md` lines 74 to 76 change to name CC BY 4.0 for LSC's own content and APQC's terms for APQC content. The repo gets a LICENSE file, the release headers and all four `catalog.ttl` files get `dcterms:license <https://creativecommons.org/licenses/by/4.0/>`, and each package carries APQC's full attribution. A new release of each module is needed, because the released packages are fixed. The worklog policy of 2026-09-18 needs a new decision record that supersedes it. Before you choose this, check the rationale in that policy: the ontology describes LSC's actual operations.
- (C) Make the GitHub repo private. Reason: this keeps the files from being read at all while the licence and domain stay open. If you choose this, no file changes. GitHub's documentation says forks and local copies made before the change still exist. The repo has 0 forks today. Check what a private repo changes for the Cursor app and the CI runs before you choose this.

## Related, not part of this question

Your namespace decision of 2026-10-14 is recorded in EPM-DEC-001-0039 (PR #273). The ontology README (line 73) and EPM-DEC-001-0037 "For the decision owner" items 2 and 3 now carry it. Item 3 said the licence was still open, which was this question. *2026-10-18:* item 3 is closed (EPM-DEC-001-0041).
