import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import re


# Spletna stran, s katere zajemamo podatke
url = "https://www.boxofficemojo.com/date/?ref_=bo_nb_in_tab"

# Zajem spletne strani
odziv = requests.get(url)

# Ustvarimo mapo za shranjevanje podatkov
os.makedirs("podatki", exist_ok=True)
# Ustvarimo mapo za shranjevanje originalnih spletnih strani
os.makedirs("original_spletne_strani", exist_ok=True)

# Shranimo originalni HTML
with open(
    "original_spletne_strani/boxofficemojo_dnevna_2026-08-25.html",
    "r",
    encoding="utf-8"
) as datoteka:
    html = datoteka.read()

# Preberemo shranjeni HTML
with open(
    "original_spletne_strani/boxofficemojo_dnevna_2026-08-25.html",
    "r",
    encoding="utf-8"
) as datoteka:
    html = datoteka.read()

soup = BeautifulSoup(html, "html.parser")

# Poiščemo tabelo
tabela = soup.find("table")

# Iz tabele preberemo vse vrstice
vrstice = tabela.find_all("tr")

podatki = []
filmi = []
for vrstica in vrstice[1:]:
    celice = vrstica.find_all(["th", "td"])

    film = celice[7]
    naslov = film.get_text(strip=True)

    povezava = film.find("a")

    if povezava:
        url_filma = povezava.get("href")
        filmi.append([naslov, url_filma])

filmi_df = pd.DataFrame(filmi, columns=["naslov", "povezava"])

filmi_df = filmi_df.drop_duplicates(subset="naslov")
filmi_df.to_csv("podatki/seznam_filmov.csv", index=False, encoding="utf-8-sig")

print("\nFILMI IN POVEZAVE:")
print(filmi_df)

print("\nŠtevilo različnih filmov:", len(filmi_df))

for vrstica in vrstice:
    celice = vrstica.find_all(["th", "td"])

    vrstica_podatkov = []

    for celica in celice:
        vrstica_podatkov.append(celica.get_text(strip=True))

    if vrstica_podatkov:
        podatki.append(vrstica_podatkov)

# Prvo vrstico uporabimo kot imena stolpcev
df = pd.DataFrame(podatki[1:], columns=podatki[0])

print("\nIZVORNI STOLPCI:")
print(df.columns)

# Obdržimo samo stolpce, ki jih potrebujemo
df = df[["Date", "#1 Release", "Gross"]]

# Slovenska imena stolpcev
df = df.rename(columns={
    "Date": "datum",
    "#1 Release": "naslov",
    "Gross": "dnevni zaslužek"
})

# Odstranimo $ in vejice ter zaslužek pretvorimo v število
df["dnevni zaslužek"] = (
    df["dnevni zaslužek"]
    .str.replace("$", "", regex=False)
    .str.replace(",", "", regex=False)
    .astype(int)
)

df.to_csv(
    "podatki/dnevni_podatki.csv",
    index=False,
    encoding="utf-8-sig"
)

# Izpis končne tabele
print("\nKONČNA TABELA:")
print(df.head())

# Število vseh vrstic
print("\nŠtevilo vrstic:", len(df))

# Število različnih filmov
print("Število različnih filmov:", df["naslov"].nunique())

# Tipi podatkov
print("\nKONČNI TIPI PODATKOV:")
print(df.dtypes)

prevod_zanrov = {
    "Action": "akcijski",
    "Adventure": "pustolovski",
    "Sci-Fi": "znanstvenofantastični",
    "Comedy": "komedija",
    "Drama": "drama",
    "Horror": "grozljivka",
    "Thriller": "triler",
    "Romance": "romantični",
    "Animation": "animirani",
    "Fantasy": "fantazijski",
    "Crime": "kriminalni",
    "Mystery": "skrivnostni",
    "Family": "družinski",
    "Musical": "muzikal",
    "War": "vojni",
    "Western": "vestern",
    "Biography": "biografski",
    "History": "zgodovinski",
    "Music": "glasbeni",
    "Sport": "športni"
}

