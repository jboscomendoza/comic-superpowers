import requests

# Refs
# https://www.mediawiki.org/wiki/Wikibase/API
# https://www.mediawiki.org/wiki/API:Presenting_Wikidata_knowledge#Parsing_claims
# https://www.wikidata.org/w/api.php?action=help&modules=wbgetentities

BASE_URL = "http://www.wikidata.org/w/api.php?format=json"

PARAMS_QUERY = "&action=query&list=search&srsearch="

PARAMS_ENTITY= (
    "&action=wbgetentities" +
    "&languages=es" +
    "&languagefallback=true" +
    "&sitefilter=eswiki"
    )

PARAMS_ENTITY = (
    "&action=wbgetentities" +
    "&languages=es" +
    "&languagefallback=true" +
    "&sitefilter=eswiki"
    )

WIKIDATA  = "&sites=wikidatawiki&ids="
WIKIPEDIA = "&sites=enwiki&titles="

CLAIMS = {
    "genero":"P21",
    "superpoder":"P2563",
    "membresia":"P463",
    "universo":"P1080"
    }


def get_query_json(query_term):
    query_url  = BASE_URL + PARAMS_QUERY + query_term
    query_resp = requests.get(query_url)
    query_json = query_resp.json()
    return query_json
 
 
def get_char_json(json_data):
    """Site is one of wikidata or wikipedia"""
    results = []
    for i in json_data["query"]["search"]:
        char_id = i["title"]
        char_url   = BASE_URL + PARAMS_ENTITY + WIKIDATA + char_id
        char_resp  = requests.get(char_url)
        char_json  = char_resp.json()
        char_json["id"] = char_id
        results.append(char_json)
    return results


def get_entity(entity_str:str, type:str):
    """type: One of 'id' or 'title', for querying wikidata or wikipedia, respectively."""
    if  type == "id":
        entity_url = BASE_URL + PARAMS_ENTITY + WIKIDATA + entity_str
    elif type == "title":
        entity_url = BASE_URL + PARAMS_ENTITY + WIKIPEDIA + entity_str
    entity_resp = requests.get(entity_url)
    entity_json = entity_resp.json()
    entity_json["id"] = entity_str
    return entity_json


def get_entity_json(char_json:dict):
    entity_id = char_json["id"]
    entity_url = BASE_URL + PARAMS_ENTITY + WIKIDATA + entity_id
    entity_resp = requests.get(entity_url)
    entity_json = entity_resp.json()
    entity_json["id"] = entity_id
    return entity_json


def get_claims(entity, entity_title=None):
    if entity_title is None:
        entity_id = entity.get("id")
        entity_dict = entity.get("entities").get(entity_id)
        entity_title = entity_dict.get("sitelinks").get("eswiki", {}).get("title", "None")
    else: 
        entity_id = [str(i) for i in entity.get("entities").keys()][0]
        entity_dict = entity.get("entities").get(entity_id)
    char_claims = dict()
    char_claims["title"] = entity_title
    for claim_k, claim_v in CLAIMS.items():
        snaks = entity_dict.get("claims").get(claim_v)
        id_list = []
        if snaks is not None:
            for snak in snaks:
                claim_id =  snak.get("mainsnak").get("datavalue").get("value").get("id")
                if len(snaks) > 1:
                    id_list.append(claim_id)
                else:
                    id_list = claim_id
        else:
            pass
        char_claims[claim_k] =  id_list
    return char_claims


def get_sp_data(char_claims):
    sp_ids = char_claims["superpoder"]
    sp_str = "|".join(sp_ids)
    sp_url = BASE_URL + PARAMS_ENTITY + WIKIDATA + sp_str
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