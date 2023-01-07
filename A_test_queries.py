import requests
import reqchars as rc

#Search query
query_term  = "Emma frost Marvel"
query_json  = rc.get_query_json(query_term)
char_json   = rc.get_char_json(query_json)
entities    = [rc.get_entity_json(i) for i in char_json]
char_claims = [rc.get_claims(i) for  i in entities]
sp_data     = [rc.get_sp_data(i) for i in char_claims]
chars = []
for claim, sp in zip(char_claims, sp_data):
    claim["detalles"] = sp_data
    chars.append(claim)
chars

# by title
exact_title = "Gambit_(Marvel_Comics)"
ent = rc.get_entity(exact_title, type="title")
ent_claims = rc.get_claims(ent, exact_title)
ent_sp = rc.get_sp_data(ent_claims)