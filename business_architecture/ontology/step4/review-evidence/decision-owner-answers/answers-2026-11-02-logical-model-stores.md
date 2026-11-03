<!-- The decision owner's words, verbatim from the Claude Code session of 2026-11-02, on whether the release's logical models load into the four ontology stores (EPM-DEC-001-0113, amendment "the stores"). Block 1: Claude asked whether the customer model's graphs should load into the stores, and recommended that Jena and Delta hold every graph (the vocabulary, ER Studio's export and the layer) as named graphs, and that Neo4j and AuraDB hold the vocabulary and the layer but not the export. Block 2: the decision owner's question about that recommendation. Claude answered that Neo4j and AuraDB would then show each entity as an unnamed node with links, that the two cautions behind it (size, and the projection's round-trip checks meeting a tool's export) do not hold up well, and recommended instead the full model as its own subgraph in Neo4j and AuraDB, apart from the ontology's Resource nodes as the technical graph is, with edges from each entity to the ontology nodes it links to and a drift check; Jena and Delta unchanged. Block 3: the decision owner's answer to that revised recommendation. -->

yes, go with your recommendation

does this mean Neo4j and Aura will not have logical model. Why do you think this is good?

yes, go with the full model as its own subgraph
