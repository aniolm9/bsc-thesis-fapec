#!/usr/bin/env python3
from scipy.stats import entropy
from matplotlib import rc
import wave.wave_samples as wave_samples
import kmall.mwc_samples as mwc_samples
import matplotlib.pyplot as plt
import pandas as pd
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
    origFile, extension = os.path.splitext(file)
    # Generate .pe from input .wav file using a bash pipeline (faster)
    if extension == ".pe":
        subprocess.run(["wave/wave_pe.sh", origFile], stdout=subprocess.DEVNULL)
    # Extract data samples from the .wav file
    elif extension == ".samples":
        wave_samples.samplesToFile(origFile)
    else:
        sys.exit(-1)

def kmallGenerator(file):
    origFile, extension = os.path.splitext(file)
    # Generate .pe from .kmwcd using a bash pipeline
    if extension == ".pe":
        subprocess.run(["kmall/kmall_pe.sh", origFile], stdout=subprocess.DEVNULL)
    # Make use of the kmall python API to find MWC samples
    elif extension == ".samples":
        mwc_samples.samplesToFile(origFile)
    else:
        sys.exit(-1)


if __name__ == "__main__":
    args = setupParser().parse_args()
    # Use Computer Modern for graphics.
    rc('font', **{'family': 'sans-serif', 'sans-serif': ['Helvetica']})
    rc('text', usetex=True)
    for file in args.files:
        print("Processing " + file + "...")
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
        bitsPerSample = 16 if args.type == "wave" else 8
        ratio = bitsPerSample/entropy(probs, base=2)
        print("Theoretical ratio \t %.3f" % (ratio))
        # Plot histogram.
        ax = df[["PE", "samples"]].plot.hist(bins=400, log=True, alpha=0.5)
        ax.set_title("Histogram of prediction errors")
        ax.set_xlabel("Sample prediction errors")
        ax.set_ylabel("Number of samples")
        plt.savefig(file + "_hist.pdf")
        #plt.show()
