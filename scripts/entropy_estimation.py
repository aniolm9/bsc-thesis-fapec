import numpy as np
from scipy import stats

def gaussian_kernel(z, bw):
    return np.exp(-(z**2)/(2*bw**2))/np.sqrt(2*np.pi*bw**2)

def estimate_pdf(x, data, chunksize):
    pdf = []
    for subx, subdata in zip(chunker(x, chunksize), chunker(data, chunksize, True)):
        bw = 0.9*min(np.std(subdata), stats.iqr(subdata)/1.34)*chunksize**(-1/5)
        subpdf = (1/len(subdata))*sum(gaussian_kernel(subx-subdata, bw))
        pdf.extend(subpdf)
    return np.array(pdf)

def estimate_entropy(x, data, pdf):
    h_hat = 0
    for value in data:
        i = find_nearest(x, value)
        h_hat += np.log(pdf[i]) if pdf[i] != 0 else 0
    return -h_hat/len(data)

def chunker(l, n, shuffle=False):
    # looping till length l
    if shuffle:
        np.random.shuffle(l)
    for i in range(0, len(l), n): 
        yield l[i:i + n]

def find_nearest(array, value):
    idx = np.searchsorted(array, value, side="left")[0]
    if idx > 0 and (idx == len(array) or np.fabs(value - array[idx-1]) < np.fabs(value - array[idx])):
        return idx-1
    else:
        return idx
