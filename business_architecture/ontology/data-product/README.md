# data-product: data product definitions

The `data-product` module defines the data products in the portfolio (`../../business_process/data_product_portfolio.json`), the product lines and segments that group them, and their links to core processes. It holds definitions only, never data values (EPM-DEC-001-0005). Its namespace is `https://w3id.org/lsc/ontology/modules/data-product/`; its build reads `core` 2.3.0 for process IRIs (2.2.0 until 2026-10-23, EPM-DEC-001-0089; 2.1.0 until 2026-10-22, EPM-DEC-001-0076); its released 1.0.0 package requires `core` 2.2.0, and 1.1.0 requires `core` 2.3.0 (EPM-DEC-001-0091). EPM-DEC-001-0053 records the design.

| File | What |
|---|---|
| `vocabulary.ttl` | The classes (data product, data product line, portfolio segment), the portfolio scheme, the portfolio status code list, and the properties `anchoredIn`, `producedBy` and `consumedBy`. `dp:DataProduct` is mapped to DCAT 3's `dcat:Dataset` with `skos:closeMatch`, not imported (EPM-DEC-001-0023) |
| `shapes.ttl` | SHACL shapes, with a stated cardinality on every property: each item is defined or parked with its reason, never both; an active item is defined; a data product sits in one line and a line in one segment; a data product carries no data values |
| `links.csv` | The process links a recorded decision names, with the release each waits for when its process is not yet in `core` |
| `build_data_products.py`, `data-products.ttl` | The build: the portfolio and `links.csv` in, 3 segments, 19 lines and 49 data products out (48 before Customer Master, 2026-10-23, EPM-DEC-001-0091). `python3 build_data_products.py` prints the figures; `--verify` fails unless `data-products.ttl` equals a fresh build. `scripts/check.sh` runs it |
| `test_data_products.py` | Tests: the vocabulary is well formed, the build is current and its figures match a hand count, each item keeps the portfolio's status and place, segment anchors, aliases, Loss Control's link to its producing process, and SHACL accepts the module and rejects broken items |

The module is not released yet. A release needs the decision owner's approval. *2026-10-22:* released as 1.0.0, with the decision owner's approval of the release plan (EPM-DEC-001-0077). The package is in `../releases/data-product/1.0.0/`. *2026-10-23:* 1.1.0, with the decision owner's approval of the close-out releases, is in `../releases/data-product/1.1.0/` (EPM-DEC-001-0091).

## What is defined and what is parked

- **Defined (16 data products; 15 before Customer Master, 2026-10-23, EPM-DEC-001-0091):** every active data product in the Commercial segment, from the portfolio's description; Customer Master, on the Marketing & Sales line, is the sixteenth.
- **Parked (33 data products):** every Midstream and Corporate data product. The portfolio names each one with status `defined_only` and gives no description, so each carries a `skos:editorialNote` saying its definition waits for its data owners. Nothing is written in their place.
- **Process links:** a data product's producing and consuming processes come from the value streams' `produces` and `consumes`, in the `value-stream` module (EPM-DEC-001-0054). The one link a decision names directly, Loss Control produced by CM 1.1.3.7.13 Reconcile Movement Losses and Gains (EPM-DEC-001-0048), waited for `core` 2.2.0, because CM 1.1.3.7.13 was added to the map after `core` 2.1.0. *2026-10-22:* `core` 2.2.0 adds the process (EPM-DEC-001-0076), so the link is emitted; the build reads `core` 2.2.0. *2026-10-23:* the build reads `core` 2.3.0 (EPM-DEC-001-0089). *2026-10-23:* a second, Customer Master produced by CM 1.3.7.1.1 (MPC-P10.3, EPM-DEC-001-0091).
- **Aliases:** an alias in the portfolio that names one item becomes its `skos:altLabel`. "Master & Rack Pricing" names two data products, so it labels neither.
