# import imageio
import sys
import numpy as np

def find_eta(i_val, j_val, imgarr, m00, m10m00, m01m00):
    lamda = ((i_val + j_val) / 2) + 1
    mu = find_mu(i_val, j_val, imgarr, m00, m10m00, m01m00)
    return mu / ((m00) ** lamda)

def find_mu(i_val, j_val, imgarr, m00, m10m00, m01m00):
    cnt = 0
    for i in range(len(imgarr)):
        for j in range(len(imgarr[0])):
            cnt += ((i + 1) - m10m00) ** i_val * ((j + 1) - m01m00) ** j_val * imgarr[i, j]
    return cnt

def invariant_moment(im):
    # im = imageio.imread(im).astype('float64')
    if len(np.shape(im)) == 3:
        im = im[:, :, 0]
    im = im / 255
    # im = im*255
    print(im)
    print(im.shape)

    m00 = np.sum(im)
    m10m00 = 0
    for i in range(len(im)):
        for j in range(len(im[0])):
            m10m00 += (j + 1) * im[i, j]
    m10m00 = m10m00 / m00

    m01m00 = 0
    for i in range(len(im)):
        for j in range(len(im[0])):
            m01m00 += (i + 1) * im[i, j]
    m01m00 = m01m00 / m00

    eta0_2 = find_eta(0, 2, im, m00, m10m00, m01m00)
    eta0_3 = find_eta(0, 3, im, m00, m10m00, m01m00)
    eta1_1 = find_eta(1, 1, im, m00, m10m00, m01m00)
    eta1_2 = find_eta(1, 2, im, m00, m10m00, m01m00)
    eta2_0 = find_eta(2, 0, im, m00, m10m00, m01m00)
    eta2_1 = find_eta(2, 1, im, m00, m10m00, m01m00)
    eta3_0 = find_eta(3, 0, im, m00, m10m00, m01m00)

    phi1 = eta2_0 + eta0_2
    phi2 = ((eta2_0 + eta0_2) ** 2) + (4 * (eta1_1 ** 2))
    phi3 = ((eta3_0 - (3 * eta1_2)) ** 2) + (((3 * eta2_1) - eta0_3) ** 2)
    phi4 = ((eta3_0 + eta1_2) ** 2) + ((eta2_1 + eta0_3) ** 2)
    phi5 = (3 * eta2_1 - eta0_3) * (eta2_1 + eta0_3) * ((eta3_0 + eta1_2) ** 2 - (eta2_1 + eta0_3) ** 2) + \
           (eta3_0 - (3 * eta1_2)) * (eta3_0 + eta1_2) * ((eta3_0 + eta1_2) ** 2 - (3 * (eta2_1 + eta0_3) ** 2))
    phi6 = ((3 * eta2_1) - eta0_3) * ((eta3_0 + eta1_2) ** 2 - (eta2_1 + eta0_3) ** 2) + \
           4 * eta1_1 * (eta3_0 + eta1_2) * (eta2_1 + eta0_3)
    phi7 = ((3 * eta2_1) - eta0_3) * (eta3_0 + eta1_2) * ((eta3_0 + eta1_2) ** 2 - (3 * (eta2_1 + eta0_3) ** 2)) - \
           (eta3_0 - (3 * eta1_2)) * (eta2_1 + eta0_3) * ((3 * (eta3_0 + eta1_2) ** 2) - (eta2_1 + eta0_3) ** 2)

    return np.array([phi1, phi2, phi3, phi4, phi5, phi6, phi7])