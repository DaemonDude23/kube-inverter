# TODO

- If a path is given, look for YAML files recursively, bypassing the need for the user to implement a loop.
- Testing and validation (`kubectl kustomize --dry-run=client /path/to/ingress` with `find`)
- Ensure temp file gets deleted no matter the exception.

## One Day...

- Allow updating only a subset of objects e.g. if not every YAML object in a file should have the same `pathPrefix`.
