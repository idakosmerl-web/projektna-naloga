import re
import os

import pandas as pd
import requests
from bs4 import BeautifulSoup


url = "https://www.boxofficemojo.com/date/?ref_=bo_nb_in_tab"

# Mape za shranjevanje podatkov
os.makedirs("podatki", exist_ok=True)
os.makedirs("original_spletne_strani", exist_ok=True)

with open("original_spletne_strani/boxofficemojo_dnevna_2026-08-25.html", "r", encoding="utf-8") as datoteka:
    html = datoteka.read()

soup = BeautifulSoup(html, "html.parser")


# Pridobivanje podatkov iz glavne spletne strani
tabela = soup.find("table")
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


for vrstica in vrstice:
    celice = vrstica.find_all(["th", "td"])

    vrstica_podatkov = []

    for celica in celice:
        vrstica_podatkov.append(celica.get_text(strip=True))

    if vrstica_podatkov:
        podatki.append(vrstica_podatkov)

df = pd.DataFrame(podatki[1:], columns=podatki[0])

df = df[["Date", "#1 Release", "Gross"]]

# Čiščenje podatkov
df = df.rename(columns={
    "Date": "datum",
    "#1 Release": "naslov",
    "Gross": "dnevni zaslužek"})

df["datum"] = df["datum"].str.extract(r"^([A-Z][a-z]{2} \d{1,2})")

df["dnevni zaslužek"] = (
    df["dnevni zaslužek"]
    .str.replace("$", "")
    .str.replace(",", "")
    .astype(int))

df.to_csv("podatki/dnevni_podatki.csv", index=False, encoding="utf-8-sig")


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
    "Sport": "športni"}


def prevedi_zanre(zanri):
    seznam_zanrov = zanri.split(", ")
    prevedeni = []

    for zanr in seznam_zanrov:
        if zanr in prevod_zanrov:
            prevedeni.append(prevod_zanrov[zanr])
        else:
            prevedeni.append(zanr)

    return ", ".join(prevedeni)


# Podstrani
def pridobi_podatek(soup, ime):
    najdeno = soup.find(string=lambda tekst: tekst and ime in tekst)

    span = najdeno.parent.find_next_sibling("span")

    if ime == "Distributor":
        return next(span.stripped_strings)


    if ime == "Release Date":
        datum = span.get_text(" ", strip=True)
        najden_datum = re.search(r"[A-Z][a-z]{2} \d{1,2}, \d{4}", datum)
        if najden_datum:
            return najden_datum.group(0)
        return datum

    
    vrednost = span.get_text(" ", strip=True)

    if ime == "Genres":
        vrednosti = vrednost.split()
        return ", ".join(vrednosti)

    return vrednost



podatki_filmi = []

for _, vrstica in filmi_df.iterrows():
    naslov = vrstica["naslov"]
    povezava = vrstica["povezava"]


    url_filma = "https://www.boxofficemojo.com" + povezava
    odziv_filma = requests.get(url_filma)
    soup_filma = BeautifulSoup(odziv_filma.text, "html.parser")


    distributer = pridobi_podatek(soup_filma, "Distributor")
    running_time = pridobi_podatek(soup_filma, "Running Time")
    genres = pridobi_podatek(soup_filma, "Genres")
    datum_izida = pridobi_podatek(soup_filma, "Release Date")


    genres = prevedi_zanre(genres)

    podatki_filmi.append({
        "naslov": naslov,
        "distributer": distributer,
        "trajanje": running_time,
        "žanri": genres,
        "datum izida": datum_izida})
    

filmi_podatki_df = pd.DataFrame(podatki_filmi)


st_dni_na_1_mestu = df["naslov"].value_counts()
filmi_podatki_df["št. dni na 1. mestu"] = (filmi_podatki_df["naslov"].map(st_dni_na_1_mestu).astype(int))


najvecji_dnevni_zasluzek = df.groupby("naslov")["dnevni zaslužek"].max()
filmi_podatki_df["največji dnevni zaslužek"] = (filmi_podatki_df["naslov"].map(najvecji_dnevni_zasluzek))


filmi_podatki_df.to_csv("podatki/seznam_filmov_dopolnjeno.csv", index=False, encoding="utf-8-sig")



print("\nUSTVARJENE DATOTEKE IN NJIHOVE VELIKOSTI:")

print("seznam_filmov.csv:", filmi_df.shape)
print("Stolpci:", list(filmi_df.columns))

print("\ndnevni_podatki.csv:", df.shape)
print("Stolpci:", list(df.columns))

print("\nseznam_filmov_dopolnjeno.csv:", filmi_podatki_df.shape)
print("Stolpci:", list(filmi_podatki_df.columns))

print("\nZAJEM PODATKOV JE USPEŠNO ZAKLJUČEN")
