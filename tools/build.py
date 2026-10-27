"""Build winter-trip-options.html from notes/*.json research files."""
import hashlib, json, pathlib, re, urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent.parent
NOTES = ROOT / "notes"
BATCHES = ["europe", "asia", "hawaii", "na"]


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
    return photo


def load():
    dests = []
    for b in BATCHES:
        p = NOTES / f"{b}.json"
        if p.exists():
            dests += json.loads(p.read_text())
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
            d["sources"] += [x for x in fix.pop("sources", []) if x["url"] not in seen]
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
        for ph in d.get("heroPhotos", []):
            commons(ph)
        for day in d.get("itinerary", []):
            if day.get("photo"):
                commons(day["photo"])
        c = d["costPP"]
        c["trip"] = c["flights"] + c["lodging"]
    fly = json.loads((NOTES / "display.json").read_text())
    # Asia trips leave Dec 12 and land a day or two later, so day 1 starts later
    start = {"japan": 1, "thailand": 1, "south-vietnam": 1, "singapore": 2, "singapore-bangkok": 2}
    for d in dests:
        d["start"] = start.get(d["id"], 0)
        d["fly"] = d.pop("flyOverride", None) or fly.get(d["id"], d["flight"].get("hours", ""))
        # drop notes about our own research process; keep real open questions
        d["unverified"] = [u for u in d.get("unverified", [])
                           if not re.search(r"photo|search budget|Commons|author/license", u, re.I)]
    recs = json.loads((NOTES / "recs.json").read_text()) if (NOTES / "recs.json").exists() else []
    return dests, recs


def main():
    dests, recs = load()
    tpl = (ROOT / "tools" / "template.html").read_text()
    data = json.dumps({"dests": dests, "recs": recs}, ensure_ascii=False).replace("</", "<\\/")
    out = tpl.replace("/*__DATA__*/null", data)
    # house style: no em dashes anywhere
    out = out.replace("—", ", ").replace("–", "-")
    (ROOT / "winter-trip-options.html").write_text(out)
    (ROOT / "index.html").write_text(out)  # so GitHub Pages serves it at the site root
    print(f"built {len(dests)} destinations, {sum(len(d.get('itinerary', [])) + len(d.get('heroPhotos', [])) for d in dests)} photos")


if __name__ == "__main__":
    main()
