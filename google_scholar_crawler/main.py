from scholarly import scholarly
import json
from datetime import datetime
import os
import sys


def log(msg):
    print(msg, flush=True)


def main():
    scholar_id = os.environ.get("GOOGLE_SCHOLAR_ID")
    if not scholar_id:
        raise RuntimeError("GOOGLE_SCHOLAR_ID is not set")

    log(f"[1/6] Loading author by id: {scholar_id}")
    author = scholarly.search_author_id(scholar_id)

    log("[2/6] Filling basic author info...")
    scholarly.fill(author, sections=["basics", "indices", "counts"])

    log("[3/6] Filling publications list...")
    try:
        scholarly.fill(author, sections=["publications"])
    except Exception as e:
        log(f"[WARN] Failed to fully load publications list: {e}")
        author.setdefault("publications", [])

    publications = author.get("publications", [])
    log(f"[4/6] Found {len(publications)} publications")

    publication_map = {}
    for i, pub in enumerate(publications, 1):
        try:
            pub_id = pub.get("author_pub_id")
            title = pub.get("bib", {}).get("title", f"pub_{i}")

            log(f"[4/6] Processing publication {i}/{len(publications)}: {title}")

            # 尽量补充单篇信息；失败也不要影响整体
            try:
                scholarly.fill(pub)
            except Exception as e:
                log(f"[WARN] Failed to fill publication '{title}': {e}")

            if pub_id:
                publication_map[pub_id] = pub

        except Exception as e:
            log(f"[WARN] Unexpected publication parse error at item {i}: {e}")

    log("[5/6] Writing JSON files...")
    author["updated"] = str(datetime.now())
    author["publications"] = publication_map

    os.makedirs("results", exist_ok=True)

    with open("results/gs_data.json", "w", encoding="utf-8") as outfile:
        json.dump(author, outfile, ensure_ascii=False)

    shieldio_data = {
        "schemaVersion": 1,
        "label": "citations",
        "message": str(author.get("citedby", 0)),
    }

    with open("results/gs_data_shieldsio.json", "w", encoding="utf-8") as outfile:
        json.dump(shieldio_data, outfile, ensure_ascii=False)

    log("[6/6] Done.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[FATAL] {e}", file=sys.stderr, flush=True)
        raise
