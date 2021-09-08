# -*- coding: utf-8 -*-
"""
Created on Tue Sep  7 19:22:03 2021

@author: scarlet_07
"""
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

def testfunc(n):
    return True

class MzmlClass:
    def __init__(self, mzml_scans, err):
        self.mzml_scans = mzml_scans
        self.err = err
    
    def peak_pick(self):
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

    
        return True