from scholarly import scholarly, ProxyGenerator
import json
from datetime import datetime
import os
import sys
import signal
from copy import deepcopy


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


# =========================
# User-configurable options
# =========================

# 主 ID -> 需要合并到这个主 ID 上的所有 Scholar 条目 ID
MERGE_BY_ID = {
    "mJlOsyYAAAAJ:YsMSGLbcyi4C": [
        "mJlOsyYAAAAJ:YsMSGLbcyi4C",
        "mJlOsyYAAAAJ:W7OEmFMy1HYC",
    ],
}

# 每个阶段的超时时间（秒）
SEARCH_AUTHOR_TIMEOUT = 60
FILL_AUTHOR_BASIC_TIMEOUT = 90
FILL_PUBLICATIONS_TIMEOUT = 120
FILL_SINGLE_PAPER_TIMEOUT = 45

# 如果 GitHub Actions 上 Scholar 不稳定，可以只抓前 N 篇
# 设为 0 表示抓全部
MAX_PUBLICATIONS = int(os.environ.get("MAX_PUBLICATIONS", "0"))

# 是否允许单篇论文 fill 失败后继续
CONTINUE_ON_PAPER_ERROR = True

# 可选代理环境变量：
# PROXY_HTTP=http://user:pass@host:port
# PROXY_HTTPS=http://user:pass@host:port
# 或者 USE_FREE_PROXIES=1
USE_FREE_PROXIES = os.environ.get("USE_FREE_PROXIES", "0") == "1"
PROXY_HTTP = os.environ.get("PROXY_HTTP")
PROXY_HTTPS = os.environ.get("PROXY_HTTPS")

# 使用已有结果作为兜底
CACHE_PATH = "results/gs_data.json"


def setup_proxy():
    """
    尝试配置 scholarly 代理。
    成功返回 True，失败返回 False。
    """
    try:
        if PROXY_HTTP or PROXY_HTTPS:
            log("[proxy] Trying single proxy from environment variables...")
            pg = ProxyGenerator()
            # scholarly 的 SingleProxy 支持 http/https
            ok = pg.SingleProxy(http=PROXY_HTTP, https=PROXY_HTTPS)
            if ok:
                scholarly.use_proxy(pg)
                log("[proxy] Single proxy enabled.")
                return True
            log("[proxy] Single proxy setup returned False.")
            return False

        if USE_FREE_PROXIES:
            log("[proxy] Trying free proxies...")
            pg = ProxyGenerator()
            ok = pg.FreeProxies()
            if ok:
                scholarly.use_proxy(pg)
                log("[proxy] Free proxies enabled.")
                return True
            log("[proxy] Free proxies setup returned False.")
            return False

    except Exception as e:
        log(f"[proxy][WARN] Failed to configure proxy: {e}")

    log("[proxy] No proxy enabled.")
    return False


def load_cached_data():
    if not os.path.exists(CACHE_PATH):
        return None
    try:
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        log(f"[cache] Loaded cache from {CACHE_PATH}")
        return data
    except Exception as e:
        log(f"[cache][WARN] Failed to load cache: {e}")
        return None


def save_json(author_data):
    os.makedirs("results", exist_ok=True)

    with open("results/gs_data.json", "w", encoding="utf-8") as outfile:
        json.dump(author_data, outfile, ensure_ascii=False)

    shieldio_data = {
        "schemaVersion": 1,
        "label": "citations",
        "message": str(author_data.get("citedby", 0)),
    }

    with open("results/gs_data_shieldsio.json", "w", encoding="utf-8") as outfile:
        json.dump(shieldio_data, outfile, ensure_ascii=False)


def merge_publications_by_id(raw_publications):
    """
    根据 MERGE_BY_ID 合并引用数。
    输出格式保持和原模板兼容：
    publications[main_id] = {
        ...
        "num_citations": 原始主条目引用,
        "merged_citations": 合并后引用,
        "source_ids": [...]
    }
    """
    final_publications = {}
    merged_ids = set()

    # 先处理需要合并的 ID
    for main_id, id_list in MERGE_BY_ID.items():
        existing_ids = [pid for pid in id_list if pid in raw_publications]
        if not existing_ids:
            continue

        base_pub = raw_publications[main_id] if main_id in raw_publications else raw_publications[existing_ids[0]]
        total_citations = sum(int(raw_publications[pid].get("num_citations", 0) or 0) for pid in existing_ids)

        merged_pub = deepcopy(base_pub)
        merged_pub["merged_citations"] = total_citations
        merged_pub["source_ids"] = existing_ids

        final_publications[main_id] = merged_pub
        merged_ids.update(existing_ids)

    # 其余未参与合并的论文照常保留
    for pub_id, pub in raw_publications.items():
        if pub_id not in merged_ids:
            final_publications[pub_id] = pub

    return final_publications


