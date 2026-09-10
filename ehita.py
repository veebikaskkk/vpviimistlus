#!/usr/bin/env python3
"""Pilditöötlus VP Viimistlus ja Puhastus OÜ kodulehele.

Lähtefailid on kaustas lahtematerjal/, valmis failid lähevad public/pildid/.
Skript on korratav: kaks käivitust annavad baidi pealt sama tulemuse.

Kasutus:  python3 ehita.py
"""

from PIL import Image, ImageDraw, ImageFilter, ImageOps
from pathlib import Path

LAHE = Path("lahtematerjal")
VALJUND = Path("public/pildid")

# Hange.ee lisab oma vaates igale pildile alumisse serva vesimärgi:
# vasakule "Hange.ee" logo ja paremale firma embleemi. Mõlemad jäävad
# alumise 52 piksli sisse, 4 pikslit on varuks. Riba lõigatakse maha,
# sest kliendi enda lehele see ei kuulu.
VESIMARK_KORGUS = 56

TUME = (11, 14, 20)
ROOSA = (233, 91, 149)
VALGE = (255, 255, 255)

# lähtefail, väljundnimi, maksimumlaius
GALERII = [
    ("siseviimistlustood-71611", "fototapeet-metsamotiiviga-elutoas", 900),
    ("siseviimistlustood-71610", "fototapeet-ornamendiga-magamistoas", 900),
    ("korterite-remont-71612", "korteri-remont-enne-ja-parast", 900),
    ("maalritood-71605", "toa-ettevalmistus-varvimiseks", 900),
    ("siseviimistlustood-71609", "fototapeet-lastetoa-seinal", 900),
    ("maalritood-71602", "maalritood-enne-ja-parast", 900),
    ("korterite-remont-71604", "varvitud-seinte-ja-laega-tuba", 900),
    ("korterite-remont-71603", "seinakarkass-korteri-remondil", 900),
    ("puhastusteenused-71592", "vannitoa-puhastus-enne-ja-parast", 900),
    ("puhastusteenused-71600", "koristatud-koogi-tooplaan", 900),
    ("puhastusteenused-71601", "puhastatud-aken-parast-remonti", 900),
]

HERO = "fototapeet-metsamotiiviga-elutoas"


def ava(nimi):
    tee = LAHE / f"vp-viimistlus-ja-puhastus-{nimi}.jpg"
    pilt = ImageOps.exif_transpose(Image.open(tee)).convert("RGB")
    laius, korgus = pilt.size
    pilt = pilt.crop((0, 0, laius, korgus - VESIMARK_KORGUS))
    # Hange.ee on pildid korduvalt JPEG-iks pakkinud ja need on pehmed.
    # Kerge teravustus toob servad tagasi, suurem tekitaks halosid.
    return pilt.filter(ImageFilter.UnsharpMask(radius=1.2, percent=55, threshold=2))


def salvesta(pilt, nimi, max_laius, kvaliteet=84):
    """Uut Image objekti salvestades kaob EXIF ja sellega ka GPS."""
    if pilt.width > max_laius:
        korgus = round(pilt.height * max_laius / pilt.width)
        pilt = pilt.resize((max_laius, korgus), Image.LANCZOS)
    tee = VALJUND / f"{nimi}.webp"
    puhas = Image.new("RGB", pilt.size)
    puhas.putdata(list(pilt.getdata()))
    puhas.save(tee, "WEBP", quality=kvaliteet, method=6)
    suurus = tee.stat().st_size
    while suurus > 400_000 and puhas.width > 400:
        uus = int(puhas.width * 0.85)
        puhas = puhas.resize((uus, round(puhas.height * uus / puhas.width)), Image.LANCZOS)
        puhas.save(tee, "WEBP", quality=kvaliteet, method=6)
        suurus = tee.stat().st_size
    print(f"{tee.name:44} {puhas.width:4}x{puhas.height:<4} {suurus/1024:7.1f} KB")
    return puhas.size


def logo():
    """Hange.ee profiililt saadud logo. Ümber on valge ääris, see lõigatakse maha.
    Lähtefail on 218x140, seega päris väike. Suuremat ei ole."""
    pilt = Image.open(LAHE / "c8a6a8142bce55301d5b23ec736aa36c.jpg").convert("RGB")
    return salvesta(pilt.crop((35, 0, 183, 140)), "vp-viimistlus-logo", 148, kvaliteet=90)


