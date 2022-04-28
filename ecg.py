import logging
import matplotlib.pyplot as plt
import math
import json
from scipy.signal import find_peaks, butter, filtfilt


def main():
    filename = 'test_data/test_data11.csv'
    logging.basicConfig(filename="ecg.log", level=logging.INFO, filemode="w")
    time, voltage, sampling_frequency = readFile(filename)
    voltage = process_data(voltage, sampling_frequency)
    metrics = make_metrics(time, voltage)
    output_json(filename, metrics)
    return


def readFile(filename):
    """reads data from a csv file and
    returns time and voltage as lists,
    and the sampling frequency.

    Parameters
    ----------
    filename : string
        directory and the name of the file to read

    Returns
    -------
    time : list
        time array
    voltage : list
        voltage array
    sampling_frequency : integer
        sampling frequency of the data

    """
    logging.info("Starting analysis of ECG data...")
    time = []
    voltage = []
    f = open(filename, 'r')
    line_number = 0
    while(1):
        line_number += 1
        line = f.readline()
        if line == "":
            break

        line = line.rstrip('\n')
        row = line.split(',')

        if row[0] == '' or row[1] == '':
            logging.error("there is an empty cell in line {}"
                          .format(line_number))
            continue
        if is_number(row[0]) is False or is_number(row[1]) is False:
            logging.error("there was a non-numeric input in line {}"
                          .format(line_number))
            continue
        row = [float(i) for i in row]
        if math.isnan(row[0]) or math.isnan(row[1]):
            logging.error("There is a NaN cell in line {}".format(line_number))
            continue
        time.append(row[0])
        voltage.append(row[1])

    if max(voltage) > 300 or min(voltage) < -300:
        logging.warning(
            "In the input file {},voltage exceed the normal range"
            .format(filename))
    sampling_frequency = len(time)/time[-1]
    return time, voltage, sampling_frequency


def process_data(voltage, sampling_frequency):
    """Removes low frequency and high frequency noise
    using bandpass filter.

    Parameters
    ----------
    voltage : list
        contains voltages per each time
    sampling_frequency : integer
        sampling frequency of the data

    Returns
    -------
    y : list
        filtered voltage data

    """
    low = 1/sampling_frequency
    high = 50/sampling_frequency
    b, a = butter(1, [low, high], 'bandpass')
    y = filtfilt(b, a, voltage, method='pad', padlen=100, padtype='constant')
    return y


def make_metrics(time, voltage):
    """Outputs calculated data into a dictionary

    Parameters
    ----------
    time : list
        time vector
    voltage : list
        voltage vector

    Returns
    -------
    metrics : dictionary
        Contains duration, voltage extremes, beats,
        number of beats, and bpm

    """
    duration = max(time)
    logging.info("The duration was {} seconds".format(duration))
    voltage_extremes = (min(voltage), max(voltage))
    logging.info("The voltage max was {}, and the min was {}"
                 .format(voltage_extremes[0], voltage_extremes[1]))
    beats = when_beats(time, voltage)
    logging.info("The beats occurred at times following {}".format(beats))
    num_beats = len(beats)
    logging.info("Number of beats: {}".format(num_beats))
    mean_hr_bpm = cal_bpm(num_beats, duration)
    logging.info("bpm: {}".format(mean_hr_bpm))
    metrics = {
        "duration": duration,
        "voltage_extremes": voltage_extremes,
        "num_beats": num_beats,
        "mean_hr_bpm": mean_hr_bpm,
        "beats": beats
    }
    return metrics


def when_beats(time, voltage):
    """
    Find when the heartbeat occurs

    Parameters
    ----------
    time : list
        time vector
    voltage : list
        voltage vector

    Returns
    -------
    peakTime : list
        contains times that heartbeat occurred.

    """
    peaks, _ = find_peaks(voltage, prominence=0.6, distance=150, height=0.35)
    peaks = peaks.tolist()

    peakVol = [voltage[peak] for peak in peaks]
    peakTime = [time[peak] for peak in peaks]
    if voltage[-1] > 0.35:
        peakTime.append(time[-1])
        peakVol.append(voltage[-1])
    # plt.plot(time, voltage)
    # plt.plot(peakTime, peakVol, "x")
    # plt.show()
    # (peakTime)
    # print(len(peakTime))
    return peakTime


def cal_bpm(num_beats, duration):
    """
    calculates beats per minute (bpm)

    Parameters
    ----------
    num_beats : integer
        number of beats within the duration
    duration : float
        duration of time measured

    Returns
    -------
    bpm : integer
        beats per minute

    """
    bpm = int(round(num_beats/duration*60))
    return bpm


def is_number(string):
    """
    Checks whether the input string is numeric

    Parameters
    ----------
    string : string
        input string that wants to be checked

    Returns
    -------
    bool
        true if the string is numeric
        false if the string is non-numeric

    """
    try:
        float(string)
        return True
    except ValueError:
        return False


def output_json(filename, metrics):
    """
    Output a json file including the diagnostics

    Parameters
    ----------
    filename : string
        data file name
    metrics : dictionary
        contains the diagnostics from ecg data

    Returns
    -------
    None.

    """
    splitted = filename.split('.')
    name = splitted[0]
    out_file = open('{}.json'.format(name), 'w')
    json.dump(metrics, out_file)
    out_file.close()


def calc_hr(time, voltage):
    global bpm
    num_beats = len(when_beats(time, voltage))
    duration = time[-1]
    bpm = cal_bpm(num_beats, duration)
    return bpm


if __name__ == "__main__":
    main()
