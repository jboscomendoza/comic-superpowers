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


def dividir_grupos(lista:list, cantidad:int=50) -> list:
    """Divide una lista de nombres en una lista donde cada elemento
    es un str con cantidad elementos, divididos por |, con formato:
    ['ele1|ele2|ele3', 'ele4|ele5|ele6', ... ]
    """
    divisiones = []
    for i in range(0, len(lista), cantidad):
        x = i
        ls = lista[x:x+cantidad]
        ls = "|".join(ls)
        divisiones.append(ls)
    return divisiones


def get_entity(entity_str:str, type:str) -> dict:
    u"""Consulta a wikidata o wikipedia para obtener el listado de atributos 
    de una entidad identificada por su id o título (title).

    Args:
        entity_str (str): Nombre de la entidad. Puede ser una sola entidad o 
        varias, divididas por |.
        type (str): "id" para consultar wikidata; "title" para consultar 
        wikipedia.

    Returns:
        dict: Diccionario con el listado de atributos de la o las entidades 
        consultada, con estructura json.
    """
    if  type == "id":
        entity_url = BASE_URL + PARAMS_ENTITY + WIKIDATA + entity_str
    elif type == "title":
        entity_url = BASE_URL + PARAMS_ENTITY + WIKIPEDIA + entity_str
    entity_resp = requests.get(entity_url)
    entity_json = entity_resp.json()
    entity_json["id"] = entity_str
    return entity_json


def get_id(entity:dict, what_id:str) -> list:
    """Recupera identificadores únicos de entidad, contenidos en el 
    identificador de un atributo, llamado 'claim'.
    Por ejemplo, para el atributo "poderes", devuelve todos los 
    identificadores de poderes que tiene la entidad.
    
    La ruta en wikidata para llegar a un id es:
    mainsnak/datavalue/value/id; donde 'mainsnak' es el conjunto de
    valores de un claim.

    Args:
        entity (dict): Entidad, formato json.
        what_id (str): id del atributo, como aparece en wikidata.

    Returns:
        list: Lista de identificadores de Wikidata.
    """
    info_unique = []
    info = entity.get("claims").get(what_id)
    if info is not None:
        for i in info:
            info_id= (
                i
                .get("mainsnak")
                .get("datavalue", {})
                .get("value", {})
                .get("id", None)
                )
            info_unique.append(info_id)
        return info_unique
    else:
        return [None]


def props_dict(lista_unicos:list, prefix:str) -> list:
    u"""Devuelve una lista de atributos con sus valores principales de una
    categoría para análisis

    
    Args:
        lista_unicos (list): Lista de identificadores únicos.
        prefix (str): Prefijo de categoría para análisis. Las categorías 
        pueden ser: 
        - gen: Género
        - sp: Superpoder
        - uni: Universo
        - team: Equipo
        - crea: Creador
        
    Returns:
        list: Lista de diccionarios, cada uno con los atributos principales 
        de un indicador.
    """
    unique_list = []
    grupos = dividir_grupos(lista_unicos)
    for grp in grupos:
        unique_ents = get_entity(grp, "id")
        for i in lista_unicos:
            props = unique_ents.get("entities").get(i)
            if props is not None:
                ent_props = {
                    prefix+"_id": props.get("id"),
                    prefix+"_nombre": props.get("labels").get("es", {}).get("value"),
                    prefix+"_desc": props.get("descriptions", {}).get("es", {}).get("value"),
                    prefix+"_idioma": props.get("descriptions", {}).get("es", {}).get("language"),
                    prefix+"_wiki": props.get("sitelinks", {}).get("eswiki", {}).get("title")
                }
                unique_list.append(ent_props)
    return unique_list


###
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