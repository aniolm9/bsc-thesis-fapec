#!/usr/bin/env python3

import argparse
from scipy.stats import entropy
import matplotlib.pyplot as plt
from matplotlib import rc
import pandas as pd
import os
import sys

def setupParser():
    parser = argparse.ArgumentParser(description='Plot histograms.')
    #parser.add_argument('-t', '--type', type=str, help='Data structure type to process. Accepted types are: kmall, wave.', required=True)
    parser.add_argument('files', metavar='FILES', type=str, nargs='+', help='List of files to plot a histogram of.')
    return parser

def checkInputFiles(files):
    for f in files:
        if not os.path.exists(f):
            print("File %s does not exist." % (f))
            sys.exit(0)


if __name__ == "__main__":
    args = setupParser().parse_args()
    # Use Computer Modern for graphics.
    #rc('font', **{'family': 'serif', 'serif': ['Computer Modern']})
    #rc('text', usetex=True)
    for f in args.files:
        # Create variables for prediction error and original samples files.
        peFile = f + ".pe"
        samplesFile = f + ".samples"
        # Check if both files exist.
        checkInputFiles([peFile, samplesFile])
        # Create dataframe with two columns: prediction errors and original samples.
        df = pd.read_csv(peFile, delimiter = "\n", header=None, names=["PE"])
        df["samples"] = pd.read_csv(samplesFile, delimiter = "\n", header=None, dtype=int)[0]
        # Calculate prediction error probabilities.
        probs = df["PE"].value_counts()/len(df["PE"])
        # Find theoretical ratio from Shannon entropy.
        ratio = 8/entropy(probs, base=2)
        print("Theoretical ratio \t %.3f" % (ratio))
        # Plot histogram.
        ax = df[["PE", "samples"]].plot.hist(bins=10, log=False, alpha=0.5)
        ax.set_title("Histogram of prediction errors")
        ax.set_xlabel("Sample prediction errors")
        ax.set_ylabel("Number of samples")
        #plt.savefig("hist.pdf")
        plt.show()
