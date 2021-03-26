#!/usr/bin/env python3
from scipy.io import wavfile
import pandas as pd
import matplotlib.pyplot as plt

def extractSamples(file):
    samplerate, data = wavfile.read(file)
    return data.flatten()

if __name__ == "__main__":
    data = extractSamples("/home/aniol/Music/PinkFloyd_Money.wav")
    df = pd.DataFrame(data, columns=["samples"])
    print(len(df))
    df.plot.hist(bins=100)
    plt.show()