import sys

# import mss
sys.path.append('../')
from mss import mssmain as msm
from mss import align
import multiprocessing
from timeit import default_timer as timer
import pandas as pd

if __name__ == '__main__':
    start = timer()
    path = '../example_data/'
    all_scans, file_names = msm.batch_scans(path, remove_noise=True, thres_noise=5000)
    file_list = [path + str(i) + '.csv' for i in file_names]
    files = list(zip(all_scans, file_list))
    jobs = []
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    for scans in files:
        p = multiprocessing.Process(target=msm.mp_peak_list, args=(scans[0],scans[1],return_dict))
        jobs.append(p)
        p.start()

    for proc in jobs:
        proc.join()

    df_list = return_dict.values()
    alignment = align.mss_align(df_list, '../example_data/test.csv', file_names, RT_error = 0.5, mz_error = 0.02)
    end = timer()
    print(f'elapsed time: {end - start}')

