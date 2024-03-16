from collections import defaultdict

func_candi = defaultdict(set)

import json
def json_pretty_dump(obj, filename):
    with open(filename, "w") as fw:
        json.dump(obj,fw, sort_keys=True, indent=4, separators=(",", ": "), ensure_ascii=False)

import os
for file in os.listdir("../mid-data/func_candi_tuple_lst"):
    if file.endswith(".txt"):
        print(file)
        with open(os.path.join("../mid-data/func_candi_tuple_lst", file), "r") as rf:
            for line in rf:
                func, tri_tuple_lst = line.strip().split(":")
                for tri_tuple_str in tri_tuple_lst.split('\t'):
                    func_candi[func].add(tri_tuple_str)

#print(len(func_candi))

func_candi_json = {func:[] for func in func_candi}
for func, tri_tuple_set in func_candi.items():
    for tri_tuple_str in tri_tuple_set:
        [candi, lag, corr_rate] = tri_tuple_str.split(',')
        func_candi_json[func].append((candi, int(lag), float(corr_rate)))

json_pretty_dump(func_candi_json, "../mid-data/func_candi.json")
