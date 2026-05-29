import requests
import xml.etree.ElementTree as ET


# Ausgabe der gefundenen Treffer
def output_xml(found_variables):

    # Schleife über alle gefundenen Bücher
    for index, book in enumerate(found_variables, start=1):

        print(f"\n{index}. Treffer")

        # Titel ausgeben
        print(f"Titel: {book['title']}")

        # Autoren ausgeben
        print("Autoren:")
        if book["authors"]:
            for author in book["authors"]:
                print(f"  - {author}")
        else:
            print("  Keine Autoren gefunden")

        # ISBNs ausgeben
        print("ISBN:")
        if book["isbns"]:
            for isbn in book["isbns"]:
                print(f"  - {isbn}")
        else:
            print("  Keine ISBN gefunden")

        # Schlagworte ausgeben
        print("Schlagworte:")
        if book["subjects"]:
            for subject in book["subjects"]:
                print(f"  - {subject}")
        else:
            print("  Keine Schlagworte gefunden")


# XML auswerten
def find_variables_xml(xml_dataset):

    # XML String in Baumstruktur umwandeln
    root = ET.fromstring(xml_dataset)

    # Namespaces
    ns = {
        "zs": "http://www.loc.gov/zing/srw/",
        "mods": "http://www.loc.gov/mods/v3"
    }

    # Liste für alle Treffer
    books = []

    # Schleife über alle records
    for record in root.findall(".//zs:record", ns):

        # MODS enthält bibliographische Daten
        mods = record.find(".//mods:mods", ns)

        # Falls kein MODS Block vorhanden
        if mods is None:
            continue

        # Titel auslesen
        title_el = mods.find(".//mods:titleInfo/mods:title", ns)
        title = title_el.text if title_el is not None else None

        # Liste für Autoren
        authors = []

        # Alle Personen durchlaufen
        for name in mods.findall(".//mods:name", ns):

            # Rolle der Person prüfen
            role = name.find(".//mods:roleTerm[@type='code']", ns)

            # Nur Autoren übernehmen
            if role is not None and role.text == "aut":

                # Namensbestandteile sammeln
                for part in name.findall(".//mods:namePart", ns):
                    if part.text:
                        authors.append(part.text)

        # Liste für ISBNs
        isbns = []

        # Alle Identifier durchsuchen
        for ident in mods.findall(".//mods:identifier", ns):

            # Nur ISBN Identifier übernehmen
            if ident.get("type") == "isbn":
                if ident.text:
                    isbns.append(ident.text)

        # Liste für Schlagworte
        subjects = []

        # Alle Schlagworte sammeln
        for sub in mods.findall(".//mods:topic", ns):
            if sub.text:
                subjects.append(sub.text)

        # Daten eines Buches speichern
        books.append({
            "title": title,
            "authors": authors,
            "isbns": isbns,
            "subjects": subjects
        })

    # Ergebnisliste zurückgeben
    return books


# XML Daten laden
def load_xml(base_url, params):

    # HTTP Anfrage senden
    response_xml = requests.get(base_url, params=params)

    # Verbindungsfehler abfangen
    if response_xml.status_code != 200:
        print("Fehler: Anfrage fehlgeschlagen (Status:", response_xml.status_code, ")")
        return None

    # UTF-8 Zeichensatz setzen
    response_xml.encoding = "utf-8"

    # XML als Text zurückgeben
    return response_xml.text


# SRU Anfrageparameter erstellen
def build_sru_url(searchnumber, searchterm):

    # Basis URL der SRU Schnittstelle
    base_url = "https://sru.k10plus.de/opac-de-627"

    # Suchfeld bestimmen
    if searchnumber == "1":
        query = "pica.per"

    elif searchnumber == "2":
        query = "pica.isb"

    elif searchnumber == "3":
        query = "pica.tit"

    # Fehlerhafte Eingabe
    else:
        print("Ungültige Eingabe")
        return None, None

    # Parameter für die SRU Anfrage
    params = {
        "version": "1.1",
        "operation": "searchRetrieve",
        "query": f"{query}={searchterm}",
        "maximumRecords": 10,
        "recordSchema": "mods"
    }

    return base_url, params


# Hauptprogramm
def main():

    print("Willkommen zur SRU Recherche GBV")

    print("\nErlaubte Eingaben: 1 (Autor), 2 ISBN) oder 3 (Titelstichwort)")

    print("\nBitte nur folgende Zahlen eingeben: 1, 2 und 3")

    # Auswahl des Suchfeldes
    searchnumber = input("Gebe jetzt eine der möglichen Zahlen ein (1, 2 oder 3):")

    # Suchbegriff eingeben
    searchterm = input("Gebe jetzt deinen Suchbegriff ein:")

    # URL und Parameter erzeugen
    base_url, params = build_sru_url(searchnumber, searchterm)

    # Falls Eingabe ungültig war
    if base_url is None:
        return

    print("\nErzeugte URL:")

    # Vollständige URL anzeigen
    print(requests.Request("GET", base_url, params=params).prepare().url)

    # XML laden
    xml_dataset = load_xml(base_url, params)
    # Verbindungsfehler abfangen
    if xml_dataset is None:
        print("Zugriffsproblem.")
        return

    # XML auswerten
    found_variables = find_variables_xml(xml_dataset)

    # Prüfen ob Treffer vorhanden sind
    if not found_variables:
        print("\nKeine Datensätze gefunden.")
        return

    # Ergebnisse ausgeben
    output_xml(found_variables)


# Programmstart
if __name__ == "__main__":
    main()
