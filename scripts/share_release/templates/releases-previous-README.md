# Earlier releases of each module

This folder holds, for each module, the releases before the newest one. It starts with one each, and each new release you make moves the one before it here. It is history: it shows that the ontology ships in versioned releases, with a changelog and a manifest whose hashes name every file.

Nothing loads it. The projection, the stores, the regression, the documents and every link read the newest set in `releases/<module>/<version>/` only. A package here may name, in what it requires, a version that this release does not carry (for example `system` 1.2.0); that is what it required when it was cut, and it is left as cut.

Each manifest's hashes are true of the files beside it: `sha256sum` any file here and compare.