def prevedi_zanre(zanri):
    seznam_zanrov = zanri.split(", ")

    prevedeni = []

    for zanr in seznam_zanrov:
        if zanr in prevod_zanrov:
            prevedeni.append(prevod_zanrov[zanr])
        else:
            prevedeni.append(zanr)

    return ", ".join(prevedeni)

def pridobi_podatek(soup, ime):
    najdeno = soup.find(
        string=lambda tekst: tekst and ime in tekst
    )

    span = najdeno.parent.find_next_sibling("span")

    # Distributer – vzamemo samo prvo besedilo
    if ime == "Distributor":
        return span.stripped_strings.__iter__().__next__().strip()

    # Datum izida – vzamemo samo prvi datum in odstranimo dodatno besedilo
    if ime == "Release Date":
        datum = span.get_text(" ", strip=True)
        najden_datum = re.search(r"[A-Z][a-z]{2} \d{1,2}, \d{4}", datum)
        if najden_datum:
            return najden_datum.group(0)
        return datum
    
    # Ostali podatki
    vrednost = span.get_text(" ", strip=True)

    # Žanre ločimo z vejico
    if ime == "Genres":
        vrednosti = vrednost.split()
        return ", ".join(vrednosti)

    return vrednost


podatki_filmi = []

for _, vrstica in filmi_df.iterrows():

    naslov = vrstica["naslov"]
    povezava = vrstica["povezava"]

    # Sestavimo URL podstrani filma
    url_filma = "https://www.boxofficemojo.com" + povezava

    # Zajamemo podstran
    odziv_filma = requests.get(url_filma)

    soup_filma = BeautifulSoup(
        odziv_filma.text,
        "html.parser"
    )

    # Pridobimo podatke
    distributer = pridobi_podatek(
        soup_filma, "Distributor"
    )

    running_time = pridobi_podatek(
        soup_filma, "Running Time"
    )

    genres = pridobi_podatek(
        soup_filma, "Genres"
    )

    datum_izida = pridobi_podatek(
        soup_filma, "Release Date"
    )

    # Prevedemo žanre
    genres = prevedi_zanre(genres)

    # Podatke dodamo v seznam
    podatki_filmi.append({
        "naslov": naslov,
        "distributer": distributer,
        "trajanje": running_time,
        "žanri": genres,
        "datum izzida": datum_izida
    })
    

# Ustvarimo tabelo iz zbranih podatkov
filmi_podatki_df = pd.DataFrame(podatki_filmi)

# Število dni, ko je bil film na 1. mestu
st_dni_na_1_mestu = df["naslov"].value_counts()

# Največji dnevni zaslužek posameznega filma
najvecji_dnevni_zasluzek = df.groupby("naslov")["dnevni zaslužek"].max()

# Dodamo podatke v tabelo filmov
filmi_podatki_df["št. dni na 1. mestu"] = (
    filmi_podatki_df["naslov"].map(st_dni_na_1_mestu).fillna(0).astype(int)
)

filmi_podatki_df["največji dnevni zaslužek"] = (
    filmi_podatki_df["naslov"].map(najvecji_dnevni_zasluzek)
)


# Shranimo tabelo filmov v CSV
os.makedirs("podatki", exist_ok=True)

filmi_podatki_df.to_csv(
    "podatki/seznam_filmov_dopolnjeno.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\nPREGLED TABELE FILMOV:")
print(filmi_podatki_df.info())

print("\nMANJKAJOČE VREDNOSTI:")
print(filmi_podatki_df.isna().sum())

print("\nOSNOVNA STATISTIKA:")
print(filmi_podatki_df.describe())

print("\nSTOLPCI TABELE FILMOV:")
print(filmi_podatki_df.columns)