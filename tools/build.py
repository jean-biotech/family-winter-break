"""Build winter-trip-options.html from notes/*.json research files."""
import hashlib, json, pathlib, re, urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent.parent
NOTES = ROOT / "notes"
BATCHES = ["europe", "asia", "hawaii", "na", "new-us", "new-europe", "new-other", "new-malaysia", "new-china"]
# trips the family dropped (kept in the notes, left off the page)
EXCLUDE = {"croatia", "puerto-rico", "japan", "singapore", "singapore-bangkok", "usvi", "rome",
           "arizona-parks", "california-coast", "california-desert", "china"}


def commons(photo):
    name = photo["file"].strip()
    name = re.sub(r"^(File|Image):", "", name).replace(" ", "_")
    name = name[0].upper() + name[1:]
    h = hashlib.md5(name.encode()).hexdigest()
    q = urllib.parse.quote(name)
    base = "https://upload.wikimedia.org/wikipedia/commons"
    photo["src"] = f"{base}/thumb/{h[0]}/{h[:2]}/{q}/960px-{q}"
    photo["orig"] = f"{base}/{h[0]}/{h[:2]}/{q}"
    for k in ("author", "license"):
        if re.search(r"see commons|unverified|not confirmed|unknown", photo.get(k) or "", re.I):
            photo[k] = ""
    if not photo["author"] and not photo["license"]:
        photo["author"], photo["license"] = "Wikimedia Commons", "see file page"
    photo["author"] = photo["author"] or "Wikimedia Commons"
    photo["license"] = photo["license"] or "see file page"
    photo["page"] = f"https://commons.wikimedia.org/wiki/File:{q}"
    found = CHECK.get(photo["file"].replace("_", " ").strip())
    if found:
        # the exact preview address Wikimedia gives (it now blocks hand-built and full-size links)
        photo["src"] = found["src"].split("?")[0]
        photo["author"], photo["license"], photo["page"] = found["author"], found["license"], found["page"]
    return photo


CHECK = {}
_check = NOTES / "photo-check.json"
if _check.exists():
    for o in json.loads(_check.read_text()):
        if o.get("found"):
            CHECK[o["file"].replace("_", " ").strip()] = o["found"]


def load():
    dests = []
    for b in BATCHES:
        p = NOTES / f"{b}.json"
        if p.exists():
            dests += [d for d in json.loads(p.read_text()) if d["id"] not in EXCLUDE]
    # later files win: per-region price re-checks, then the nonstop-preference flight pass
    for pp in [NOTES / f"price-{b}.json" for b in BATCHES] + [NOTES / "price-nonstop.json"]:
        if not pp.exists():
            continue
        fixes = json.loads(pp.read_text())
        for d in dests:
            fix = dict(fixes.get(d["id"]) or {})
            if not fix:
                continue
            seen = {x["url"] for x in d["sources"]}
            d["sources"] += [x for x in fix.pop("sources", []) if x["url"] not in seen and x["url"].startswith("http")]
            if "fly" in fix:
                d["flyOverride"] = fix.pop("fly")
            for k in ("from", "routing", "airline"):
                if k in fix:
                    d["flight"][k] = fix.pop(k)
            if fix.get("alt"):
                d["flight"]["notes"] = "Other option: " + fix.pop("alt")
            fix.pop("alt", None)
            d["costPP"].update(fix)
    for d in dests:
        place = d["name"].split(",")[-1].strip()  # country or state, to keep photo searches on target
        for ph in d.get("heroPhotos", []) + [x["photo"] for x in d.get("itinerary", []) if x.get("photo")]:
            commons(ph)
            ph["q"] = f'{ph.get("caption", "")} {place}'.strip()
        c = d["costPP"]
        c["trip"] = c["flights"] + c["lodging"]
    fly = json.loads((NOTES / "display.json").read_text())
    # Asia trips leave Dec 12 and land a day or two later, so day 1 starts later
    start = {"japan": 1, "thailand": 1, "south-vietnam": 1, "singapore": 2, "singapore-bangkok": 2, "malaysia": 1, "china": 1}
    for d in dests:
        d["start"] = start.get(d["id"], 0)
        d["fly"] = d.pop("flyOverride", None) or fly.get(d["id"]) or d.get("fly") or d["flight"].get("hours", "")
        # drop notes about our own research process; keep real open questions
        d["unverified"] = [u for u in d.get("unverified", [])
                           if not re.search(r"photo|search budget|Commons|author/license", u, re.I)]
    recs = json.loads((NOTES / "recs.json").read_text()) if (NOTES / "recs.json").exists() else []
    # Vietnamese text (notes/vi-*.json, same shape as the English fields) for the language switch
    vi = {}
    for p in sorted(NOTES.glob("vi-[0-9]*.json")):
        vi.update(json.loads(p.read_text()))
    vi_recs = vi.pop("_recs", {})
    for d in dests:
        if d["id"] in vi:
            d["vi"] = vi[d["id"]]
    for r in recs:
        if r["id"] in vi_recs:
            r["vi"] = vi_recs[r["id"]]
    return dests, recs


def main():
    dests, recs = load()
    tpl = (ROOT / "tools" / "template.html").read_text()
    def tidy(v, key=""):
        if isinstance(v, dict):
            return {k: tidy(x, k) for k, x in v.items()}
        if isinstance(v, list):
            return [tidy(x, key) for x in v]
        if isinstance(v, str) and key not in ("file", "src", "orig", "page", "url", "q"):
            return v.replace("\u2014", ", ").replace("\u2013", "-")
        return v
    data = json.dumps(tidy({"dests": dests, "recs": recs}), ensure_ascii=False).replace("</", "<\\/")
    out = tpl.replace("/*__DATA__*/null", data)
    (ROOT / "winter-trip-options.html").write_text(out)
    (ROOT / "index.html").write_text(out)  # so GitHub Pages serves it at the site root
    print(f"built {len(dests)} destinations, {sum(len(d.get('itinerary', [])) + len(d.get('heroPhotos', [])) for d in dests)} photos")


if __name__ == "__main__":
    main()
