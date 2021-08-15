# TODO

- Testing and validation (`kubectl kustomize --dry-run=client /path/to/ingress` with `find`)
- Windows
  - Test
  - Docs
- Ensure temp file gets deleted no matter the exception.

## One Day...

- Allow updating only a subset of objects e.g. if not every YAML object in a file should have the same `pathPrefix`.
