#!/usr/bin/env python3
"""Kontrollnimekiri koodiga, mitte silma järgi. Kasutus: python3 kontroll.py"""

import json
import re
from html.parser import HTMLParser
from pathlib import Path

JUUR = Path("public")
vead = []
teated = []


def viga(t):
    vead.append(t)


def ok(t):
    teated.append(t)


HTMLID = sorted(JUUR.glob("*.html"))
html = {f: f.read_text(encoding="utf-8") for f in HTMLID}
css = (JUUR / "stiil.css").read_text(encoding="utf-8")
js = (JUUR / "skript.js").read_text(encoding="utf-8")

# 1. JSON-LD
for f, s in html.items():
    for plokk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        try:
            json.loads(plokk)
            ok(f"1. JSON-LD parsib: {f.name}")
        except json.JSONDecodeError as e:
            viga(f"1. JSON-LD katki failis {f.name}: {e}")

# 2. pealkirjad
for f, s in html.items():
    tasemed = [int(m) for m in re.findall(r"<h([1-6])\b", s)]
    if tasemed.count(1) != 1:
        viga(f"2. {f.name}: h1 arv on {tasemed.count(1)}")
    for a, b in zip(tasemed, tasemed[1:]):
        if b > a + 1:
            viga(f"2. {f.name}: pealkirjatase hüppab h{a} pealt h{b} peale")
    ok(f"2. {f.name}: pealkirjad korras ({''.join('h%d ' % t for t in tasemed)})")

# 3. sisemised lingid ja ankrud
for f, s in html.items():
    idd = set(re.findall(r'\sid="([^"]+)"', s))
    for href in re.findall(r'href="([^"]+)"', s):
        if href.startswith("#"):
            if href[1:] not in idd:
                viga(f"3. {f.name}: ankur {href} ei vasta ühelegi id-le")
        elif href.startswith("/"):
            tee = JUUR / href.lstrip("/")
            if not tee.exists() and not (JUUR / (href.lstrip("/") + ".html")).exists():
                viga(f"3. {f.name}: link {href} viitab puuduvale failile")
        elif href.startswith(("tel:", "mailto:", "http")):
            pass
        else:
            viga(f"3. {f.name}: kahtlane link {href}")
ok("3. lingid ja ankrud kontrollitud")

# 4. siltide tasakaal
TUHI = {"meta", "link", "img", "br", "hr", "input", "source", "area", "col", "wbr"}


class Tasakaal(HTMLParser):
    def __init__(self):
        super().__init__()
        self.pinu = []
        self.probleemid = []

    def handle_starttag(self, tag, attrs):
        if tag not in TUHI:
            self.pinu.append(tag)

    def handle_endtag(self, tag):
        if tag in TUHI:
            return
        if not self.pinu or self.pinu[-1] != tag:
            self.probleemid.append(f"ootamatu </{tag}>, pinus {self.pinu[-3:]}")
        else:
            self.pinu.pop()


for f, s in html.items():
    p = Tasakaal()
    p.feed(s)
    if p.probleemid or p.pinu:
        viga(f"4. {f.name}: sildid tasakaalust väljas {p.probleemid} {p.pinu}")
    else:
        ok(f"4. {f.name}: sildid tasakaalus")

# 5. pikk mõttekriips
for f, s in list(html.items()) + [(JUUR / "sitemap.xml", (JUUR / "sitemap.xml").read_text(encoding="utf-8"))]:
    if "—" in s:
        viga(f"5. {f.name}: sisaldab pikka mõttekriipsu")
ok("5. pikka mõttekriipsu ei ole")

# 6. koma rinnastava sidesõna ees
for f, s in html.items():
    tekst = re.sub(r"<[^>]+>", " ", s)
    for m in re.finditer(r",\s+(ja|ning|või|ega)\b", tekst):
        viga(f"6. {f.name}: koma sidesõna ees: ...{tekst[max(0,m.start()-45):m.end()+25].strip()}...")
ok("6. komareegel kontrollitud")

# 7. kohatäited
for f, s in html.items():
    for m in re.findall(r"\[[A-ZÄÖÜÕ ]{3,}\]", s):
        viga(f"7. {f.name}: kohatäide {m}")
ok("7. kohatäiteid ei ole")

# 8. reastiil
for f, s in html.items():
    if re.search(r"<[^>]*\sstyle=", s):
        viga(f"8. {f.name}: sisaldab style= atribuuti, CSP keelab selle")
ok("8. style= atribuute ei ole")

# 9 ja 10 ja 11. pildid
from struct import unpack


def webp_moodud(tee):
    b = tee.read_bytes()
    if b[12:16] == b"VP8X":
        w = int.from_bytes(b[24:27], "little") + 1
        h = int.from_bytes(b[27:30], "little") + 1
        return w, h
    if b[12:16] == b"VP8 ":
        w = unpack("<H", b[26:28])[0] & 0x3FFF
        h = unpack("<H", b[28:30])[0] & 0x3FFF
        return w, h
    if b[12:16] == b"VP8L":
        bits = int.from_bytes(b[21:25], "little")
        return (bits & 0x3FFF) + 1, ((bits >> 14) & 0x3FFF) + 1
    raise ValueError("tundmatu WebP")


