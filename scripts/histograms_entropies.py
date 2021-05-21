#!/usr/bin/env python3
from datetime import datetime
from io import StringIO
from negentropy_estimation import negentropy
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

def cmpHist(df_samples, df_pe):
    # Find 0.05, 0.5 and 0.95 quantiles
    df_quantiles = df_pe.quantile([0.05, 0.5, 0.95])
    # Plot histogram
    samples_value_counts = df_samples["samples"].value_counts()
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

def cumHist(df_samples, df_pe):
    # Cumulative hists
    fig, ax = plt.subplots()
    fig.suptitle("Cumulative distributions of original and prediction error samples")
    xmax = max(df_samples["samples"].max(), df_pe["PE"].max())
    xmin = min(df_samples["samples"].min(), df_pe["PE"].min())
    # Samples cumulative hist
    samples_value_counts = df_samples["samples"].value_counts()
    count, division = np.histogram(df_samples, bins=len(samples_value_counts))
    cumulative = np.cumsum(count)
    cumulative = np.insert(np.append(cumulative, cumulative[len(cumulative)-1]), 0, 0)
    ax.step(np.insert(np.append(division[:-1], xmax), 0, xmin), cumulative, label="Original samples", where="post")
    # PE cumulative hist
    pe_value_counts = df_pe["PE"].value_counts()
    count, division = np.histogram(df_pe, bins=len(pe_value_counts))
    cumulative = np.cumsum(count)
    cumulative = np.insert(np.append(cumulative, cumulative[len(cumulative)-1]), 0, 0)
    ax.step(np.insert(np.append(division[:-1], xmax), 0, xmin), cumulative, label="Prediction errors", where="post")
    # Title and axis labels
    ax.set_title("File: %s" % (os.path.basename(file)), fontsize=9)
    ax.set_xlabel("Sample value")
    ax.set_ylabel("Number of samples")
    ax.grid()
    ax.legend()
    # Save figure to vectorial graphics pdf
    plt.savefig(file + "_hist_cum.pdf")
    # Free memory
    plt.close()

def negentropies(df_samples, df_pe):
    smp = df_samples["samples"].to_numpy().astype(np.float)
    pe = df_pe["PE"].to_numpy().astype(np.float)
    J_smp = negentropy(smp)
    J_pe = negentropy(pe)
    return pd.Series([J_smp, J_pe], index=["J_smp", "J_pe"])

if __name__ == "__main__":
    args = setupParser().parse_args()
    # Dataframe negentropies
    df_entropies = pd.DataFrame(columns=["file", "J_smp", "J_pe"])
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
        row = 0 if pd.isnull(df_entropies.index.max()) else df_entropies.index.max() + 1
        df_entropies.loc[row] = round(negentropies(df_samples, df_pe), 4)
        df_entropies.loc[row, "file"] = os.path.basename(file)
        # Histogram
        cmpHist(df_samples, df_pe)
        # Cumulative histograms
        cumHist(df_samples, df_pe)
        del df_samples, df_pe
    # Save ratios dataframe to a CSV file
    df_entropies.to_csv(datetime.now().isoformat() + "-" + "results_" + args.type  + ".csv", index=False)
