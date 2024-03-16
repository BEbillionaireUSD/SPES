import numpy as np
import os
from tqdm import tqdm
from collections import defaultdict
import time

def cal_correlation(pre_arr, arr, lag):
    if lag > 0:
        pre = np.where(np.array(pre_arr[:-lag])>0, True, False)
        cur = np.where(np.array(arr[lag:])>0, True, False)
    else:
        pre = np.where(np.array(pre_arr)>0, True, False)
        cur = np.where(np.array(arr)>0, True, False)
    
    if sum(cur) > 0:
        return sum(pre & cur) / sum(cur), sum(pre & (~cur)) / sum(~cur)
    else:
        return 0, 0


import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--start", default=0, type=int)
parser.add_argument("--total", default=3704, type=int) #1/10 of the total
parser.add_argument("--warm_th", default=0.7, type=float)

if __name__ == '__main__':
    params = vars(parser.parse_args())
    start, total = params["start"], params["total"]
    warm_th, zero_th = params["warm_th"], 1 - params["warm_th"]

    func_arrcount = {}
    func_forget = {}
    with open("./cal_corr/to_cal_corr.txt") as rf:
        for line in rf:
            func, forget, arrcount = line.strip().split('\t')
            func_forget[func] = int(forget)
            func_arrcount[func] = [int(a) for a in arrcount.split(',')]
    
    unknown_ownerapp_lst = {}
    with open("./cal_corr/unknown_ownerapp_lst.txt") as rf:
        for line in rf:
            func, ownerapp_lst = line.strip().split('\t')
            unknown_ownerapp_lst[func] = ownerapp_lst.split(',')
    
    pre_func_lst = defaultdict(list)
    
    c = 0
    st = time.time()
    with tqdm(total=total) as pbar:
        for func in sorted(list(unknown_ownerapp_lst.keys()))[start * total: min((start+1) * total, len(unknown_ownerapp_lst))]:
            c += 1
            if c % 40 == 0: pbar.update(40)
            for pre_func in set(unknown_ownerapp_lst[func]):
                
                if pre_func == func: continue
                forget = func_forget[pre_func]
                for lag in range(0, 11):
                    corr_rate, zero_inconsistency = cal_correlation(func_arrcount[pre_func][forget*1440: ],
                                                                    func_arrcount[func][forget*1440: ], lag)
                    if corr_rate >= warm_th and zero_inconsistency <= zero_th:
                        #print(corr_rate, warm_th, zero_inconsistency, zero_th)
                        pre_func_lst[func].append((pre_func, lag, corr_rate))
                        break
            
            if func in pre_func_lst: #sort: in the order of corr_rate from large to small
                pre_func_lst[func] = sorted(pre_func_lst[func], key=lambda tri_tuple: tri_tuple[-1], reverse=True)

    print(len(pre_func_lst), round((time.time()-st)/60, 4))
    
    os.makedirs("./func_candi_tuple_lst", exist_ok=True)

    with open(f"./func_candi_tuple_lst/{start}.txt", "w") as wf:
        for f, tri_tuple_lst in pre_func_lst.items():
            wf.write(f+":"+'\t'.join("{},{},{:.4f}".format(a, b, c) for (a, b, c) in tri_tuple_lst)+'\n')
