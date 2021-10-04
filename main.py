from setup import *
import signal
import matplotlib.pyplot as plt
import numpy as np


def signal_handler(signal, frame):
    global interrupted
    interrupted = True

signal.signal(signal.SIGINT, signal_handler)
interrupted = False


port = 'ASRL6::INSTR'       # RS-232
file_path = '/Users/'

while True:
    print("Data Saving...")
    scope = Tektronix(port)
    ch1_param, ch2_param = get_waveform_parameters(scope)
    ch1_volt, ch2_volt = get_ascii_voltage(scope)
    WFM_time1, WFM_voltage1 = get_WFM(ch1_volt, ch1_param)
    WFM_time2, WFM_voltage2 = get_WFM(ch2_volt, ch2_param)
    save_file(file_path, WFM_time1, WFM_voltage1, WFM_voltage2)
    print("Data saved successfully!")

    # Comment the following if don't want live WFM display
    plt.ion()
    plt.subplots_adjust(hspace=0.13, top=0.9, bottom=0.112, left=0.16, right=0.93)
    plt.plot(WFM_time1, WFM_voltage1, label='Channel 1', c='darkorange')
    plt.axhline(np.average(WFM_voltage1), c='darkorange', ls=':')
    plt.plot(WFM_time2, WFM_voltage2, label='Channel 2', c='navy')
    plt.axhline(np.average(WFM_voltage2), c='navy', ls=':')
    plt.xlabel('Time (s)', fontsize=13)
    plt.ylabel('Voltage (V)', fontsize=13)
    plt.title('Live Updating Waveform', fontsize=14)
    plt.legend(fancybox=False, framealpha=0.7, edgecolor='k', loc='upper right')
    # plt.ylim(.116, -.284)
    plt.draw()
    plt.show()
    plt.pause(0.00001)

    plt.close()

    if interrupted:
        print("*******SAVING INTERRUPTED!*******")
        break