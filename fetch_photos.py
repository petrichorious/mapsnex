#!/usr/bin/env python3
import json, os, urllib.request, urllib.parse, ssl, time

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

UA = "HotDFamilyTree/1.0 (personal educational project)"
OUT = os.path.join(os.path.dirname(__file__), "images")
os.makedirs(OUT, exist_ok=True)

# id -> list of candidate Wikipedia titles (first that yields an image wins)
CHARS = {
    "otto":     ["Otto Hightower"],
    "lyonel":   ["Lyonel Strong"],
    "corlys":   ["Corlys Velaryon"],
    "rhaenys":  ["Rhaenys Velaryon", "Rhaenys Targaryen"],
    "aemma":    ["Aemma Arryn"],
    "viserys":  ["Viserys I Targaryen"],
    "alicent":  ["Alicent Hightower"],
    "daemon":   ["Daemon Targaryen"],
    "rhea":     ["Rhea Royce"],
    "laenor":   ["Laenor Velaryon"],
    "rhaenyra": ["Rhaenyra Targaryen"],
    "aegon2":   ["Aegon II Targaryen"],
    "helaena":  ["Helaena Targaryen"],
    "aemond":   ["Aemond Targaryen"],
    "daeron":   ["Daeron the Daring", "Daeron Targaryen"],
    "laena":    ["Laena Velaryon"],
    "harwin":   ["Harwin Strong"],
    "larys":    ["Larys Strong"],
    "jace":     ["Jacaerys Velaryon"],
    "luke":     ["Lucerys Velaryon"],
    "joffrey":  ["Joffrey Velaryon"],
    "aegon3":   ["Aegon III Targaryen"],
    "viserys2": ["Viserys II Targaryen"],
    "jaehaerys":["Jaehaerys Targaryen (son of Aegon II)", "Jaehaerys Targaryen"],
    "jaehaera": ["Jaehaera Targaryen"],
    "maelor":   ["Maelor Targaryen"],
    "baela":    ["Baela Targaryen"],
    "rhaena":   ["Rhaena Targaryen (daughter of Daemon)", "Rhaena Targaryen"],
}

API_BASE = "https://gameofthrones.fandom.com/api.php"

def fetch(url):
    for attempt in range(6):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, context=ctx, timeout=25) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(5 + attempt * 5)
                continue
            raise
    return None

def api(title):
    q = urllib.parse.urlencode({
        "action": "query", "titles": title, "prop": "pageimages",
        "format": "json", "pithumbsize": "600", "redirects": "1",
    })
    url = API_BASE + "?" + q
    b = fetch(url)
    if not b:
        return None
    data = json.loads(b)
    pages = data.get("query", {}).get("pages", {})
    for _, p in pages.items():
        thumb = p.get("thumbnail", {}).get("source")
        if thumb:
            return thumb
    return None

def download(url, path):
    b = fetch(url)
    if not b or len(b) < 1200:
        return False
    with open(path, "wb") as f:
        f.write(b)
    return True

ok, fail = [], []
for cid, titles in CHARS.items():
    got = False
    for t in titles:
        try:
            src = api(t)
            if src and download(src, os.path.join(OUT, cid + ".jpg")):
                ok.append(cid); got = True; break
        except Exception as e:
            pass
    if not got:
        fail.append(cid)
    time.sleep(1.5)

print("OK   (%d):" % len(ok), ",".join(sorted(ok)))
print("FAIL (%d):" % len(fail), ",".join(sorted(fail)))
