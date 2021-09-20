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
sys.path.append('/home/hack_summer/mass-suite/')
from mss import mssmain as msm
import numpy as np
from multiprocessing import Pool
import peakutils
import scipy
import itertools
from timeit import default_timer as timer
import pandas as pd

path = '../example_data/ex_3.mzML'
err = 20
#mzml_scans = msm.get_scans(path)
#msm.noise_removal(mzml_scans, int_thres=5000)
mzml_scans = msm.get_scans(path)
msm.noise_removal(mzml_scans, int_thres=5000)
#def error
#path = '/home/hack_summer/mass-suite/example_data/'
#all_scans, file_list = msm.batch_scans(path, remove_noise=True, thres_noise=5000)


def peak_pick(input_mz, error=20, enable_score=False, peak_thres=0.01,
              peakutils_thres=0.02, min_d=1, rt_window=1.5,
              peak_area_thres=1e5, min_scan=5, max_scan=200, max_peak=5,
              overlap_tol=15, sn_detect=15, rt=None):
    '''
    The function is used to detect peak for given m/z's chromatogram
    error: in ppm
    enable_score: option to enable the RF model
    peak_thres: base peak tolerance
    peakutils_thres: threshold from peakutils, may be repeated with peak_thres
    min_d: peaktuils parameter
    rt_window: window for integration only, didn't affect detection
    peak_area_thres: peak area limitation
    min_scan: min scan required to be detected as peak
    max_scan: max scan limit to exclude noise
    max_peak: max peak limit for selected precursor
    overlap_tot: overlap scans for two peaks within the same precursor
    sn_detect: scan numbers before/after the peak for sn calculation
    '''
    if not rt:
        rt = [i.scan_time[0] for i in mzml_scans]
    intensity = msm.ms_chromatogram_list(mzml_scans, input_mz, error)

    # Get rt_window corresponding to scan number
    scan_window = int(
        (rt_window / (rt[int(len(intensity) / 2)] -
                      rt[int(len(intensity) / 2) - 1])))
    rt_conversion_coef = np.diff(rt).mean()
    # Get peak index
    indexes = peakutils.indexes(intensity, thres=peakutils_thres,
                                min_dist=min_d)

    result_dict = {}

    # dev note: boundary detection refinement
    for index in indexes:
        h_range = index
        l_range = index
        base_intensity = peak_thres * intensity[index]
        half_intensity = 0.5 * intensity[index]

        # Get the higher and lower boundary
        while intensity[h_range] >= base_intensity:
            h_range += 1
            if h_range >= len(intensity) - 1:
                break
            if intensity[h_range] < half_intensity:  
                if h_range - index > 4:  
                    # https://stackoverflow.com/questions/55649356/
                    # how-can-i-detect-if-trend-is-increasing-or-
                    # decreasing-in-time-series as alternative
                    x = np.linspace(h_range - 2, h_range, 3)
                    y = intensity[h_range - 2: h_range + 1]
                    (_slope, _intercept, r_value,
                     _p_value, _std_err) = scipy.stats.linregress(x, y)
                    if abs(r_value) < 0.6:
                        break
        while intensity[l_range] >= base_intensity:
            l_range -= 1
            if l_range <= 1:
                break
            # Place holder for half_intensity index
            # if intensity[l_range] < half_intensity:
            #     pass

        # Output a range for the peak list
        # If len(intensity) - h_range < 4:
        #     h_range = h_range + 3
        peak_range = []
        if h_range - l_range >= min_scan:
            if rt[h_range] - rt[l_range] <= rt_window:
                peak_range = intensity[l_range:h_range]
            else:
                if index - scan_window / 2 >= 1:
                    l_range = int(index - scan_window / 2)
                if index + scan_window / 2 <= len(intensity) - 1:
                    h_range = int(index + scan_window / 2)
                peak_range = intensity[l_range:h_range]
                # print(index + scan_window)

        # Follow Agilent S/N document
        width = rt[h_range] - rt[l_range]
        if len(peak_range) != 0:
            height = max(peak_range)
            hw_ratio = round(height / width, 0)
            neighbour_blank = (intensity[
                l_range - sn_detect: l_range] +
                intensity[h_range: h_range +
                          sn_detect + 1])
            noise = np.std(neighbour_blank)
            if noise != 0:
                sn = round(height / noise, 3)
            elif noise == 0:
                sn = 0

        # Additional global parameters
        # 1/2 peak range
        h_loc = index
        l_loc = index
        while intensity[h_loc] > half_intensity:
            h_loc += 1
            if h_loc >= len(intensity) - 1:
                break
        while intensity[l_loc] > half_intensity and l_loc > 0:
            l_loc -= 1

        # Intergration based on the simps function
        if len(peak_range) >= min_scan:
            integration_result = scipy.integrate.simps(peak_range)
            if integration_result >= peak_area_thres:
                # https://doi.org/10.1016/j.chroma.2010.02.010
                background_area = (h_range - l_range) * height
                ab_ratio = round(integration_result / background_area, 3)
                if enable_score is True:
                    h_half = h_loc + \
                        (half_intensity - intensity[h_loc]) / \
                        (intensity[h_loc - 1] - intensity[h_loc])
                    l_half = l_loc + \
                        (half_intensity - intensity[l_loc]) / \
                        (intensity[l_loc + 1] - intensity[l_loc])
                    # when transfer back use rt[index] instead
                    mb = (height - half_intensity) / \
                        ((h_half - index) * rt_conversion_coef)
                    ma = (height - half_intensity) / \
                        ((index - l_half) * rt_conversion_coef)
                    w = rt[h_range] - rt[l_range]
                    t_r = (h_half - l_half) * rt_conversion_coef
                    l_width = rt[index] - rt[l_range]
                    r_width = rt[h_range] - rt[index]
                    assym = r_width / l_width
                    # define constant -- upper case
                    var = (w ** 2 / (1.764 * ((r_width / l_width)
                           ** 2) - 11.15 * (r_width / l_width) + 28))
                    x_peak = [w, t_r, l_width, r_width, assym,
                              integration_result, sn, hw_ratio, ab_ratio,
                              height, ma, mb, ma + mb, mb / ma, var]
                    x_input = np.asarray(x_peak)
                    # score = np.argmax(Pmodel.predict(x_input.reshape(1,-1)))
                    # for tensorflow
                    score = 1
                elif enable_score is False:
                    score = 1

                # appending to result
                if len(result_dict) == 0:
                    (result_dict.update(
                     {index: [l_range, h_range,
                              integration_result, sn, score,input_mz]}))
                # Compare with previous item
                # * get rid of list()
                elif integration_result != list(result_dict.values())[-1][2]:
                    # test python 3.6 and 3.7
                    s_window = abs(index - list(result_dict.keys())[-1])
                    if s_window > overlap_tol:
                        (result_dict.update(
                         {index: [l_range, h_range, integration_result,
                                  sn, score, input_mz]}))
    # If still > max_peak then select top max_peak results
    if len(result_dict) > max_peak:
        result_dict = dict(sorted(result_dict.items(),
                                  key=lambda x: x[1][2], reverse=True))
        result_dict = dict(itertools.islice(result_dict.items(), max_peak))

    return result_dict



def main(): #Add variable in main() and add loop into the main module
    start = timer()

    rt = [i.scan_time[0] for i in mzml_scans]
    ms_list = msm.mz_gen(mzml_scans, err, mz_c_thres=5)

    with Pool() as pool:
        peak_dict = pool.map(peak_pick, ms_list)
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
