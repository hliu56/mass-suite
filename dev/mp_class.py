import sys
# import mss
sys.path.append('../')
from mss import mssmain as msm
import numpy as np
import multiprocessing
import peakutils
import scipy
import itertools
from timeit import default_timer as timer
import pandas as pd

if __name__ == '__main__':
    path = '../example_data/'
    all_scans, file_list = msm.batch_scans(path, remove_noise=True, thres_noise=5000)
    jobs = []
    for scans in all_scans:
        print(type(scans))
        p = multiprocessing.Process(target=msm.peak_list,args=(scans,))
        jobs.append(p)
        p.start()