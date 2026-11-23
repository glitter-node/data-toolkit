# Third-Party Licenses

Repository: https://github.com/glitter-node/data-toolkit

The root `LICENSE` covers original Data Toolkit source only. This inventory
was checked on 2026-11-23 from the local `venv` using Python package metadata
and `pip freeze`. It covers the direct requirements and the resolved packages
in that environment; it is not a universal inventory for every platform or
optional extra.

## Direct requirements

| Distribution | Resolved version | License metadata | Upstream source | Role |
| --- | ---: | --- | --- | --- |
| fastapi | 0.165.0 | MIT | [FastAPI](https://github.com/fastapi/fastapi) | runtime |
| httpx | 0.28.1 | BSD-3-Clause | [HTTPX](https://github.com/encode/httpx) | test/runtime requirement |
| httpx2 | 2.16.2 | BSD-3-Clause | [httpx2](https://github.com/pydantic/httpx2) | test/runtime requirement |
| Jinja2 | 3.1.6 | BSD-3-Clause (verified from bundled `LICENSE.txt`) | [Jinja](https://github.com/pallets/jinja) | runtime dependency |
| python-multipart | 0.0.34 | Apache-2.0 | [python-multipart](https://github.com/Kludex/python-multipart) | runtime |
| pydantic | 2.10.4 | MIT | [Pydantic](https://github.com/pydantic/pydantic) | runtime |
| pydantic-settings | 2.16.3 | MIT | [pydantic-settings](https://github.com/pydantic/pydantic-settings) | runtime |
| python-dotenv | 1.2.4 | BSD-3-Clause | [python-dotenv](https://github.com/theskumar/python-dotenv) | runtime dependency |
| sse-starlette | 3.7.0 | BSD-3-Clause | [sse-starlette](https://github.com/sysid/sse-starlette) | runtime |
| openpyxl | 3.1.5 | MIT | [openpyxl](https://foss.heptapod.net/openpyxl/openpyxl) | runtime |
| PyYAML | 6.0.4 | MIT | [PyYAML](https://github.com/yaml/pyyaml) | runtime |
| defusedxml | 0.7.1 | PSFL | [defusedxml](https://github.com/tiran/defusedxml) | runtime |
| uvicorn | 0.30.6 | BSD-3-Clause (verified from `License-Expression` and bundled `LICENSE.md`) | [Uvicorn](https://github.com/encode/uvicorn) | runtime |
| pytest | 7.4.4 | MIT | [pytest](https://github.com/pytest-dev/pytest) | development/test |

`requirements.txt` contains ranges for several packages. The versions above
are the versions actually installed in the checked environment, not new
constraints imposed on normal installation. Jinja2's bundled license text was
read directly from the installed distribution and is BSD 3-Clause. Uvicorn's
installed metadata declares `BSD-3-Clause` and includes its BSD license text.

## Resolved transitive packages

The same environment resolved these additional packages:

| Distribution | Version | License metadata | Official source |
| --- | ---: | --- | --- |
| annotated-doc | 0.0.7 | MIT | [repository](https://github.com/fastapi/annotated-doc) |
| annotated-types | 0.8.0 | MIT | [repository](https://github.com/annotated-types/annotated-types) |
| anyio | 4.16.0 | MIT | [documentation](https://anyio.readthedocs.io/) |
| certifi | 2026.11.20 | MPL-2.0 | [repository](https://github.com/certifi/python-certifi) |
| click | 8.5.1 | BSD-3-Clause | [documentation](https://click.palletsprojects.com/) |
| et-xmlfile | 2.0.0 | MIT | [repository](https://foss.heptapod.net/openpyxl/et-xmlfile) |
| h11 | 0.16.0 | MIT | [repository](https://github.com/python-hyper/h11) |
| httpcore | 1.0.9 | BSD-3-Clause | [repository](https://github.com/encode/httpcore) |
| httpcore2 | 2.16.2 | BSD-3-Clause | [repository](https://github.com/pydantic/httpx2) |
| httptools | 0.9.0 | MIT | [repository](https://github.com/MagicStack/httptools) |
| idna | 3.20 | BSD-3-Clause | [repository](https://github.com/kjd/idna) |
| iniconfig | 2.3.1 | MIT | [repository](https://github.com/pytest-dev/iniconfig) |
| MarkupSafe | 3.0.4 | BSD-3-Clause | [repository](https://github.com/pallets/markupsafe) |
| opentelemetry-api | 1.45.2 | Apache-2.0 | [repository](https://github.com/open-telemetry/opentelemetry-python) |
| packaging | 26.3 | Apache-2.0 OR BSD-2-Clause | [repository](https://github.com/pypa/packaging) |
| pluggy | 1.7.0 | MIT | [repository](https://github.com/pytest-dev/pluggy) |
| pydantic-core | 2.27.2 | MIT | [repository](https://github.com/pydantic/pydantic-core) |
| starlette | 1.10.0 | BSD-3-Clause | [repository](https://github.com/Kludex/starlette) |
| truststore | 0.10.5 | MIT | [documentation](https://truststore.readthedocs.io/) |
| typing-extensions | 4.16.0 | PSF-2.0 | [repository](https://github.com/python/typing_extensions) |
| typing-inspection | 0.4.5 | MIT | [repository](https://github.com/pydantic/typing-inspection) |
| uvloop | 0.23.0 | MIT License (metadata) | [repository](https://github.com/MagicStack/uvloop) |
| watchfiles | 1.3.0 | MIT | [repository](https://github.com/samuelcolvin/watchfiles) |
| websockets | 17.4 | BSD-3-Clause | [repository](https://github.com/python-websockets/websockets) |

The environment also contains `pip` and `setuptools`, which are environment
tools rather than application requirements and are not included above. Some
packages may contain bundled notices or platform-specific binary components;
those notices must remain with any redistributed package artifacts. This
repository does not copy third-party source code or package artifacts into the
application tree.

## Optional and platform-specific dependency checks

Package metadata was also inspected for declared extras and conditional
dependencies:

- `uvicorn[standard]` is part of the declared requirement. The checked Linux
  resolution includes `httptools`, `python-dotenv`, `PyYAML`, `uvloop`,
  `watchfiles`, and `websockets`; these are listed in the resolved inventory.
  Its metadata conditionally selects `colorama` on Windows and excludes
  `uvloop` there.
- Jinja2's `i18n` extra would add Babel; it is not installed or used by this
  application.
- FastAPI, pydantic-settings, httpx/httpx2, and sse-starlette declare optional
  extras for CLI, cloud-secret, protocol, or example integrations. Those
  extras were not requested by `requirements.txt` and were not installed.
- A Linux environment was the only environment executed. Cross-platform
  `pip --dry-run` resolution is not treated as a Windows/macOS installation
  test because target-platform marker handling and binary availability depend
  on the actual host interpreter and index.

Accordingly, the direct requirements and the resolved Linux environment are
verified. Uninstalled optional extras and actual non-Linux installations still
require a separate package-resolution and license check before redistribution
for those targets.

## Verification and limitations

- License values are taken from installed distribution metadata or bundled
  license files. No SPDX identifier is inferred where the evidence is absent.
- The check covered the direct requirements and the resolved dependency set on
  Linux x86_64 with CPython 3.11.10. Optional extras and platform-specific
  dependency branches were not installed or audited.
- The inventory is therefore improved and evidence-based, but it is not a
  legal opinion or a complete audit of every possible installation.
- When redistributing wheels, archives, or a bundled deployment, retain each
  upstream license and notice included by that distribution. Recheck the
  package metadata and bundled license files for the target platform.
