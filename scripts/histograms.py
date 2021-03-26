#!/usr/bin/env python3
from scipy.stats import entropy
from matplotlib import rc
import matplotlib.pyplot as plt
import pandas as pd
import argparse
import os
import sys


def setupParser():
    parser = argparse.ArgumentParser(description='Plot histograms.')
    parser.add_argument('-t', '--type', type=str, choices=['wave', 'kmall'], help='Data structure type to process.', required=True)
    parser.add_argument('-a', '--auto', dest="auto", action='store_true', help='Automatically generate missing files, if possible.', required=False)
    parser.add_argument('files', metavar='FILES', type=str, nargs='+', help='List of files to plot a histogram of.')
    return parser

def checkInputFiles(origFile):
    files = [origFile + ".samples", origFile + ".pe"]
    for file in files:
        if not os.path.exists(file) or not os.path.exists(file):
            createFile = "y" if args.auto else input("File %s does not exist. Do you want to create it [y/N]? " % (file)).lower()
            # If the original file does not exist or we don't want to generate .pe and .samples, we exit.
            if not os.path.exists(os.path.splitext(file)[0]) or createFile != "y":
                sys.exit(-1)
            # Generate missing .pe or .samples files for the given file and type.
            if args.type == "wave":
                waveGenerator(file)
            elif args.type == "kmall":
                kmallGenerator(file)

def waveGenerator(file):
    extension = os.path.splitext(file)[1]
    if extension == ".pe":
        pass
    elif extension == ".samples":
        pass
    else:
        sys.exit(-1)

def kmallGenerator(file):
    extension = os.path.splitext(file)[1]
    if extension == ".pe":
        pass
    elif extension == ".samples":
        pass
    else:
        sys.exit(-1)


if __name__ == "__main__":
    args = setupParser().parse_args()
    # Use Computer Modern for graphics.
    #rc('font', **{'family': 'serif', 'serif': ['Computer Modern']})
    #rc('text', usetex=True)
    for file in args.files:
        # Create variables for prediction error and original samples files.
        peFile = file + ".pe"
        samplesFile = file + ".samples"
        # Check if both files exist.
        checkInputFiles(file)
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
