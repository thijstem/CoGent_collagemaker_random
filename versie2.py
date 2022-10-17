import pandas as pd
from lodstorage.sparql import SPARQL
from lodstorage.csv import CSV
import ssl
import json
from urllib.error import HTTPError
from urllib.request import urlopen
import requests
from PIL import Image, ImageEnhance

zoekterm = input("Wat zoek je? ")

lst = [1, 2, 3, 4, 5, 6, 7, 8, 9]


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
     LIMIT 100
     """ % (zoekterm,)

    c = 0
    sparql = SPARQL("https://stad.gent/sparql")
    qlod = sparql.queryAsListOfDicts(sparqlQuery)
    print(qlod)
    for i in range(0, len(qlod)):
        try:
            response = urlopen(qlod[i]['o'])
        except ValueError:
            pass
        except HTTPError:
            pass
        else:
            data_json = json.loads(response.read())
            afbeelding = data_json["sequences"][0]['canvases'][0]["images"][0]["resource"]["@id"]
            afbeelding = afbeelding.replace("full/full/0/default.jpg", "square/500,/0/default.jpg")
            #df_sparql.loc[i, "afbeeldingen"] = afbeelding
            print(str(lst[c]) + " afbeelding(en) gedownload")
            prentje = requests.get(afbeelding).content
            with open(str(lst[c]) + '.jpg', 'wb') as handler:
                handler.write(prentje)
            c += 1
        if c == 9:
            break


iiifmanifest()


collage = Image.new("RGBA", (1500, 1500), color=(255, 255, 255, 255))


d = 0

for i in range(0, 1500, 500):
    for j in range(0, 1500, 500):
        file = str(lst[d]) + ".jpg"
        photo = Image.open(file).convert("RGBA")
        photo = photo.resize((500, 500))

        collage.paste(photo, (i, j))
        d += 1
collage.show()
collage.save(f"{zoekterm}.png")





