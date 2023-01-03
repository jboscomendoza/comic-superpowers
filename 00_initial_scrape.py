import requests

# Refs
# https://www.mediawiki.org/wiki/Wikibase/API
# https://www.mediawiki.org/wiki/API:Presenting_Wikidata_knowledge#Parsing_claims
# https://www.wikidata.org/w/api.php?action=help&modules=wbgetentities

BASE_URL = "http://www.wikidata.org/w/api.php?format=json"

QUERY_PARAMS = "&action=query&list=search&srsearch="

ENTITIES_PARAMS = (
    "&action=wbgetentities" +
    "&sites=wikidatawiki" +
    "&languages=es" +
    "&languagefallback=true" +
    "&sitefilter=eswiki" +
    "&ids="
    )

CLAIMS = {
    "genero":"P21",
    "superpoder":"P2563",
    "membresia":"P463",
    "universo":"P1080"
    }


def get_query_json(query):
    query_url  = BASE_URL + QUERY_PARAMS + query_term
    query_resp = requests.get(query_url)
    query_json = query_resp.json()
    return query_json
 
 
def get_char_json(json_data):
    results = []
    for i in json_data["query"]["search"]:
        char_id = i["title"]
        char_url   = BASE_URL + ENTITIES_PARAMS + char_id
        char_resp  = requests.get(char_url)
        char_json  = char_resp.json()
        char_json["id"] = char_id
        results.append(char_json)
    return results

       
def get_entity_json(char_json):
    entity_id = char_json["id"]
    entity_url = BASE_URL + ENTITIES_PARAMS + entity_id
    entity_resp = requests.get(entity_url)
    entity_json = entity_resp.json()
    entity_json["id"] = entity_id
    return entity_json


def get_claims(entity):
    entity_id = entity.get("id")
    entity_dict = entity.get("entities").get(entity_id)
    entity_title = entity_dict.get("sitelinks").get("eswiki", {}).get("title", "None")
    char_claims = dict()
    char_claims["title"] = entity_title
    for claim_k, claim_v in CLAIMS.items():
        snaks = entity_dict.get("claims").get(claim_v)
        id_list = []
        for snak in snaks:
            claim_id = snak.get("mainsnak").get("datavalue").get("value").get("id")
            if len(snaks) > 1:
                id_list.append(claim_id)
            else:
                id_list = claim_id
        char_claims[claim_k] =  id_list
    return char_claims


def get_sp_data(char_claims):
    sp_ids = char_claims["superpoder"]
    sp_str = "|".join(sp_ids)
    sp_url = BASE_URL + ENTITIES_PARAMS + sp_str
    sp_resp = requests.get(sp_url)
    sp_json = sp_resp.json()
    sp_data = dict()
    for i in  sp_ids:
        sp_entity = sp_json.get("entities").get(i)
        sp_dict = dict(
            name=sp_entity.get("labels").get("es").get("value"),
            desc=sp_entity.get("descriptions").get("es").get("value")
        )
        sp_data[i] = sp_dict
    return sp_data


query_term  = "Emma frost Marvel"
query_json  = get_query_json(query_term)
char_json   = get_char_json(query_json)
entities    = [get_entity_json(i) for i in char_json]
char_claims = [get_claims(i) for  i in entities]
sp_data     = [get_sp_data(i) for i in char_claims]
chars = []
for claim, sp in zip(char_claims, sp_data):
    claim["detalles"] = sp_data
    chars.append(claim)
chars