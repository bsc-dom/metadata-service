# metadata-service

To install a Python package in “editable”/”development” mode Change directory to the root of the project directory and run:

```bash
python -m pip install -e .
```


# PUBLSIH

```bash
docker buildx build --platform linux/amd64,linux/arm64 \
-t bscdataclay/dspython:edge \
--build-arg PYTHON_VERSION=3.10-bullseye --push .
```