# Naputak

Navedena skripta prolazi kroz sve `.json` datoteke koje se nalaze
u trenutnom radnom direktoriju. Za svaku datoteku, provjerava
postoji podatak o završnom sniku zaslona koji je generirao alat
"Lighthouse". Ako pronađe takav podatak, izvlači snimku zaslona iz
podataka o snimku i pohranjuje kao `.jpeg` sliku u poddirektorij
`/screeenshots` s istim imenom kao i originalna json datoteka, ali
s dodatkom `_screenshot` u imenu.

## Funkcionalnost

Skripta koristi funkciju `save_image` kako bi dekodirala base64
kodiranu sliku iz json podataka i spremila je kao slikovnu datoteku
u png formatu. Nakon obrade svih json datoteka, skripta ispisuje
poruke o tome je li pronašla i pohranila snimak zaslona za svaku
datoteku ili ne.

### Dodatna funkcionalnost

Skripta nakon pohranjivanja snimke zaslona (u `.png` formatu), pohranjuje sve podatke o bojama (rgb vrijednost)
u zajedničku json datoteku (unutar `/colors-json` poddirektorija u `all_sites_color_analysis.json`), gdje se mogu vidjeti
podaci o identifikatoru, nazivu datoteke i njezinim svojstvama boje.

### Nova skripta (`skripta03.py`)

Nova skripta `skripta03.py` analizira sve `.json` datoteke i izvlači podatke HTTPS, Viewport, FCP, LCP, Speed Index, TBT, CLS, TTI, FMP, Max Potential FID, Server Response Time, Javascript Execution Time, Critical Request Chains, Number of Network Requests, Console Errors, Responsive Images, Correct Aspect Ratio, Preload Key Requests, Preconnect Suggestions. Navedene podatke sprema unutar poddirektorija `/analyzed-json`.

### Nova skripta (`skripta01.py`)

Nova skripta `skripta01.py` analizira slike (`.png` format) gdje pronalazi postotak i zasićenost bijele boje u svakoj slici i potom raspoređuje svaku sliku na temelju prisutstva bijele boje u `light-photos/` poddirektorij ili `dark-photos/` poddirektorij.
