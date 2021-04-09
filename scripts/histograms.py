#!/usr/bin/env python3
from scipy.stats import entropy
from datetime import datetime
from io import StringIO
import matplotlib.pyplot as plt
import matplotlib as mpl
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
    mpl.rc('font', **fontProperties)
    # Dataframe for theoretical ratios
    df_ratios = pd.DataFrame(columns=["file", "ratio_fapec_theo"])
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
        samples_value_counts = df_samples["samples"].value_counts()
        pe_value_counts = df_pe["PE"].value_counts()
        probs = pe_value_counts / len(df_pe["PE"])
        # Find theoretical ratio from Shannon entropy
        bitsPerSample = 16 if args.type == "wave" else 8
        ratio = round(bitsPerSample/entropy(probs, base=2), 3)
        df_ratios.loc[0 if pd.isnull(df_ratios.index.max()) else df_ratios.index.max() + 1] = [os.path.basename(file), ratio]
        # Find 0.05, 0.5 and 0.95 quantiles
        df_quantiles = df_pe.quantile([0.05, 0.5, 0.95])
        # Plot histogram
        binwidth = max(int(len(samples_value_counts)/500), 30 if args.type == "wave" else 3)
        bins_samples = np.arange(min(df_samples["samples"]), max(df_samples["samples"]) + binwidth, binwidth)
        bins_pe = np.arange(min(df_pe["PE"]), max(df_pe["PE"]) + binwidth, binwidth)
        fig, ax = plt.subplots()
        fig.suptitle("Comparison of original and prediction error samples distributions")
        ax.hist(df_samples, bins=bins_samples, log=True, alpha=0.5, label="Original samples")
        ax.hist(df_pe, bins=bins_pe, log=True, alpha=0.5, label="Prediction errors")
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
        # Free hist memory
        plt.close()
        # Cumulative hists
        fig, ax = plt.subplots()
        fig.suptitle("Cumulative distributions of original and prediction error samples")
        xmax = max(df_samples["samples"].max(), df_pe["PE"].max())
        xmin = min(df_samples["samples"].min(), df_pe["PE"].min())
        # Samples cumulative hist
        count, division = np.histogram(df_samples, bins=bins_samples)
        cumulative = np.cumsum(count)
        cumulative = np.append(cumulative, cumulative[len(cumulative)-1])
        ax.plot(np.append(bins_samples[:-1], xmax), cumulative, label="Original samples")
        # PE cumulative hist
        count, division = np.histogram(df_pe, bins=bins_pe)
        cumulative = np.cumsum(count)
        cumulative = np.insert(np.append(cumulative, cumulative[len(cumulative)-1]), 0, cumulative[0])
        ax.plot(np.insert(np.append(bins_pe[:-1], xmax), 0, xmin), cumulative, label="Prediction errors")
        # Title and axis labels
        ax.set_title("File: %s" % (os.path.basename(file)), fontsize=9)
        ax.set_xlabel("Sample value")
        ax.set_ylabel("Number of samples")
        ax.grid()
        ax.legend()
        # Save figure to vectorial graphics pdf
        plt.savefig(file + "_hist_cum.pdf")
        # Free dataframes memory
        del df_samples, df_pe
    # Save ratios dataframe to a CSV file
    df_ratios.to_csv(datetime.now().isoformat() + "-" + "ratios_" + args.type  + ".csv", index=False)
