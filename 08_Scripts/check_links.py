# -*- coding: utf-8 -*-
"""Sitedeki kaynak bağlantılarının açılıp açılmadığını kontrol eder (HTTP durum kodu). Ağ yoksa atlanır."""
import concurrent.futures as cf
import urllib.request
import resources as R

UA = {"User-Agent": "Mozilla/5.0"}


def status(url):
    last = "?"
    for _ in range(3):  # geçici ağ dalgalanmalarına karşı 3 deneme
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=25) as r:
                return r.status
        except urllib.error.HTTPError as e:
            return e.code
        except Exception as e:
            last = str(type(e).__name__)
    return last


def check_all():
    urls = {k: v[1] for k, v in R.LINKS.items()}
    with cf.ThreadPoolExecutor(8) as ex:
        res = dict(zip(urls, ex.map(status, urls.values())))
    return res


def check_videos(ids):
    import json
    import urllib.parse

    def ok(v):
        try:
            u = "https://www.youtube.com/oembed?url=" + urllib.parse.quote("https://www.youtube.com/watch?v=" + v) + "&format=json"
            with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=20) as r:
                return bool(json.loads(r.read().decode("utf-8")).get("title"))
        except Exception:
            return False
    with cf.ThreadPoolExecutor(8) as ex:
        return dict(zip(ids, ex.map(ok, ids)))


if __name__ == "__main__":
    res = check_all()
    bad = {k: v for k, v in res.items() if v != 200}
    print(f"{len(res) - len(bad)}/{len(res)} bağlantı HTTP 200", bad or "")
