#!/usr/bin/env python3
"""One-off: save the treaty list of EDIT (Electronic Database of Investment Treaties).

EDIT (World Trade Institute, https://edit.wti.org/) loads its search results with JavaScript
from a public JSON API. This script calls the same endpoints as the search page, 2 s apart:

- ``POST /web-public-api/document/investment-treaty/full_search``, 500 documents a page
  (9 pages on 2026-11-23): uuid, name, type (``WTI_TYPE_TREATY_BIT``, ``_OIIA`` or ``_MT`` for a
  model treaty), ISO party codes, dates of signature, entry into force and termination (or of
  publication for a model), and the start of the text (empty when EDIT has no text);
- ``POST /web-public-api/document/report/csv``: the same list as CSV with the languages of
  the text and EDIT's document reference, but without the uuid.

It saves metadata only: it does not download the treaty texts (``document/txt``) nor the PDFs.
``import_edit.py`` reads the files it writes.

Usage: python -I scripts/oneoff/fetch_edit.py OUT_DIR
"""

import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "https://edit.wti.org/web-public-api/"
DOCUMENT_TYPE = "ab84e341-c223-4f40-a355-a8d562032221"  # investment treaties
FORM = "public_full_search_list_document"
HEADERS = {"User-Agent": "internacia-db one-off (EDIT treaty list)", "X-Requested-With": "XMLHttpRequest"}


def post(route: str, fields: dict) -> bytes:
    body = urllib.parse.urlencode({f"{FORM}[{k}]": v for k, v in fields.items()}).encode()
    request = urllib.request.Request(BASE + route, data=body, headers=HEADERS, method="POST")
    with urllib.request.urlopen(request, timeout=300) as response:
        return response.read()


def main(argv: list[str]) -> int:
    out = Path(argv[0])
    out.mkdir(parents=True, exist_ok=True)
    page, pages = 1, 1
    while page <= pages:
        fields = {"page": page, "limit": 500, "documentType": DOCUMENT_TYPE,
                  "orderParameter": "date_signed_or_published", "orderValue": "desc"}
        data = post("document/investment-treaty/full_search", fields)
        pages = json.loads(data)["pages"]
        (out / f"fs_p{page}.json").write_bytes(data)
        print(f"page {page}/{pages}")
        page += 1
        time.sleep(2)
    (out / "export.csv").write_bytes(post("document/report/csv", {"documentType": DOCUMENT_TYPE}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
