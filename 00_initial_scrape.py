import requests

# Refs
# https://www.mediawiki.org/wiki/Wikibase/API
# https://www.mediawiki.org/wiki/API:Presenting_Wikidata_knowledge#Parsing_claims
# https://www.wikidata.org/w/api.php?action=help&modules=wbgetentities

search_term = "Jubilee Marvel"

base_url = "http://www.wikidata.org/w/api.php?format=json"
query_params = "&action=query&list=search&srsearch="
query_url = base_url + query_params + search_term

params_str = (
    "&action=wbgetentities" +
    "&sites=wikidatawiki" +
    "&languages=es" +
    "&languagefallback=true" +
    "&sitefilter=eswiki" +
    "&ids="
    )

claims = {
    "genero":"P21",
    "superpoder":"P2563",
    "membresia":"P463",
    "universo":"P1080"
    }

resp_query = requests.get(query_url)

query_json = resp_query.json()

results = []

for i in query_json["query"]["search"]:
   results.append(dict(title=i["title"], pagid=i["pageid"]))

char_id    = results[0]["title"]
char_url   = base_url + params_str + char_id
char_resp  = requests.get(char_url)
char_json  = char_resp.json()
char_title = char_json["entities"][char_id]["sitelinks"]["eswiki"]["title"]
char_claims = []


for claim in claims.values():
    snaks = char_json["entities"][char_id]["claims"].get(claim)
    for snak in snaks:
        key_info = {
            snak["mainsnak"]["property"]: snak["mainsnak"]["datavalue"]["value"]["id"]
        }
        char_claims.append(key_info)
    
sp_value = []

for i in char_claims:
    sp_id = i.get(claims["superpoder"])
    if sp_id is not None:
        sp_value.append(sp_id)

sp_id = "|".join(sp_value)
sp_url = base_url + params_str + sp_id
sp_resp = requests.get(sp_url)
sp_json = sp_resp.json()
sp_data = sp_json["entities"][sp_id]["labels"]["es"]["value"]
sp_desc = sp_json["entities"][sp_id]["descriptions"]["es"]["value"]