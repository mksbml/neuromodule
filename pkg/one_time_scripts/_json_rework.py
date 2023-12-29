

from os import listdir
from pkg.cache.cache import save_machinery, tractor_jsons
import json


JSON_tractorS_FOLDER = "json_database/tractors/"
JSON_TRAILER_FOLDER = "json_database/trailers/"
JSON_HARVESTER_FOLDER = "json_database/harvesters/"
JSON_MISC_FOLDER = "json_database/misc/"

# everything = "everyjson/"
everything = "json_database/misc/"


# for f_name in [everything+f for f in listdir(everything)]:
#     # try:
#         with open(f_name, encoding='utf-8') as f:
#             data = json.load(f)
#         save_machinery(data)
#     # except Exception as e:
#     #     print(e)
#         # pass
# for i in tractor_jsons:
#     if tractor_jsons[i]["Мощность двигателя, л.с."] == '220':
#         print(tractor_jsons[i])