def video_kaas():
    """YouTube eelvaatepilt. Video on püstine, servades on hägune täide.
    Lõikame välja ainult päris kaadri."""
    pilt = Image.open(LAHE / "youtube-kapitaalremont-maxres.jpg").convert("RGB")
    kaader = pilt.crop((438, 0, 843, 720))
    return salvesta(kaader, "video-kapitaalremont-eelvaade", 405)


def jagamispilt(hero_fail):
    """og:image 1200x630, tume kate ja firma nimi."""
    foto = Image.open(hero_fail).convert("RGB")
    suhe = max(1200 / foto.width, 630 / foto.height)
    foto = foto.resize((round(foto.width * suhe), round(foto.height * suhe)), Image.LANCZOS)
    x = (foto.width - 1200) // 2
    y = (foto.height - 630) // 2
    laud = foto.crop((x, y, x + 1200, y + 630))

    kate = Image.new("RGB", (1200, 630), TUME)
    laud = Image.blend(laud, kate, 0.62)

    joonis = ImageDraw.Draw(laud)
    joonis.rectangle([(0, 0), (1200, 10)], fill=ROOSA)

    from PIL import ImageFont
    def font(suurus, paks=True):
        for tee in ("/System/Library/Fonts/Supplemental/Arial Bold.ttf" if paks
                    else "/System/Library/Fonts/Supplemental/Arial.ttf",
                    "/System/Library/Fonts/Helvetica.ttc",
                    "/Library/Fonts/Arial.ttf"):
            try:
                return ImageFont.truetype(tee, suurus)
            except OSError:
                continue
        return ImageFont.load_default(suurus)

    joonis.text((80, 210), "VP Viimistlus", font=font(86), fill=VALGE)
    joonis.text((80, 310), "ja Puhastus OÜ", font=font(86), fill=ROOSA)
    joonis.text((80, 440), "Siseviimistlus, remont ja puhastus üle Eesti",
                font=font(34, paks=False), fill=(226, 226, 232))

    tee = VALJUND / "vp-viimistlus-jagamispilt.webp"
    laud.save(tee, "WEBP", quality=82, method=6)
    print(f"{tee.name:44} 1200x630  {tee.stat().st_size/1024:7.1f} KB")


def favicon():
    """Lihtne märk: tume ruut, roosa VP. Logo ise on liiga peen 32 piksli sees."""
    from PIL import ImageFont
    def font(suurus):
        for tee in ("/System/Library/Fonts/Supplemental/Arial Bold.ttf",
                    "/System/Library/Fonts/Helvetica.ttc"):
            try:
                return ImageFont.truetype(tee, suurus)
            except OSError:
                continue
        return ImageFont.load_default(suurus)

    def mark(kulg):
        pilt = Image.new("RGB", (kulg * 4, kulg * 4), TUME)
        joonis = ImageDraw.Draw(pilt)
        joonis.text((kulg * 2, kulg * 2), "VP", font=font(int(kulg * 2.1)),
                    fill=ROOSA, anchor="mm")
        return pilt.resize((kulg, kulg), Image.LANCZOS)

    juur = Path("public")
    mark(180).save(juur / "apple-touch-icon.png")
    mark(192).save(juur / "favicon-192.png")
    mark(512).save(juur / "favicon-512.png")
    mark(64).save(juur / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    print("faviconid valmis")


def main():
    VALJUND.mkdir(parents=True, exist_ok=True)
    moodud = {}
    for lahe, nimi, laius in GALERII:
        moodud[nimi] = salvesta(ava(lahe), nimi, laius)
    # hero vajab ka väiksemat varianti, et mobiil ei laeks arvutiversiooni
    moodud[HERO + "-640"] = salvesta(ava("siseviimistlustood-71611"), HERO + "-640", 640)
    moodud["logo"] = logo()
    moodud["video"] = video_kaas()
    jagamispilt(VALJUND / f"{HERO}.webp")
    favicon()

    print("\nHTML jaoks width ja height:")
    for nimi, (w, h) in sorted(moodud.items()):
        print(f'  {nimi}: width="{w}" height="{h}"')


if __name__ == "__main__":
    main()
