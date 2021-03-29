from scipy.io import wavfile
import pandas as pd

def samplesToFile(file):
    samplerate, data = wavfile.read(file)
    df = pd.DataFrame(data.flatten(), columns=["samples"])
    df.to_csv(file + ".samples", index=False, header=False, sep="\n")
