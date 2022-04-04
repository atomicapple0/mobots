import cv2
import numpy as np

import matplotlib.pyplot as plt
from skimage import exposure
from skimage import filters

from scipy.ndimage import gaussian_filter1d

def view_hist(img, val=-1):
    if val == -1:
        val = filters.threshold_otsu(img)
    hist, bins_center = exposure.histogram(img)
    # plt.figure(figsize=(9, 4))
    # plt.subplot(131)
    # plt.imshow(img, cmap='gray', interpolation='nearest')
    # plt.axis('off')
    # plt.subplot(132)
    # plt.imshow(img > val, cmap='gray', interpolation='nearest')
    # plt.axis('off')
    hist = gaussian_filter1d(hist, 5)
    plt.plot(bins_center, hist, lw=2)
    plt.axvline(val, color='k', ls='--')
    plt.tight_layout()
    plt.show()

def calc_threshold(img):
    img = img[img!=0].flatten()
    val = min(120, np.percentile(img, 70) - 5)
    # view_hist(img, val=val)
    return val

# def find_bimodal_peaks(hist, bin_centers):
#     hist = gaussian_filter1d(hist, 5)
#     length = len(hist)
#     ret = []
#     lookaround = 15
#     for i in range(length):
#         is_peak = True
#         if i < lookaround or i > length - lookaround:
#             continue
#         if i-lookaround > 0:
#             is_peak &= (hist[i] > 1.05 * hist[i-lookaround])
#         if i+lookaround < length:
#             is_peak &= (hist[i] > 1.05 * hist[i+lookaround])
#         is_peak &= (hist[i] > 1.2 * np.percentile(hist, 30))
#         if is_peak:
#             ret.append(bin_centers[i])
#     if not ret:
#         print('no peaks')
#         return -1
#     peaks = np.array(ret)
#     midpoint = filters.threshold_otsu(peaks)
#     final_peaks = [np.max(peaks[peaks < midpoint]), np.min(peaks[peaks > midpoint])]
#     print('peaks: %s -> %s' % (str(peaks), str(final_peaks)))
#     if final_peaks[1] - final_peaks[0] < lookaround:
#         print('they suck!')
#         return -1
#     return np.mean(final_peaks)

def rescale(img, pix=500):
    img_radius = np.min(img.shape[:2])
    return cv2.resize(img, dsize=(0, 0), fx=pix/img_radius, fy=pix/img_radius)

def cv2_view(t=0, **kwargs):
    for name,img in kwargs.items():
        print(f'displaying {name}')
        # cv2.imshow('img', img)
        # cv2_wait(t)

def cv2_wait(t=0):
    key = cv2.waitKey(t) & 0xFF
    if key == ord("q"):
        exit()

def bgr2gray(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

def bin2gray(img):
    return img.astype(np.uint8) * 255

def flatten_array(arr):
    return [x for sublist in arr for x in sublist]