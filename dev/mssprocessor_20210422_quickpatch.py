import sys
sys.path.append('../')
import mss
from mss import mssmain as msm
from mss import align
from timeit import default_timer as timer
'''
path = input('filename to process:')
scans = msm.get_scans(path, ms_all=False, ms_lv=1)
#noise removal
msm.noise_removal(scans, 2000)
d_op = msm.peak_list(scans, 10, enable_score=True,peak_base=0.001,peak_area_thres=0)
output_path = input('path and filename to export:')
d_op.to_csv(output_path)
'''
def main():
    data_path = 'D:/UW/6ppdozonation_mzml/20210618_6PPDozonation_mzml_MSStest/'#input('data path:')
    output_path = 'D:/UW/6ppdozonation_mzml/summary.csv'#input('output path:')
    align.mss_process(data_path, output_path,err_ppm=20, thres_noise=3000,enable_score=False)
    return

if __name__ == '__main__':
    main()
