#!/usr/bin/env python3
from matplotlib.ticker import FormatStrFormatter
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import numpy as np
import subprocess
import argparse
import time
import os

def setupParser():
    parser = argparse.ArgumentParser(description='Plot histograms.')
    parser.add_argument('-d', '--directory', type=str, help='Path to the directory of the files in the CSV.')
    parser.add_argument('csv', metavar='CSV', type=str, help='Path to CSV file generated by histograms.py.')
    return parser

def getRatios(file):
    file = os.path.join(args.directory, file)
    # Original file size
    orig_size = os.path.getsize(file)
    # FAPEC ratio
    start = time.time()
    result = subprocess.check_output('fapec -qq -mt 1 -chunk 4M -dtype kmall -kmopts 0 0 0 -ow -o /dev/stdout ' + '"' + file + '"', shell=True)
    end = time.time()
    fapec_time = round(end - start, 4)
    fapec_size = len(result)
    ratio_fapec = round(orig_size / fapec_size, 3)
    # Gzip ratio
    start = time.time()
    result = subprocess.check_output('gzip -q -c "' + file + '"', shell=True)
    end = time.time()
    gzip_time = round(end - start, 4)
    gzip_size = len(result)
    ratio_gzip = round(orig_size / gzip_size, 3)
    return pd.Series([ratio_fapec, ratio_gzip, fapec_time, gzip_time], index=["ratio_fapec", "ratio_gzip", "time_fapec", "time_gzip"])

def plotCompare(df):
    fig, ax = plt.subplots(constrained_layout=True)
    fig.suptitle("Comparison of FAPEC, FLAC and GZIP")
    markers = ["x", "o", "v", "^", "s"]
    unicode_markers = [u"✕", u"•", u"▼", u"▲", u"◼️"]
    title = ""
    for i, row in df.iterrows():
        ax.plot(row["time_fapec"], 1/row["ratio_fapec"], "b" + markers[i], label="FAPEC")
        ax.plot(row["time_gzip"], 1/row["ratio_gzip"], "r" + markers[i], label="GZIP")
        title += "File: %s (%s)\n" % (row["file"], unicode_markers[i])
    ax.legend(["FAPEC", "GZIP"])
    ax.grid()
    ax.set_title(title, fontsize=9)
    ax.set_xlabel("Process time [s]")
    ax.set_ylabel("Compression ratio")
    xlim = [0, ax.get_xlim()[1]]
    ylim = [0, ax.get_ylim()[1]]
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.xaxis.set_major_formatter(FormatStrFormatter('%.3f'))
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.3f'))
    # Save figure to vectorial graphics pdf
    plt.savefig(os.path.join(args.directory, args.csv + "_comparison.pdf"))
    plt.close()

if __name__ == "__main__":
    args = setupParser().parse_args()
    df = pd.read_csv(args.csv)
    df = pd.concat([df, df.file.apply(getRatios)], axis=1)
    # Plot diagram and calculate Euclidean distances
    plotCompare(df)
    df["distance_fapec"] = df.apply(lambda row: round(np.linalg.norm([row["time_fapec"], 1/row["ratio_fapec"]]), 4), axis=1)
    df["distance_gzip"] = df.apply(lambda row: round(np.linalg.norm([row["time_gzip"], 1/row["ratio_gzip"]]), 4), axis=1)
    df.to_csv(args.csv, index=False)
