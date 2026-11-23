# Data Formats

Repository: https://github.com/glitter-node/data-toolkit

CSV: UTF-8 or UTF-8 BOM, first row headers. JSON/YAML: arrays of flat objects. XML: rows containing child elements; attributes and mixed content are not preserved. XLSX: active worksheet only, first row headers, cached formula values. Outputs are intended for tabular exchange and are not lossless document transformations. Dates and numeric types may change across formats. Do not use this tool for fidelity-critical archival conversions without independent validation.
