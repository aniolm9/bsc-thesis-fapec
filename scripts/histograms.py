#!/usr/bin/env python3
from scipy.stats import entropy
from matplotlib import rc
from io import StringIO
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import argparse
import subprocess
import os
import sys

def setupParser():
    parser = argparse.ArgumentParser(description='Plot histograms.')
    parser.add_argument('-t', '--type', type=str, choices=['wave', 'kmall'], help='Data structure type to process.', required=True)
    parser.add_argument('-a', '--auto', dest="auto", action='store_true', help='Automatically generate missing files, if possible.', required=False)
    parser.add_argument('files', metavar='FILES', type=str, nargs='+', help='List of files to plot a histogram of.')
    return parser

def waveGenerator(file):
    # Find PE using a bash pipeline (faster)
    wave_pe = subprocess.run(["wave/wave_pe.sh", file], capture_output=True)
    # Dataframe for PE
    df_pe = pd.read_csv(StringIO(wave_pe.stdout.decode('utf-8')), header=None, names=["PE"], dtype="int32")
    # Dataframe for original samples
    df_samples = pd.DataFrame(np.fromfile(file, dtype="int16"), columns=["samples"], dtype="int16")
    # Return both dataframes
    return df_samples, df_pe

def kmallGenerator(file):
    # Find PE using a bash pipeline (faster)
    kmall_pe = subprocess.run(["kmall/kmall_pe.sh", file], capture_output=True)
    # Dataframe for PE
    df_pe = pd.read_csv(StringIO(kmall_pe.stdout.decode('utf-8')), header=None, names=["PE"], dtype="int16")
    # Dataframe for original samples
    df_samples = pd.DataFrame(np.fromfile(file, dtype="int8"), columns=["samples"], dtype="int8")
    # Return both dataframes
    return df_samples, df_pe

if __name__ == "__main__":
    args = setupParser().parse_args()
    # Use a Sans-Serif for figures
    rc('font', **{'family': 'sans-serif', 'sans-serif': ['Libertinus Sans']})
    rc('text', usetex=True)
    for file in args.files:
        print("Processing " + file + "...")
        # Get Pandas DataFrame
        df_samples, df_pe = (None, None)
        if args.type == "wave":
            df_samples, df_pe = waveGenerator(file)
        elif args.type == "kmall":
            df_samples, df_pe = kmallGenerator(file)
        else:
            sys.exit(-1)
        # Calculate prediction error probabilities
        probs = df_pe["PE"].value_counts() / len(df_pe["PE"])
        # Find theoretical ratio from Shannon entropy
        bitsPerSample = 16 if args.type == "wave" else 8
        ratio = bitsPerSample/entropy(probs, base=2)
        print("Theoretical ratio \t %.3f" % (ratio))
        # Plot histogram
        n_bins = 400 if args.type == "wave" else 255
        ax = plt.axes()
        ax.hist(df_samples, bins=n_bins, log=True, alpha=0.5)
        ax.hist(df_pe, bins=n_bins, log=True, alpha=0.5)
        ax.set_title("Comparison of original and prediction errors samples distribution")
        ax.set_xlabel("Sample value")
        ax.set_ylabel("Number of samples")
        ax.legend(["Original samples", "Prediction Errors"])
        plt.savefig(file + "_hist.pdf")
        plt.show()
        del df_samples, df_pe
