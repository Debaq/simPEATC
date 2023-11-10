from scipy.ndimage import gaussian_filter1d

def smooth_curve_gaussian(array, sigma):
    smoothed_array = gaussian_filter1d(array, sigma=sigma)
    return smoothed_array

