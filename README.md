# VP Viimistlus ja Puhastus OÜ – üheleheline koduleht

Puhas HTML, CSS ja JavaScript. Ei mingit raamistikku ega ehitusprotsessi.
Majutus Cloudflare Workeri peal.

## Failid

    public/            kõik, mis brauserisse jõuab
      index.html       kogu leht
      404.html         veateade
      stiil.css        kogu kujundus
      skript.js        mobiilimenüü, galerii suurendus ja video käivitamine
      pildid/          WebP fotod, ornament ja jagamispilt
      fondid/          Plus Jakarta Sans, majutatud koos lehega
      _headers         turvapäised ja vahemälu
      _redirects       näidised, www suunamine on worker.js sees
      robots.txt
      sitemap.xml
    worker.js          www suunamine ja eelvaate noindex
    wrangler.jsonc     seadistus
    ehita.py           pilditöötlus, lähtefailidest public/pildid sisse
    kontroll.py        kontrollnimekiri koodiga
    lahtematerjal/     originaalfotod, ei lähe lehele ega Giti

## MIS TULEB ENNE AVALDAMIST ÄRA ASENDADA

1. **Domeen.** Praegu on koodis `vpviimistlus.ee`. Kui päris domeen on teine,
   vaheta see korraga ära:

       grep -rl vpviimistlus.ee public worker.js | xargs sed -i '' 's/vpviimistlus\.ee/PÄRISDOMEEN.ee/g'

   Domeen esineb kohtades: canonical, og:url, og:image, JSON-LD, robots.txt,
   sitemap.xml.

2. **Fotod.** Kõik pildid on võetud firma hange.ee profiililt. Portaal lisab
   igale pildile oma vesimärgi, `ehita.py` lõikab selle alumise 56 piksliga
   maha ja teravustab pilte kergelt. Hange.ee jagab avalikult ainult 300 px
   (`thumb`) ja 900 px (`large`) versiooni, originaalid seal kättesaadavad
   ei ole. 900 px ongi lehe fotode ülempiir.
   **Küsi kliendilt originaalfotod telefonist**, pane need `lahtematerjal/`
   kausta ja jooksuta `python3 ehita.py` uuesti. Siis kaob vajadus lõikamise
   järele ja pildid lähevad teravamaks.

3. **Logo.** Praegune logo on 218x140 pikslit, sest suuremat ei olnud saada.
   Päisesse mahub see ära, aga küsi kliendilt originaal.

## MIDA KLIENDILT VEEL KÜSIDA

Neid asju ei ole lehele kirjutatud, sest neid ei ole antud ja välja mõelda
ei tohi:

- KMKR number, kui firma on käibemaksukohustuslane
- asutamisaasta ja töötajate arv
- klientide tagasiside tsitaadid koos loaga neid avaldada
- kas hinnakiri või hinnavahemikud võiks lehele tulla
- kas Mustjõe tn 18 on vastuvõtuga aadress või ainult juriidiline aadress

## KOHALIK ARENDUS

    npx wrangler dev

Ainult see jooksutab `_headers`, `not_found_handling` ja Workeri koodi.
Tavaline staatiline server neid ei näita.

Pärast iga muudatust:

    python3 kontroll.py

Skript kontrollib JSON-LD-d, pealkirjatasemeid, katkiseid linke, siltide
tasakaalu, pikka mõttekriipsu, komareeglit, reastiile, piltide mõõte ja
suurusi, kasutuseta faile, jaluse andmeid, värvikontraste ja fonte.

## AVALDAMINE

    npx wrangler deploy

Domeen seotakse Cloudflare paneelis Workeri küljes: Workers & Pages ->
vp-viimistlus -> Settings -> Domains & Routes.

Külastajate arvestus: Cloudflare Web Analytics lülitatakse paneelist sisse.
Koodi lisada ei ole vaja ja küpsist see ei tekita.

## VIDEO

Video on YouTube'is (`F1JUho0N7ac`, konto Vilma Poolar). Leht näitab
alguses ainult eelvaatepilti. Alles klõpsu peale laeb `skript.js`
`youtube-nocookie.com` raami. Nii ei võta YouTube enne klõpsu ühendust ja
küpsiseteavitust vaja ei ole.

Kui video välja vahetatakse, muuda `data-video` väärtust `index.html` sees
ja tee uus eelvaatepilt: pane uus pisipilt `lahtematerjal/` kausta nimega
`youtube-kapitaalremont-maxres.jpg` ja jooksuta `ehita.py`.

## MÄRKUSED

- Content-Security-Policy on range. Ainus lubatud võõras allikas on
  `frame-src https://www.youtube-nocookie.com`. Reastiil `style="..."` on
  keelatud, kogu kujundus peab olema `stiil.css` sees.
- Kontaktivormi lehel ei ole, seega privaatsuslehte ei ole vaja. Kui vorm
  hiljem lisatakse, tuleb ka `privaatsus.html` teha.
- `ehita.py` on korduv: kaks käivitust annavad baidi pealt sama tulemuse.
