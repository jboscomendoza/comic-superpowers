import json

SP_CAT = "P2563"

with open("x_men_ents.txt") as file:
    xson = json.loads(file.read())

x_entities_all = dict()

for i in xson:
    x_entities_all.update(i["entities"])

x_entities = x_entities_all.copy()

to_remove = filter(lambda x: len(x) < 4, list(x_entities_all.keys()))
for i in list(to_remove):
    x_entities.pop(i)


sp_unique = []

for i in x_entities.values():
    sp = i.get("claims").get(SP_CAT)
    if sp is not None:
        sp_id = (
            sp[0]
            .get("mainsnak")
            .get("datavalue")
            .get("value")
            .get("id")
            )
        if sp_id not in sp_unique:
            sp_unique.append(sp_id)