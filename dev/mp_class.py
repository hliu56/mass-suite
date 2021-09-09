import sys

# import mss
sys.path.append('../')
from mss import mssmain as msm
import multiprocessing
from timeit import default_timer as timer

if __name__ == '__main__':
    start = timer()
    path = '../example_data/'
    all_scans, file_list = msm.batch_scans(path, remove_noise=True, thres_noise=5000)
    jobs = []
    for scans in all_scans:
        p = multiprocessing.Process(target=msm.peak_list, args=(scans,))
        jobs.append(p)
        p.start()

    end = timer()
    print(f'elapsed time: {end - start}')
