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
import re

def setupParser():
    parser = argparse.ArgumentParser(description='Plot histograms.')
    parser.add_argument('-t', '--type', type=str, choices=['wave', 'kmall'], help='Data structure type to process.', required=True)
    parser.add_argument('-a', '--auto', dest="auto", action='store_true', help='Automatically generate missing files, if possible.', required=False)
    parser.add_argument('files', metavar='FILES', type=str, nargs='+', help='List of files to plot a histogram of.')
    return parser

def waveGenerator(file):
    # Find PE using a bash pipeline (faster)
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wave/wave_pe.sh")
    wave_pe = subprocess.run([script_path, file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # Dataframe for PE
    df_pe = pd.read_csv(StringIO(wave_pe.stdout.decode('utf-8')), header=None, names=["PE"], dtype="int32")
    # Dataframe for original samples
    df_samples = pd.DataFrame(np.fromfile(file, dtype="int16"), columns=["samples"], dtype="int16")
    # Return both dataframes
    return df_samples, df_pe

def kmallGenerator(file):
    # Find PE using a bash pipeline (faster)
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kmall/kmall_pe.sh")
    kmall_pe = subprocess.run([script_path, file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # Dataframe for PE
    df_pe = pd.read_csv(StringIO(kmall_pe.stdout.decode('utf-8')), header=None, names=["PE"], dtype="int16")
    # Dataframe for original samples
    df_samples = pd.DataFrame(np.fromfile(file, dtype="int8"), columns=["samples"], dtype="int8")
    # Return both dataframes
    return df_samples, df_pe

if __name__ == "__main__":
    args = setupParser().parse_args()
    # Use a Sans-Serif for figures
    fontProperties = {'family': 'sans-serif', 'sans-serif': ['Latin Modern Sans']}
    rc('font', **fontProperties)
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
        # Find 0.05, 0.5 and 0.95 quantiles
        df_quantiles = df_pe.quantile([0.05, 0.5, 0.95])
        # Plot histogram
        n_bins = 400 if args.type == "wave" else 255
        fig, ax = plt.subplots()
        fig.suptitle("Comparison of original and prediction error samples distributions")
        ax.hist(df_samples, bins=n_bins, log=True, alpha=0.5, label="Original samples")
        ax.hist(df_pe, bins=n_bins, log=True, alpha=0.5, label="Prediction errors")
        # Plot quantiles
        colors = ["r", "g", "b"]
        for i, rows in enumerate(df_quantiles.iterrows()):
            index, row = rows
            ax.axvline(row["PE"], color=colors[i], linewidth=1, label="$P_{" + str(int(index*100)) + "}$")
        # Set figure title and axis labels
        ax.set_title("File: %s" % (os.path.basename(file)), fontsize=9)
        ax.set_xlabel("Sample value")
        ax.set_ylabel("Number of samples")
        ax.legend()
        # Save figure to vectorial graphics pdf
        plt.savefig(file + "_hist.pdf")
        # Free memory
        del df_samples, df_pe
