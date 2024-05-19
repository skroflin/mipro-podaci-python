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
u jpeg formatu. Nakon obrade svih json datoteka, skripta ispisuje
poruke o tome je li pronašla i pohranila snimak zaslona za svaku
datoteku ili ne.
