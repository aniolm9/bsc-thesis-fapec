#!/usr/bin/env python3
from scipy.io import wavfile
from pydub import AudioSegment
import pandas as pd
import numpy as np
import subprocess
import argparse
import io
import os

def setupParser():
    parser = argparse.ArgumentParser(description='Plot histograms.')
    parser.add_argument('-d', '--directory', type=str, help='Path to the directory of the files in the CSV.')
    parser.add_argument('csv', metavar='CSV', type=str, help='Path to CSV file generated by histograms.py.')
    return parser

def getFlacRatio(file):
    file = os.path.join(args.directory, file)
    extension = os.path.splitext(file)[1]
    # Original file size
    orig_size = os.path.getsize(file)
    # Read binary file as int16 samples
    data_array = np.fromfile(file, dtype=np.int16)
    lossy = 0
    samplerate = 44100
    if extension == ".iq":
        # Apply lossy
        wave_losses = [1,2,4,6,8,12,16,24,32,48,64,96,128,196,256,384,512]
        lossy = 6
        data_array = np.floor_divide(data_array, wave_losses[lossy])
        # Create a Nx2 array for the IQ channels
        in_phase = data_array[::2]
        quadrature = data_array[1::2]
        data_array = np.transpose(np.array([in_phase, quadrature]))
    # Create buffer with WAV samples
    wavBuffer = io.BytesIO()
    wavfile.write(wavBuffer, samplerate, data_array)
    # Compress using FLAC and check ratio
    flacBuffer = io.BytesIO()
    song = AudioSegment.from_wav(wavBuffer)
    song.export(flacBuffer, format = "flac")
    ratio_flac = round(orig_size / flacBuffer.getbuffer().nbytes, 3)
    # FAPEC ratio
    result = subprocess.check_output('fapec -qq -dtype 16 -signed -wave 4 2 0 ' + str(lossy) + ' -ow -o /dev/stdout ' + '"' + file + '"', shell=True)
    fapec_size = len(result)
    ratio_fapec = round(orig_size / fapec_size, 3)
    return pd.Series([ratio_fapec, ratio_flac], index=["ratio_fapec", "ratio_flac"])

if __name__ == "__main__":
    args = setupParser().parse_args()
    df = pd.read_csv(args.csv)
    df = pd.concat([df, df.file.apply(getFlacRatio)], axis=1)
    df.to_csv(args.csv, index=False)
    