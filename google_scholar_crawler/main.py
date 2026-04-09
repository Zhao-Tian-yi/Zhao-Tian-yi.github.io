from scholarly import scholarly
import json
from datetime import datetime
import os
import sys
import signal


def log(msg):
    print(msg, flush=True)


class TimeoutException(Exception):
    pass


def _timeout_handler(signum, frame):
    raise TimeoutException("Operation timed out")


def run_with_timeout(func, seconds, *args, **kwargs):
    old_handler = signal.signal(signal.SIGALRM, _timeout_handler)
    signal.alarm(seconds)
    try:
        return func(*args, **kwargs)
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)


# 主 ID -> 需要合并到这个主 ID 上的所有 Scholar 条目 ID
MERGE_BY_ID = {
    "mJlOsyYAAAAJ:YsMSGLbcyi4C": [
        "mJlOsyYAAAAJ:YsMSGLbcyi4C",
        "mJlOsyYAAAAJ:W7OEmFMy1HYC",
    ],
}


def main():
    scholar_id = os.environ.get("GOOGLE_SCHOLAR_ID")
    if not scholar_id:
        raise RuntimeError("GOOGLE_SCHOLAR_ID is not set")

    log(f"[1/6] Loading author by id: {scholar_id}")
    author = run_with_timeout(scholarly.search_author_id, 60, scholar_id)

    log("[2/6] Filling basic author info...")
    run_with_timeout(
        scholarly.fill,
        90,
        author,
        sections=["basics", "indices", "counts"]
    )

    log("[3/6] Filling publications list...")
    try:
        run_with_timeout(
            scholarly.fill,
            120,
            author,
            sections=["publications"]
        )
    except Exception as e:
        log(f"[WARN] Failed to fully load publications list: {e}")
        author.setdefault("publications", [])

    publications = author.get("publications", [])
    log(f"[4/6] Found {len(publications)} publications")

    raw_publications = {}

    for i, pub in enumerate(publications, 1):
        try:
            title = pub.get("bib", {}).get("title", f"pub_{i}")
            pub_id = pub.get("author_pub_id")
            log(f"[4/6] Processing publication {i}/{len(publications)}: {title}")

            try:
                run_with_timeout(scholarly.fill, 60, pub)
            except Exception as e:
                log(f"[WARN] Failed to fill publication '{title}': {e}")

            if not pub_id:
                continue

            citedby = int(pub.get("num_citations", 0) or 0)

            raw_publications[pub_id] = {
                "author_pub_id": pub_id,
                "bib": pub.get("bib", {}),
                "num_citations": citedby,
                "merged_citations": citedby,
                "source_ids": [pub_id],
            }

        except Exception as e:
            log(f"[WARN] Unexpected publication parse error at item {i}: {e}")

    final_publications = {}
    merged_ids = set()

    for main_id, id_list in MERGE_BY_ID.items():
        existing_ids = [pid for pid in id_list if pid in raw_publications]
        if not existing_ids:
            continue

        base_pub = raw_publications[main_id] if main_id in raw_publications else raw_publications[existing_ids[0]]
        total_citations = sum(int(raw_publications[pid].get("num_citations", 0) or 0) for pid in existing_ids)

        merged_pub = dict(base_pub)
        merged_pub["merged_citations"] = total_citations
        merged_pub["source_ids"] = existing_ids

        final_publications[main_id] = merged_pub
        merged_ids.update(existing_ids)

    for pub_id, pub in raw_publications.items():
        if pub_id not in merged_ids:
            final_publications[pub_id] = pub

    log("[5/6] Writing JSON files...")
    author["updated"] = str(datetime.now())
    author["publications"] = final_publications

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
    except TimeoutException as e:
        print(f"[FATAL] Scholar request timed out: {e}", file=sys.stderr, flush=True)
        raise
    except Exception as e:
        print(f"[FATAL] {e}", file=sys.stderr, flush=True)
        raise
