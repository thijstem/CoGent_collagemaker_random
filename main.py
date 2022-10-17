import pandas as pd
from lodstorage.sparql import SPARQL
from lodstorage.csv import CSV
import ssl
import json
from urllib.error import HTTPError
from urllib.request import urlopen
import requests
from PIL import Image
import time

time.perf_counter()

zoekterm = input("Wat zoek je? ")

def iiifmanifest():
    ssl._create_default_https_context = ssl._create_unverified_context



    sparqlQuery = """
    PREFIX cidoc: <http://www.cidoc-crm.org/cidoc-crm/>
    SELECT ?o ?title WHERE {
    ?object cidoc:P129i_is_subject_of ?o .
    ?object cidoc:P102_has_title ?title.
    FILTER (regex(?title, "%s" , "i"))
    BIND(RAND() AS ?random) .
    } ORDER BY ?random
    LIMIT 1
    """ %(zoekterm, )

    df_sparql = pd.DataFrame()
    sparql = SPARQL("https://stad.gent/sparql")
    qlod = sparql.queryAsListOfDicts(sparqlQuery)
    csv = CSV.toCSV(qlod)


    df_result = pd.DataFrame([x.split(',') for x in csv.split('\n')])
    df_sparql = df_sparql.append(df_result, ignore_index=True)
    df_sparql[0] = df_sparql[0].str.replace(r'"', '')
    df_sparql[0] = df_sparql[0].str.replace(r'\r', '')

    iiifmanifest = df_sparql[0].iloc[1]
    return iiifmanifest

def image():
    manifest = iiifmanifest()
    try:
        response = urlopen(manifest)
    except ValueError:
        return image()
    except HTTPError:
        return image()
    else:
        data_json = json.loads(response.read())
        afbeelding = data_json["sequences"][0]['canvases'][0]["images"][0]["resource"]["@id"]
        #afbeelding = afbeelding.replace("full/full/0/default.jpg","square/400,/0/default.jpg")
        manifestje = data_json["@id"]
        objectnummer = manifestje.rpartition('/')[2]
        webplatform = "https://data.collectie.gent/entity/" + objectnummer
        print(webplatform)
        return afbeelding

lst = [1, 2, 3, 4, 5, 6, 7, 8, 9]

for i in lst:
    afbeelding = image()
    prentje = requests.get(afbeelding).content
    print(time.perf_counter())
    print("na " + str(i) + " ophalen")
    with open(str(i)+'.jpg', 'wb') as handler:
        handler.write(prentje)
    print(time.perf_counter())
    print("na " + str(i) + " downloaden")

collage = Image.new("RGBA", (1500, 1500), color=(255, 255, 255, 255))


c = 0
for i in range(0, 1500, 500):
    for j in range(0, 1500, 500):
        file = str(lst[c]) + ".jpg"
        photo = Image.open(file).convert("RGBA")
        photo = photo.resize((500, 500))

        collage.paste(photo, (i, j))
        c += 1
collage.show()
collage.save(f"{zoekterm}.png")
print(time.perf_counter())

##snelheid: gaat supersnel eenmaal goede url er is om te downloaden // ik denk dat urlopen langste duurt

## hoe verbeteren? sneller, zoeken in beschrijvingen, zorgen dat hij opnieuw start als beeld er al is