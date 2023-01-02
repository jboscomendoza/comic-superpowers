import requests

# Refs
# https://www.mediawiki.org/wiki/Wikibase/API
# https://www.mediawiki.org/wiki/API:Presenting_Wikidata_knowledge#Parsing_claims
# https://www.wikidata.org/w/api.php?action=help&modules=wbgetentities

base_url = "http://www.wikidata.org/w/api.php?{params}&format=json"
params_query = "action=query&list=search&srsearch=Jubilee Marvel"
query_url = base_url.format(params=params_query)

resp_query = requests.get(query_url)

query_json = resp_query.json()

results = []

for i in query_json["query"]["search"]:
   results.append(dict(title=i["title"], pagid=i["pageid"]))
   
char_id = results[0]["title"]
params_get = "action=wbgetentities&sites=wikidatawiki&languages=es&props=aliases|claims|sitelinks&sitefilter=eswiki&ids={}".format(char_id)
char_url = base_url.format(params=params_get)


resp_char = requests.get(char_url)
resp_dat = resp_char.json()

char_id = resp_dat["entities"][char_id]["id"]
char_title = resp_dat["entities"][char_id]["sitelinks"]["eswiki"]["title"]

# Prop id
claims = {
    "genero":"P21",
    "superpoder":"P2563",
    "membresia":"P463",
    "universo":"P1080"
    }

char_claims = []

for claim in claims.values():
    snaks = resp_dat["entities"][char_id]["claims"].get(claim)
    for snak in snaks:
        key_info = {
            "property":snak["mainsnak"]["property"],
            "id":snak["mainsnak"]["datavalue"]["value"]["id"]
        }
        char_claims.append(key_info)