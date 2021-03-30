#!/usr/bin/env python3
from scipy.stats import entropy
from matplotlib import rc
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
    df = pd.DataFrame([int(n) for n in wave_pe.stdout.decode("utf-8").split("\n") if n.strip('-').isnumeric()])
    # Find original samples (16 bits/sample) using numpy
    df = pd.concat([df, pd.DataFrame(np.fromfile(file, dtype="int16"))], axis=1)
    # Set dataframe columns names
    df.columns = ["PE", "samples"]
    return df

def kmallGenerator(file):
    # Find PE using a bash pipeline (faster)
    kmall_pe = subprocess.run(["kmall/kmall_pe.sh", file], capture_output=True)
    df = pd.DataFrame([int(n) for n in kmall_pe.stdout.decode("utf-8").split("\n") if n.strip('-').isnumeric()])
    # Find original samples using numpy
    df = pd.concat([df, pd.DataFrame(np.fromfile(file, dtype="int8"))], axis=1)
    # Set dataframe columns names
    df.columns = ["PE", "samples"]
    return df

if __name__ == "__main__":
    args = setupParser().parse_args()
    # Use a Sans-Serif for figures
    rc('font', **{'family': 'sans-serif', 'sans-serif': ['Helvetica']})
    rc('text', usetex=True)
    for file in args.files:
        print("Processing " + file + "...")
        # Get Pandas DataFrame
        df = None
        if args.type == "wave":
            df = waveGenerator(file)
        elif args.type == "kmall":
            df = kmallGenerator(file)
        else:
            sys.exit(-1)
        # Calculate prediction error probabilities.
        probs = df["PE"].value_counts()/len(df["PE"])
        # Find theoretical ratio from Shannon entropy.
        bitsPerSample = 16 if args.type == "wave" else 8
        ratio = bitsPerSample/entropy(probs, base=2)
        print("Theoretical ratio \t %.3f" % (ratio))
        # Plot histogram.
        ax = df[["PE", "samples"]].plot.hist(bins=400, log=True, alpha=0.5)
        ax.set_title("Histogram of prediction errors")
        ax.set_xlabel("Sample prediction errors")
        ax.set_ylabel("Number of samples")
        #plt.savefig(file + "_hist.pdf")
        plt.show()
