# Opis projekta

Projektna naloga obravnava zajem in analizo podatkov o filmih s spletne strani Box Office Mojo med 1. januarjem 2026 in 23. avgustom 2026. Podatki o dnevnih zaslužkih in filmih so zajeti, predelani in shranjeni v CSV datoteke, nato pa analizirani s knjižnico pandas in predstavljeni z grafi v Jupyter Notebooku. Za posamezne filme so dodatno pridobljeni podatki o naslovu, distributerju, trajanju, žanrih, datumu izida, številu dni na 1. mestu ter največjem dnevnem zaslužku. 

Namen projekta je s pomočjo zbranih podatkov odgovoriti na zastavljena raziskovalna vprašanja ter ugotoviti, ali so izbrane značilnosti filmov povezane z njihovim zaslužkom in uspešnostjo.

# Uporaba
Za ponovno izvedbo zajema podatkov zaženite `zajem_podatkov.py`. Program uporabi shranjeno izvorno HTML stran, ker se sicer originalna spletna stran dnevno posodablja, ter pridobi in obdela podatke o filmih.
Rezultate shrani v mapo `podatki`.

Nato za ogled rezultatov odprite datoteko `analiza_podatkov.ipynb` in zaženite celice v Jupyter Notebooku. Notebook vsebuje raziskovalna vprašanja, analizo podatkov, tabele, grafe in ugotovitve.

# Datoteke
1. `zajem_podatkov.py` – program za zajem in predelavo podatkov
2. `analiza_podatkov.ipynb` – analiza podatkov, vizualizacije in ugotovitve
3. `podatki` – mapa z ustvarjenimi CSV datotekami
4. `original_spletne_strani` – mapa s shranjeno izvorno HTML stranjo

