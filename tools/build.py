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
    for d in dests:
        for ph in d.get("heroPhotos", []):
            commons(ph)
        for day in d.get("itinerary", []):
            if day.get("photo"):
                commons(day["photo"])
        c = d["costPP"]
        c["trip"] = c["flights"] + c["lodging"]
    fly = json.loads((NOTES / "display.json").read_text())
    for d in dests:
        d["fly"] = fly.get(d["id"], d["flight"].get("hours", ""))
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
    print(f"built {len(dests)} destinations, {sum(len(d.get('itinerary', [])) + len(d.get('heroPhotos', [])) for d in dests)} photos")


if __name__ == "__main__":
    main()
