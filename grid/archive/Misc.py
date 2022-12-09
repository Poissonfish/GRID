import numpy as np
import pandas as pd
from enum import Enum
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *



def get_peak(img, map, n_smooth=100, axis=0):
    '''
    '''
    from scipy.signal import find_peaks
    import numpy as np
    # compute signal
    ls_mean = img.mean(axis=(not axis)*1) # 0:nrow
    # gaussian smooth signal
    for i in range(n_smooth):
        ls_mean = np.convolve(np.array([1, 2, 4, 2, 1])/10, ls_mean, mode='same')
    peaks, _ = find_peaks(ls_mean)
    if map is not None:
        if len(peaks) > map.shape[axis]:
            while len(peaks) > map.shape[axis]:
                ls_diff = [peaks[i+1]-peaks[i] for i in range(len(peaks)-1)]
                idx_diff = np.argmin(ls_diff)
                idx_kick = idx_diff if (ls_mean[peaks[idx_diff]] < ls_mean[peaks[idx_diff+1]]) else (idx_diff+1)
                peaks = np.delete(peaks, idx_kick)
        elif len(peaks) < map.shape[axis]:
            while len(peaks) < map.shape[axis]:
                ls_diff = [peaks[i+1]-peaks[i] for i in range(len(peaks)-1)]
                idx_diff = np.argmax(ls_diff)
                peak_insert = (peaks[idx_diff]+peaks[idx_diff+1])/2
                peaks = np.sort(np.append(peaks, int(peak_insert)))
    return peaks, ls_mean



