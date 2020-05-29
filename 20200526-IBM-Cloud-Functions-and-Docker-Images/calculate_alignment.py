import json
import os 
import requests
import librosa
import io
import numpy as np

SAMPLE_RATE = 44100

# function to measure two waveforms with one offset by a certian amount
def measure_error(x0, x1, offset):
    max_len = min(len(x0), len(x1))
    
    # calculate the mean squared error of the two signals
    diff = x0[:max_len] - np.roll(x1[:max_len], offset)
    err = np.sum(diff**2) / len(diff)
    return err

# function to process the signals and get something that 
# we can compare against each other.
def process_signal(o):
    # normalise the values (zscore)
    o = (o - np.mean(o)) / np.std(o)
    # take any values > 2 standard deviations
    o = np.where(o > 2, 1.0, 0.0)
    
    # add an 'decay' to the values such that we can do a more 'fuzzy' match
    # forward pass
    for i in range(1, len(o)):
        o[i] = max(o[i], o[i-1] * 0.9)
        
    # backwards pass
    for i in range(len(o)-2, 0, -1):
        o[i] = max(o[i], o[i+1] * 0.9)
    
    return o


# Find the offest with the lowest error       
def find_offset(x0, x1):
    offsets = tuple(range(-100, 100))
    errors = [ (measure_error(x0, x1, offset), offset) for offset in offsets ]
    
    error, offset = sorted(errors)[0]
                     
    return offset, error


def main(params):

    base_url = """https://github.com/IBMDeveloperUK/ML-For-Everyone/blob/master/20200526-IBM-Cloud-Functions-and-Docker-Images/data/{}?raw=true"""
    
    reference = requests.get(base_url.format(params['reference'])).content
    part = requests.get(base_url.format(params['part'])).content

    # load in the leader
    x0, fs0 = librosa.load(io.BytesIO(reference), 
                           sr=SAMPLE_RATE, mono=True, offset=10, duration=10)

    # load in part
    x1, fs1 = librosa.load(io.BytesIO(part), 
                           sr=SAMPLE_RATE, mono=True, offset=10, duration=10)

    # Normalise the two signals so that they are the same average amplitude (volume)
    x0 = (x0 - np.mean(x0)) / np.std(x0)
    x1 = (x1 - np.mean(x1)) / np.std(x1)

    # Calculate the 'onset strength' of the files, ie where parts start
    o0 = librosa.onset.onset_strength(x0, sr=fs0)
    o1 = librosa.onset.onset_strength(x1, sr=fs1)

    # process the signal of the leader and sarah
    s0 = process_signal(o0)
    s1 = process_signal(o1)

    offset, error = find_offset(s0, s1)
    
    return {"offset": ((offset * 512) / SAMPLE_RATE) * 1000,
            "err": error}