viidatud = set()
for f, s in html.items():
    for m in re.finditer(r'<img[^>]*>', s):
        silt = m.group(0)
        src = re.search(r'src="([^"]+)"', silt).group(1)
        viidatud.add(src.lstrip("/"))
        tee = JUUR / src.lstrip("/")
        if not tee.exists():
            viga(f"11. {f.name}: pilt {src} puudub")
            continue
        w = re.search(r'width="(\d+)"', silt)
        h = re.search(r'height="(\d+)"', silt)
        if not w or not h:
            viga(f"9. {f.name}: pildil {src} puudub width või height")
            continue
        if tee.suffix == ".webp":
            pw, ph = webp_moodud(tee)
            if (pw, ph) != (int(w.group(1)), int(h.group(1))):
                viga(f"9. {f.name}: {src} on {pw}x{ph}, HTML ütleb {w.group(1)}x{h.group(1)}")
        if not re.search(r'alt="[^"]', silt) and 'alt=""' not in silt:
            viga(f"9. {f.name}: pildil {src} puudub alt")
    for m in re.finditer(r'srcset="([^"]+)"', s):
        for osa in m.group(1).split(","):
            viidatud.add(osa.strip().split(" ")[0].lstrip("/"))

for tee in JUUR.rglob("*.webp"):
    kb = tee.stat().st_size / 1024
    if kb > 400:
        viga(f"10. {tee} on {kb:.0f} KB, üle 400 KB")
ok("10. ükski pilt ei ole üle 400 KB")

# og:image
for f, s in html.items():
    m = re.search(r'property="og:image" content="https://vpviimistlus\.ee/([^"]+)"', s)
    if m:
        viidatud.add(m.group(1))
        if not (JUUR / m.group(1)).exists():
            viga(f"12. {f.name}: og:image fail puudub")
        else:
            ok(f"12. {f.name}: og:image on olemas")

# CSS-ist viidatud failid
for m in re.finditer(r'url\("([^"]+)"\)', css):
    viidatud.add(m.group(1).lstrip("/"))

olemas = {str(p.relative_to(JUUR)) for p in JUUR.rglob("*") if p.is_file() and p.name != ".DS_Store"}
kasutuseta = olemas - viidatud - {
    "index.html", "404.html", "robots.txt", "sitemap.xml", "_headers", "_redirects",
    "stiil.css", "skript.js", "site.webmanifest", "favicon.ico", "favicon.svg",
    "apple-touch-icon.png", "favicon-192.png", "favicon-512.png",
}
if kasutuseta:
    viga(f"11. kasutuseta failid: {sorted(kasutuseta)}")
else:
    ok("11. kasutuseta faile ei ole")

# 13. jalus
for f, s in html.items():
    jalus = s[s.find("<footer"):]
    for tykk in ("VP Viimistlus ja Puhastus OÜ", "17356505", "Mustjõe", "5858 5052", "vpviimistlusjapuhastus@gmail.com"):
        if tykk not in jalus:
            viga(f"13. {f.name}: jaluses puudub {tykk}")
ok("13. jaluses on ettevõtte andmed")


# 15. kontrast
def kanal(v):
    v /= 255
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def heledus(hex_):
    r, g, b = (int(hex_[i:i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * kanal(r) + 0.7152 * kanal(g) + 0.0722 * kanal(b)


def kontrast(a, b):
    la, lb = heledus(a), heledus(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


PAARID = [
    ("tekst paberil", "#16171f", "#f4f3f6"),
    ("vaikne paberil", "#4f5065", "#f4f3f6"),
    ("tekst kaardil", "#16171f", "#ffffff"),
    ("vaikne kaardil", "#4f5065", "#ffffff"),
    ("link paberil", "#ad1c59", "#f4f3f6"),
    ("link kaardil", "#ad1c59", "#ffffff"),
    ("silt paberil", "#ad1c59", "#f4f3f6"),
    ("nupu tekst", "#14060d", "#e95b95"),
    ("menuu tumedal", "#e8e9ef", "#0e1017"),
    ("paise alanimi", "#b9bcc9", "#0e1017"),
    ("roosa tumedal", "#e95b95", "#0e1017"),
    ("tume lahter tekst", "#c9ccd8", "#0e1017"),
    ("tume lahter sissejuhatus", "#b9bcc9", "#0e1017"),
    ("jaluse tekst", "#c9ccd8", "#0e1017"),
    ("jaluse link", "#f6c3d8", "#0e1017"),
    ("fookus paberil", "#ad1c59", "#f4f3f6"),
    ("fookus tumedal", "#e95b95", "#0e1017"),
]
for nimi, a, b in PAARID:
    k = kontrast(a, b)
    if k < 4.5:
        viga(f"15. kontrast {nimi} on {k:.2f}:1, alla 4.5")
    else:
        ok(f"15. kontrast {nimi} {k:.2f}:1")

# 17. murdepunktid
punktid = re.findall(r"@media \(max-width: (\d+)px\)", css)
ok(f"17. murdepunktid: {', '.join(punktid)} px")

# 18. fondid
if "fonts.googleapis" in css or "fonts.gstatic" in "".join(html.values()) + css:
    viga("18. font tuleb võõralt serverilt")
for fail in ("plus-jakarta-sans-latin.woff2", "plus-jakarta-sans-latin-ext.woff2"):
    if not (JUUR / "fondid" / fail).exists():
        viga(f"18. fondifail {fail} puudub")
ok("18. fondid tulevad omast kaustast")

# lisaks: CSP ja frame-src
paised = (JUUR / "_headers").read_text(encoding="utf-8")
if "youtube-nocookie" not in paised:
    viga("CSP: frame-src ei luba YouTube'i, video ei avane")
if "youtube-nocookie" not in js:
    viga("skript.js ei kasuta youtube-nocookie aadressi")
ok("CSP lubab ainult youtube-nocookie raami")

print("\n".join(teated))
print()
if vead:
    print("VEAD:")
    print("\n".join(" - " + v for v in vead))
    raise SystemExit(1)
print("Kõik kontrollid läbitud.")
