# Bibliographic Metadata Audit

Two papers cite the same two works. After a reference-network conversion, they appear to share just one. Which citation disappeared?

This offline Python tool compares citation pairs before and after a conversion. It grew out of a religious studies project where checking a bibliography meant answering two separate questions. Did the database find the work I meant? Once I accepted the match, did its references survive the analysis?

## Try it on four citation pairs

From the repository root, run these commands with Python 3.10 or later. The examples use the standard library and require no account or network connection.

~~~sh
python3 reference_audit.py examples/accepted_works.json examples/filtered.csv
~~~

The report shows **4 original pairs, 2 surviving pairs, and 2 lost pairs**. Both citing papers lost the same reference, `W621128614`. Within this excerpt their shared-reference count fell from two to one. The program exits with status **1** so a data pipeline can flag the difference.

~~~sh
python3 reference_audit.py examples/accepted_works.json examples/preserved.csv
~~~

This time all four pairs survive. A full OpenAlex URL and its bare work ID identify the same work. This comparison exits with status **0**.

The source fixture contains two references that occurred in both papers’ OpenAlex records in the November 2026 study snapshot. It is a four-pair excerpt of longer reference lists. The filtered fixture models the length rule observed in bibliometrix 5.5.0. To inspect the citing papers, see [The cultural evolution of prosocial religions](https://openalex.org/W2152126086) and [The evolution of costly displays, cooperation and religion](https://openalex.org/W2128261329).

## Use your own data

Start with the works you accepted during bibliographic review. For OpenAlex, save a single work object, an array of works, or a Works API response containing a `results` array as UTF-8 JSON. Each work needs an `id` and a `referenced_works` array. An empty array contributes zero pairs. A missing or null array raises an input error so an incomplete export is visible. The command reads only the works in the file. For paginated exports, collect every page you intend to audit first.

The second input is a UTF-8 CSV of the citation pairs you obtained after conversion. Use the same document identifiers across both files:

~~~csv
document_id,reference_id
paper-a,https://openalex.org/W621128614
paper-b,W621128614
~~~

Run `python3 reference_audit.py works.json after.csv`. If both snapshots are CSV, keep the same headers in both and run `python3 reference_audit.py before.csv after.csv`. The JSON report lists lost and added pairs. Repeated rows count once. Exit status **2** means the input could not be read or validated. A document with no reported references contributes no pairs, so this comparison alone cannot tell whether a reference list was empty or unavailable.

## Review the work before counting its references

These two decisions from the original study illustrate why a match needs a stated scope.

| Source record | Candidate and evidence | Decision |
| --- | --- | --- |
| Joseph Henrich, *The evolution of costly displays, cooperation and religion* (2009) | The author, core title, and DOI agree with the [OpenAlex record](https://openalex.org/W2128261329). | Accept the work-level match for the citation audit. |
| Bruce Lincoln, *Authority: Construction and Corrosion* (1994), print edition | The [candidate](https://openalex.org/W4229660601) has the same author, title, and year. The source identifies a print ISBN; the candidate DOI identifies an electronic edition. | Keep the edition unresolved and exclude it from this citation sample pending independent confirmation. |

The bundled JSON contains Henrich’s accepted paper and a second accepted paper, *The cultural evolution of prosocial religions*. Both records are excerpted to the two shared references. Lincoln’s candidate stays outside the input while the edition is unresolved. The command compares the supplied pairs. The researcher makes the identity decision before the audit.

## What happened in the original study

Of 140 purpose-selected records, 117 were accepted as work-level OpenAlex matches. Of those, 70 had nonempty OpenAlex reference lists. All 117 works imported into Biblioshiny. The loss occurred later, when building reference networks with **bibliometrix 5.5.0**.

The OpenAlex converter shortened full reference URLs to bare work IDs. The subsequent `cocMatrix(Field="CR")` step kept reference strings longer than ten characters. A valid ID such as `W621128614` is exactly ten characters long.

In this sample the filter removed **208 of 3,132 distinct cited IDs** and **232 of 3,592 document–reference pairs**, affecting 45 citing works. In a separate analysis copy, restoring the full URLs from the original records brought the tested coupling and co-citation matrices into agreement with independent counts. These figures describe the historical sample and software version. The small example above lets you inspect the mechanism without the full corpus or an R installation.

## Tests

~~~sh
python3 -m unittest -v
~~~

See the [reproduction guide](docs/REPRODUCING.md) for expected example results, exit codes and the scope of the bundled evidence.
