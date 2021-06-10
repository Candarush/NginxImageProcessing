import numpy as np
import cv2

def get_ndvi(nir_mat, red_mat): 
    nir_mat = np.array(nir_mat, dtype='uint8')
    red_mat = np.array(red_mat, dtype='uint8')
    nir_mat_float = nir_mat.astype(float)
    red_mat_float = red_mat.astype(float)
    sub_mat = np.subtract(nir_mat_float, red_mat_float)
    sum_mat = np.add(nir_mat_float, red_mat_float)
    result = np.divide(sub_mat,sum_mat)
    return result;

def apply_gradient(grayscale_mat):
    heatmap = heatmap = cv2.applyColorMap((grayscale_mat * 256.).astype('uint8'), cv2.COLORMAP_SUMMER)
    heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
    return heatmap;