def build_fallback_from_cache(cached_data, scholar_id):
    """
    当在线抓取失败时，尽量从缓存构造可用结果。
    """
    if not cached_data:
        raise RuntimeError("No cache available for fallback.")

    fallback = deepcopy(cached_data)
    fallback["updated"] = str(datetime.now())
    fallback.setdefault("scholar_id", scholar_id)
    log("[fallback] Using cached data as fallback.")
    return fallback


def main():
    scholar_id = os.environ.get("GOOGLE_SCHOLAR_ID")
    if not scholar_id:
        raise RuntimeError("GOOGLE_SCHOLAR_ID is not set")

    log("[0/6] Initializing...")
    setup_proxy()
    cached_data = load_cached_data()

    # -------------------------
    # Step 1: load author page
    # -------------------------
    log(f"[1/6] Loading author by id: {scholar_id}")
    try:
        author = run_with_timeout(scholarly.search_author_id, SEARCH_AUTHOR_TIMEOUT, scholar_id)
    except Exception as e:
        log(f"[WARN] search_author_id failed: {e}")
        if cached_data:
            fallback = build_fallback_from_cache(cached_data, scholar_id)
            save_json(fallback)
            log("[6/6] Done with cache fallback.")
            return
        raise

    # -------------------------
    # Step 2: fill author basics
    # -------------------------
    log("[2/6] Filling basic author info...")
    try:
        run_with_timeout(
            scholarly.fill,
            FILL_AUTHOR_BASIC_TIMEOUT,
            author,
            sections=["basics", "indices", "counts"]
        )
    except Exception as e:
        log(f"[WARN] Failed to fill author basics: {e}")
        if cached_data:
            fallback = build_fallback_from_cache(cached_data, scholar_id)
            # 尝试用当前已有 author 的总引用覆盖缓存
            fallback["citedby"] = author.get("citedby", fallback.get("citedby", 0))
            fallback["updated"] = str(datetime.now())
            save_json(fallback)
            log("[6/6] Done with partial fallback.")
            return
        raise

    # -------------------------
    # Step 3: fill publication list
    # -------------------------
    log("[3/6] Filling publications list...")
    try:
        run_with_timeout(
            scholarly.fill,
            FILL_PUBLICATIONS_TIMEOUT,
            author,
            sections=["publications"]
        )
    except Exception as e:
        log(f"[WARN] Failed to fully load publications list: {e}")
        author.setdefault("publications", [])

    publications = author.get("publications", []) or []
    if MAX_PUBLICATIONS > 0:
        publications = publications[:MAX_PUBLICATIONS]
        log(f"[3/6] Truncated publications to first {MAX_PUBLICATIONS} items")

    log(f"[4/6] Found {len(publications)} publications")

    # -------------------------
    # Step 4: fill each paper
    # -------------------------
    raw_publications = {}

    for i, pub in enumerate(publications, 1):
        try:
            title = pub.get("bib", {}).get("title", f"pub_{i}")
            pub_id = pub.get("author_pub_id")
            log(f"[4/6] Processing publication {i}/{len(publications)}: {title}")

            try:
                run_with_timeout(scholarly.fill, FILL_SINGLE_PAPER_TIMEOUT, pub)
            except Exception as e:
                log(f"[WARN] Failed to fill publication '{title}': {e}")
                if not CONTINUE_ON_PAPER_ERROR:
                    raise

            if not pub_id:
                log(f"[WARN] Publication '{title}' has no author_pub_id, skipped.")
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

    # 如果单篇抓取结果太少，尝试用缓存补齐非关键字段
    if cached_data and isinstance(cached_data.get("publications"), dict):
        cached_pubs = cached_data.get("publications", {})
        for pub_id, cached_pub in cached_pubs.items():
            if pub_id not in raw_publications:
                raw_publications[pub_id] = cached_pub

    final_publications = merge_publications_by_id(raw_publications)

    # -------------------------
    # Step 5: write output
    # -------------------------
    log("[5/6] Writing JSON files...")
    author["updated"] = str(datetime.now())
    author["scholar_id"] = scholar_id
    author["publications"] = final_publications

    save_json(author)

    # -------------------------
    # Step 6: done
    # -------------------------
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
