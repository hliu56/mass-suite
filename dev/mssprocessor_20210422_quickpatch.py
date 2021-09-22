#import sys
import mss
# sys.path.append('../')
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
    start = timer()
    data_path = '../example_data/'#input('data path:')
    output_path = '../example_data/test2.csv'#input('output path:')
    align.mss_process(data_path, output_path, thres_noise=5000,enable_score=False)
    end = timer()
    print(f'elapsed time: {end - start}')
    return

if __name__ == '__main__':
    main()
