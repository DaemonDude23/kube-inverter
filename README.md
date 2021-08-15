**kube-inverter**

- [Why](#why)
- [This Tool's Purpose](#this-tools-purpose)
- [Install](#install)
  - [Put it in Your `$PATH`](#put-it-in-your-path)
- [CLI Usage](#cli-usage)
  - [Examples](#examples)
    - [Linux](#linux)
      - [In-place Update Against Multiple Files](#in-place-update-against-multiple-files)
      - [Write to Separate File](#write-to-separate-file)
- [Points of Interest](#points-of-interest)
  - [Detail About The New API Version's `spec`](#detail-about-the-new-api-versions-spec)
    - [Calculate `diff` Between Versions](#calculate-diff-between-versions)
    - [`v1beta1`](#v1beta1)
    - [`v1`](#v1)
- [Dev](#dev)
  - [Virtual Environment Setup](#virtual-environment-setup)

---

## Why

Kubernetes `v1.22` is [removing support](https://kubernetes.io/docs/reference/using-api/deprecation-guide/#ingress-v122) for the `v1beta` **apiVersion** for **Ingress** objects, not just _deprecating_ it. And `kubectl convert` was [deprecated](https://github.com/kubernetes/kubectl/issues/725#convert-as-a-plugin) back in 1.17.

The `Ingress` syntax is changing a bit. Sure, you could update them by hand, which I do often, but that is lame. I have hundreds upon hundreds of `Ingress` objects to convert, and I bet others do as well, so this should help.

## This Tool's Purpose

Converts **Kubernetes** `Ingress` YAML objects with `apiVersion: networking.k8s.io/v1beta1` _to_ `apiVersion: networking.k8s.io/v1`, modifying:

- The keys/values for:
  - `serviceName`
  - `ServicePort` - either name (`str`) or port number (`int`)
- Checks for `apiVersion` differences in the [Points of Interest](#points-of-interest) section.
- (Optional) Injects a configurable `pathPrefix` into each `Ingress` object.
- YAML Comments/order/formatting are preserved... mostly. It depends on their scope, but hey, I'm tryin'!
-

Requires Python `3.6`+

## Install

### Put it in Your `$PATH`

1. Get the code
```bash
git clone git clone https://github.com/DaemonDude/kube-inverter.git -b v0.1.0
```
2. Get into that directory
```bash
cd ./kube-inverter
```
3. Create symlink:
```bash
sudo ln -s ${PWD}/src/main.py /usr/local/bin/kube-inverter
```
4. Install dependencies:
```bash
pip3 install -r ./src/requirements.txt
```

## CLI Usage

- **By default, this will update your file in place**. If that's not desired, use `--dry-run` to test it, or write to a separate file with `--output-file`.
- Only one file is updated per run. Wrap this script in a loop (see examples further down) to operate it against multiple files.

```
usage: kube-inverter [-h] [--debug] [--output-file OUTPUT_FILE] [--path-type PATH_TYPE] [--version] input_file

Converts Kubernetes Ingress objects from 'networking.k8s.io/v1beta1' to 'networking.k8s.io/v1'

optional arguments:
  -h, --help            show this help message and exit

  --debug               enable debug logging (default: False)
  --output-file OUTPUT_FILE, -o OUTPUT_FILE
                        Output file path. This disables an in-place update to the input file (default: None)
  --path-type PATH_TYPE, --pathType PATH_TYPE, -p PATH_TYPE
                        Path Type for Ingress rule. Options: 'Exact', 'ImplementationSpecific', 'Prefix' (default: None)
  --version, -v         show program's version number and exit
  input_file            input file
```

### Examples

_See [examples](examples/) folder._

#### Linux

```bash
kube-inverter ./examples/in-place-update/input-1.yaml
```

##### In-place Update Against Multiple Files

```bash
find ./examples/in-place-update/ -type f -name '*.yaml' -exec kube-inverter '{}' \;
```

##### Write to Separate File

```bash
find ./examples/multiple-documents/ -type f -name '*.yaml' -exec kube-inverter '{}' -o '{}'-out \;
```

## Points of Interest

### Detail About The New API Version's `spec`

#### Calculate `diff` Between Versions

```bash
diff <(kubectl explain ingresses --api-version=networking.k8s.io/v1beta1 --recursive) <(kubectl explain ingresses --api-version=networking.k8s.io/v1 --recursive)
```

<details>
<summary>Click to expand output</summary>


```diff
2c2
< VERSION:  networking.k8s.io/v1beta1
---
> VERSION:  networking.k8s.io/v1
43c43
<       backend <Object>
---
>       defaultBackend  <Object>
48,49c48,52
<          serviceName  <string>
<          servicePort  <string>
---
>          service      <Object>
>             name      <string>
>             port      <Object>
>                name   <string>
>                number <integer>
60,61c63,67
<                   serviceName <string>
<                   servicePort <string>
---
>                   service     <Object>
>                      name     <string>
>                      port     <Object>
>                         name  <string>
>                         number        <integer>
```

</details>

#### `v1beta1`

```bash
kubectl explain ingresses --api-version=networking.k8s.io/v1beta1 --recursive
```

<details>
<summary>Click to expand output</summary>

```
KIND:     Ingress
VERSION:  networking.k8s.io/v1beta1

DESCRIPTION:
     Ingress is a collection of rules that allow inbound connections to reach
     the endpoints defined by a backend. An Ingress can be configured to give
     services externally-reachable urls, load balance traffic, terminate SSL,
     offer name based virtual hosting etc.

FIELDS:
   apiVersion   <string>
   kind <string>
   metadata     <Object>
      annotations       <map[string]string>
      clusterName       <string>
      creationTimestamp <string>
      deletionGracePeriodSeconds        <integer>
      deletionTimestamp <string>
      finalizers        <[]string>
      generateName      <string>
      generation        <integer>
      labels    <map[string]string>
      managedFields     <[]Object>
         apiVersion     <string>
         fieldsType     <string>
         fieldsV1       <map[string]>
         manager        <string>
         operation      <string>
         time   <string>
      name      <string>
      namespace <string>
      ownerReferences   <[]Object>
         apiVersion     <string>
         blockOwnerDeletion     <boolean>
         controller     <boolean>
         kind   <string>
         name   <string>
         uid    <string>
      resourceVersion   <string>
      selfLink  <string>
      uid       <string>
   spec <Object>
      backend   <Object>
         resource       <Object>
            apiGroup    <string>
            kind        <string>
            name        <string>
         serviceName    <string>
         servicePort    <string>
      ingressClassName  <string>
      rules     <[]Object>
         host   <string>
         http   <Object>
            paths       <[]Object>
               backend  <Object>
                  resource      <Object>
                     apiGroup   <string>
                     kind       <string>
                     name       <string>
                  serviceName   <string>
                  servicePort   <string>
               path     <string>
               pathType <string>
      tls       <[]Object>
         hosts  <[]string>
         secretName     <string>
   status       <Object>
      loadBalancer      <Object>
         ingress        <[]Object>
            hostname    <string>
            ip  <string>
            ports       <[]Object>
               error    <string>
               port     <integer>
               protocol <string>
```

</details>

#### `v1`

```bash
kubectl explain ingresses --api-version=networking.k8s.io/v1 --recursive
```

<details>
<summary>Click to expand output</summary>

```
KIND:     Ingress
VERSION:  networking.k8s.io/v1

DESCRIPTION:
     Ingress is a collection of rules that allow inbound connections to reach
     the endpoints defined by a backend. An Ingress can be configured to give
     services externally-reachable urls, load balance traffic, terminate SSL,
     offer name based virtual hosting etc.

FIELDS:
   apiVersion   <string>
   kind <string>
   metadata     <Object>
      annotations       <map[string]string>
      clusterName       <string>
      creationTimestamp <string>
      deletionGracePeriodSeconds        <integer>
      deletionTimestamp <string>
      finalizers        <[]string>
      generateName      <string>
      generation        <integer>
      labels    <map[string]string>
      managedFields     <[]Object>
         apiVersion     <string>
         fieldsType     <string>
         fieldsV1       <map[string]>
         manager        <string>
         operation      <string>
         time   <string>
      name      <string>
      namespace <string>
      ownerReferences   <[]Object>
         apiVersion     <string>
         blockOwnerDeletion     <boolean>
         controller     <boolean>
         kind   <string>
         name   <string>
         uid    <string>
      resourceVersion   <string>
      selfLink  <string>
      uid       <string>
   spec <Object>
      defaultBackend    <Object>
         resource       <Object>
            apiGroup    <string>
            kind        <string>
            name        <string>
         service        <Object>
            name        <string>
            port        <Object>
               name     <string>
               number   <integer>
      ingressClassName  <string>
      rules     <[]Object>
         host   <string>
         http   <Object>
            paths       <[]Object>
               backend  <Object>
                  resource      <Object>
                     apiGroup   <string>
                     kind       <string>
                     name       <string>
                  service       <Object>
                     name       <string>
                     port       <Object>
                        name    <string>
                        number  <integer>
               path     <string>
               pathType <string>
      tls       <[]Object>
         hosts  <[]string>
         secretName     <string>
   status       <Object>
      loadBalancer      <Object>
         ingress        <[]Object>
            hostname    <string>
            ip  <string>
            ports       <[]Object>
               error    <string>
               port     <integer>
               protocol <string>
```

</details>

## Dev

### Virtual Environment Setup

```bash
# assuming virtualenv is already installed...
./venv/bin/python -m pip install --upgrade pip
virtualenv --python=python3.9 ./venv/
source ./venv/bin/activate
pip3 install -r ./src/requirements.txt
```
