"""Look up every photo in the built page on Wikimedia Commons: does the file exist, its exact
960px thumbnail URL, and its real author and license. Writes notes/photo-check.json."""
import html, json, re, sys, time, urllib.parse, urllib.request

UA = "FamilyTripGuide/1.0 (https://github.com/jean-biotech/family-winter-break)"
API = "https://commons.wikimedia.org/w/api.php"


def get(params):
    url = API + "?" + urllib.parse.urlencode({**params, "format": "json"})
    for attempt in range(12):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code != 429:
                raise
            # Wikimedia throttles shared IPs; wait as asked, longer each time
            time.sleep(max(int(e.headers.get("Retry-After") or 0), 5 * (attempt + 1)))
    raise RuntimeError("rate limited")


def plain(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s or "")).strip()


def info(pages):
    out = {}
    for pg in pages.values():
        if "imageinfo" not in pg:
            continue
        ii = pg["imageinfo"][0]
        m = ii.get("extmetadata", {})
        out[pg["title"]] = {
            "title": pg["title"], "src": ii.get("thumburl") or ii["url"], "mime": ii.get("mime"),
            "width": ii.get("width"), "page": ii.get("descriptionurl"),
            "author": plain(m.get("Artist", {}).get("value"))[:80] or "Wikimedia Commons",
            "license": plain(m.get("LicenseShortName", {}).get("value")) or "see file page",
        }
    return out


def lookup(files):
    """files: list of bare file names -> {file: info or None}"""
    res = {}
    for i in range(0, len(files), 20):
        batch = files[i:i + 20]
        j = get({"action": "query", "redirects": 1, "prop": "imageinfo", "iiprop": "url|mime|size|extmetadata",
                 "iiextmetadatafilter": "Artist|LicenseShortName", "iiurlwidth": 960,
                 "titles": "|".join("File:" + f for f in batch)})
        q = j.get("query", {})
        alias = {}
        for kind in ("normalized", "redirects"):
            for n in q.get(kind, []):
                alias[n["from"]] = n["to"]
        found = info(q.get("pages", {}))
        for f in batch:
            t = "File:" + f
            while t in alias:
                t = alias[t]
            res[f] = found.get(t)
        time.sleep(4)
    return res


def search(query, limit=6):
    j = get({"action": "query", "generator": "search", "gsrnamespace": 6, "gsrlimit": limit,
             "gsrsearch": query + " filetype:bitmap", "prop": "imageinfo", "iiprop": "url|mime|size|extmetadata",
             "iiextmetadatafilter": "Artist|LicenseShortName", "iiurlwidth": 960})
    pages = j.get("query", {}).get("pages", {})
    order = sorted(pages.values(), key=lambda p: p.get("index", 0))
    found = info({str(i): p for i, p in enumerate(order)})
    return [found[p["title"]] for p in order if p["title"] in found and re.search("jpeg|png", found[p["title"]]["mime"] or "")]


if __name__ == "__main__":
    page = open(sys.argv[1]).read()
    data = json.loads(re.search(r"const DATA = (\{.*?\});\n", page, re.S).group(1))
    photos = []
    for d in data["dests"]:
        for k, ph in enumerate(d.get("heroPhotos", [])):
            photos.append((d["id"], f"hero{k}", ph))
        for x in d["itinerary"]:
            if x.get("photo"):
                photos.append((d["id"], f"day{x['day']}", x["photo"]))
    names = sorted({re.sub(r"^(File|Image):", "", p["file"]).replace("_", " ").strip() for _, _, p in photos})
    res = lookup(names)
    out = []
    for dest, slot, ph in photos:
        n = re.sub(r"^(File|Image):", "", ph["file"]).replace("_", " ").strip()
        out.append({"dest": dest, "slot": slot, "file": ph["file"], "caption": ph.get("caption"), "q": ph.get("q"), "found": res.get(n)})
    # Wikimedia blocks full-size originals; for photos narrower than 960px use the largest standard size below it
    for o in out:
        f = o["found"]
        if f and "upload.wikimedia.org" in f["src"]:
            step = max([w for w in (120, 250, 330, 500) if w < (f["width"] or 0)] or [120])
            j = get({"action": "query", "titles": f["title"], "prop": "imageinfo", "iiprop": "url", "iiurlwidth": step})
            ii = list(j["query"]["pages"].values())[0]["imageinfo"][0]
            f["src"] = ii.get("thumburl") or ii["url"]
            time.sleep(2)
    json.dump(out, open(sys.argv[2], "w"), indent=1, ensure_ascii=False)
    miss = [o for o in out if not o["found"]]
    print(f"{len(out)} photos, {len(names)} unique files, {len(miss)} missing")
    for o in miss:
        print("  MISSING", o["dest"], o["slot"], o["file"])
