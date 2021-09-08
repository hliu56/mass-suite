# -*- coding: utf-8 -*-
"""
Created on Tue Sep  7 19:29:39 2021

@author: scarlet_07
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Aug 17 15:12:19 2021

@author: scarlet_07
"""

#!/usr/bin/python
# Next step: add mss_process into the mp.py, make mp use on multiple files
# map issue: solution a) put all_scans as func constant b) call the .py script outside and loop there

#Class

import sys
# import mss
sys.path.append('../')
from mss import mssmain as msm
import numpy as np
from multiprocessing import Pool
import peakutils
import scipy
import itertools
from timeit import default_timer as timer
import pandas as pd
from mzmlclass import MzmlClass
from mzmlclass import testfunc

#path = '../example_data/ex_1.mzML'
#mzml_scans = msm.get_scans(path)
#msm.noise_removal(mzml_scans, int_thres=5000)
#mzml_scans = msm.get_scans(path)[:100]
#msm.noise_removal(mzml_scans, int_thres=5000)
#def error
#path = '/home/hack_summer/mass-suite/example_data/'
#all_scans, file_list = msm.batch_scans(path, remove_noise=True, thres_noise=5000)
#err=20  

def main(): #Add variable in main() and add loop into the main module
    start = timer()
    
    path = '../example_data/ex_2.mzML'
    #mzml_scans = msm.get_scans(path)
    #msm.noise_removal(mzml_scans, int_thres=5000)
    mzml_scans = msm.get_scans(path)[:100]
    msm.noise_removal(mzml_scans, int_thres=5000)
    mzml = MzmlClass(mzml_scans, 20)
    
    rt = [i.scan_time[0] for i in mzml_scans]
    ms_list = msm.mz_gen(mzml.mzml_scans, mzml.err, mz_c_thres=5)[:100]
    print(len(ms_list))
    print(len(mzml.mzml_scans))
    with Pool() as pool:
        peak_dict = pool.map(testfunc, ms_list)
        peak_dict = list(filter(None, peak_dict))
    super_list = []
    for d in peak_dict:
        for k, v in d.items():  # d.items() in Python 3+
            super_list.append([k]+v)

    rt_index = [ i[0] for i in super_list]
    rt_list = [rt[i] for i in rt_index]
    

    d_result = pd.DataFrame()
    d_result['m/z'] = [round(i[6],4) for i in super_list]
    d_result['rt'] = [round(i,2) for i in rt_list]
    d_result['peak area'] = [i[3] for i in super_list]
    d_result['sn'] = [i[4] for i in super_list]
    print(d_result)
    
    end = timer()
    print(f'elapsed time: {end - start}')

if __name__ == '__main__':
    main()