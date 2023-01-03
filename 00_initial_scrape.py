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


def get_sp_json(sp_list):
    sp_ids = "|".join(sp_list)
    sp_url = BASE_URL + ENTITIES_PARAMS + sp_ids
    sp_resp = requests.get(sp_url)
    sp_json = sp_resp.json()
    return sp_json


def get_sp_data(sp_id, sp_json):
    sp_entity = sp_json.get("entities").get(sp_id)
    sp_dict = dict(
        sp_data = sp_entity.get("labels").get("es").get("value"),
        sp_id = sp_entity.get("descriptions").get("es").get("value")
        )
    return sp_dict


query_term  = "Emma frost Marvel"
query_json  = get_query_json(query_term)
char_json   = get_char_json(query_json)
entities    = [get_entity_json(i) for i in char_json]
char_claims = [get_claims(i) for  i in entities]
sp_value = []
for claim in char_claims:
    sp_entity = []
    for i in claim:
        try:
            sp_entity.append(i["superpoder"])
        except:
            pass
    sp_value.append(sp_entity)
sp_json = [get_sp_json(i) for i in sp_value]
sp_data = []
for i in range(len(sp_json)):
    sp_data.append([get_sp_data(sp, sp_json[i]) for sp in sp_value[i]])
sp_data