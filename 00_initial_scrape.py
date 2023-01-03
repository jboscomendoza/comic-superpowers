import requests

# Refs
# https://www.mediawiki.org/wiki/Wikibase/API
# https://www.mediawiki.org/wiki/API:Presenting_Wikidata_knowledge#Parsing_claims
# https://www.wikidata.org/w/api.php?action=help&modules=wbgetentities

search_term = "Emma frost Marvel"
 
base_url = "http://www.wikidata.org/w/api.php?format=json"
query_params = "&action=query&list=search&srpop&srsearch="
query_url = base_url + query_params + search_term


params_str = (
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
 
resp_query = requests.get(query_url)
 
query_json = resp_query.json()
 
def get_char_json(json_data):
    results = []
    for i in json_data["query"]["search"]:
        char_id = i["title"]
        char_url   = base_url + params_str + char_id
        char_resp  = requests.get(char_url)
        char_json  = char_resp.json()
        char_json["id"] = char_id
        results.append(char_json)
    return results
       
results  = get_char_json(query_json)

def get_entity_json(char_json):
    entity_id = char_json["id"]
    entity_url = base_url + params_str + entity_id
    entity_resp = requests.get(entity_url)
    entity_json = entity_resp.json()
    entity_json["id"] = entity_id
    return entity_json

entities = [get_entity_json(i) for i in results]


def get_claims(entity):
    entity_id = entity.get("id")
    entity_dict = entity.get("entities").get(entity_id)
    entity_title = entity_dict.get("sitelinks").get("eswiki", {}).get("title", "None")
    
    char_claims = []
    char_claims.append({"title": entity_title})
    for claim_k, claim_v in CLAIMS.items():
        snaks = entity_dict.get("claims").get(claim_v)
        for snak in snaks:
            claim_id = snak.get("mainsnak").get("datavalue").get("value").get("id")
            key_info = {claim_k: claim_id}
        char_claims.append(key_info)
    
    return char_claims

char_claims = [get_claims(i) for i in entities]
char_claims

sp_value = [i.get("superpoder") for i in char_claims if i.get("superpoder") is not None]
sp_value

def get_sp_json(sp_list):
    sp_ids = "|".join(sp_list)
    sp_url = base_url + params_str + sp_ids
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

sp_json = get_sp_json(sp_value)
sp_data = [get_sp_data(i, sp_json) for i in sp_value]
sp_data


