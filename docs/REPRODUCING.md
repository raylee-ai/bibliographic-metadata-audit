# Reproducing the citation audit

The bundled example checks whether four document-reference pairs survive a data conversion. It runs offline with Python 3.10 or later and the standard library.

## Run the existing tests

From the repository root:

```sh
python3 -m unittest -v
```

The tests cover identifier normalization, duplicate pairs, changes attributed to the correct document, the supported OpenAlex JSON shapes, malformed inputs and the published source excerpt.

## Run the two examples

```sh
python3 reference_audit.py examples/accepted_works.json examples/filtered.csv
python3 reference_audit.py examples/accepted_works.json examples/preserved.csv
```

| Converted input | Before pairs | After pairs | Lost | Added | Expected exit code |
| --- | ---: | ---: | ---: | ---: | ---: |
| `examples/filtered.csv` | 4 | 2 | 2 | 0 | 1 |
| `examples/preserved.csv` | 4 | 4 | 0 | 0 | 0 |

Exit code **1** means the comparison found a difference. The filtered example deliberately produces it. If a shell or CI job stops on a nonzero exit code, run the examples separately or explicitly check for the expected code. Treating every nonzero result as success would also hide input errors.

The filtered example loses these pairs:

| Document | Reference |
| --- | --- |
| `W2128261329` | `W621128614` |
| `W2152126086` | `W621128614` |

The [CI workflow](../.github/workflows/ci.yml) runs the existing tests on Python 3.10 and checks each example's exit code and report counts. It runs for pull requests and pushes to `main`.

## Input and output contract

- The before snapshot can be CSV or UTF-8 OpenAlex JSON: a single work, an array of works or an object containing a `results` array.
- CSV inputs need `document_id` and `reference_id` columns.
- OpenAlex work records need an `id` and a `referenced_works` array. An empty array contributes zero pairs; a missing or null array is an input error.
- A full OpenAlex work URL and its bare work ID are normalized to the same identifier. Duplicate pairs count once.
- The JSON report contains pair counts plus `lost` and `added` lists.

| Exit code | Meaning |
| --- | --- |
| 0 | The normalized sets of pairs are equal |
| 1 | At least one pair was lost or added |
| 2 | An input could not be read or validated |

The program compares the supplied snapshots. It does not fetch missing pages of an API response or decide whether two bibliographic records identify the same work or edition.

## What this example establishes

[accepted_works.json](../examples/accepted_works.json) is a four-pair excerpt from the November 2026 study snapshot described in the [README](../README.md). It contains two selected references from each of two accepted OpenAlex works:

- [The evolution of costly displays, cooperation and religion](https://openalex.org/W2128261329)
- [The cultural evolution of prosocial religions](https://openalex.org/W2152126086)

[source.csv](../examples/source.csv) expresses the source pairs as CSV. [filtered.csv](../examples/filtered.csv) models the discussed identifier-length filter; [preserved.csv](../examples/preserved.csv) keeps all four pairs.

This small fixture demonstrates how losing one reference from each paper changes the comparison. It does not independently reproduce every statistic from the historical 140-record study, run bibliometrix or establish a book's edition identity. Those claims require their own evidence and, for full numerical reproduction, the corresponding complete data.
