from lodstorage.sparql import SPARQL
import ssl
import json
from urllib.error import HTTPError
from urllib.request import urlopen
import requests
from PIL import Image
import time


lst = [1, 2, 3, 4, 5, 6, 7, 8, 9]

zoekterm = ""

def iiifmanifest():
    ssl._create_default_https_context = ssl._create_unverified_context
    global zoekterm
    zoekterm = input("Wat zoek je? ")

    print(time.perf_counter())

    sparqlQuery = """
     PREFIX cidoc: <http://www.cidoc-crm.org/cidoc-crm/>
     SELECT DISTINCT ?o ?title WHERE {
     ?object cidoc:P129i_is_subject_of ?o .
     ?object cidoc:P102_has_title ?title.
     FILTER (regex(?title, "%s" , "i"))
     BIND(RAND() AS ?random) .
     } ORDER BY ?random
     LIMIT 1000
     """ % (zoekterm,)

    c = 0
    sparql = SPARQL("https://stad.gent/sparql")
    qlod = sparql.queryAsListOfDicts(sparqlQuery)
    print(time.perf_counter())
    print(qlod)
    print(str(len(qlod)) + " gevonden objecten")
    if len(qlod) < 9:
        print("Te weinig objecten in de Collectie van de Gentenaar met dit woord in de titel :(. Probeer het opnieuw!")
        iiifmanifest()
        return
    else:
        for i in range(0, len(qlod)):
            if i == 20:
                ## nog op te lossen, i == len(qlod) werkt niet :(
                print(
                    "ERROR: te weinig publieke manifesten. Helaas! Er zijn te weinig objecten in de Collectie van de Gentenaar met dit woord in de titel :(. Probeer het opnieuw!")
                iiifmanifest()
                return

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
                prentje = requests.get(afbeelding).content
                with open(str(lst[c]) + '.jpg', 'wb') as handler:
                    handler.write(prentje)
                manifestje = data_json["@id"]
                objectnummer = manifestje.rpartition('/')[2]
                webplatform = "https://data.collectie.gent/entity/" + objectnummer
                print(webplatform)
                print(time.perf_counter())
                print("na downloaden beeld " + str(lst[c]))
                c += 1

            if c == 9:
                collagemaker()


def collagemaker():
    collage = Image.new("RGBA", (1500, 1500), color=(255, 255, 255, 255))


    d = 0

    for h in range(0, 1500, 500):
        for j in range(0, 1500, 500):
            file = str(lst[d]) + ".jpg"
            photo = Image.open(file).convert("RGBA")
            photo = photo.resize((500, 500))

            collage.paste(photo, (h, j))
            d += 1
    print("collage klaar ")
    collage.show()
    print(time.perf_counter())
    collage.save(f"{zoekterm}.png")


iiifmanifest()





