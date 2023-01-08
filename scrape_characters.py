import requests as re
import reqchars as rc
import json
import time

with open("wiki_links.txt", "r") as links_file:
    x_men = links_file.readlines()
    x_men = [i.rstrip("\n") for i in x_men]

x_men_groups = []
cuantos = 25

for i in range(0, len(x_men), cuantos):
    x = i
    x_men_groups.append(x_men[x:x+cuantos])

x_men_groups = ["|".join(i) for i in x_men_groups]

x_men_ents = []

for x_men_names in x_men_groups:
    entity_group = rc.get_entity(x_men_names, type="title")
    x_men_ents.append(entity_group)
    # Courtesy sleep
    time.sleep(2)

with open('x_men_ents.txt', 'w') as file_json:
    json.dump(x_men_ents, file_json)