import pyvisa as visa
import csv
from datetime import datetime


channel_list = ['CH1', 'CH2']

def Tektronix(port_address):
    """
    Scope configuration and setup
    :param port_address:
    :return:
    """
    rm = visa.ResourceManager()
    scope = rm.open_resource(port_address)
    scope.write('DATA:WIDTH 1')
    scope.write('DATa:ENC ASCii')

    return scope


def get_waveform_parameters(scope):
    """
    Get displayed waveform parameters
    :param scope:
    :return:
    """
    channel_param_key = ['YMUlt', 'YZEro', 'YOFf', 'YUNit', 'XINcr', 'XZEro', 'XUNit', 'PT_Off', 'NR_Pt']
    channel_1_param = {key: None for key in channel_param_key}
    channel_2_param = {key: None for key in channel_param_key}

    for channel in channel_list:
        scope.write("DATA:SOURCE " + channel)

        # get voltage parameters (y related parameter)
        YMUlt = float(scope.query('WFMPRE:YMULT?'))         # Returns the vertical scale factor
        YZEro = float(scope.query('WFMPRE:YZERO?'))         # Returns the offset voltage
        YOFf = float(scope.query('WFMPRE:YOFF?'))           # Returns the vertical position
        YUNit = scope.query('WFMPre:YUNit?')                # Returns the vertical units

        # get time parameters (x parameters)
        XINcr = float(scope.query('WFMPRE:XINCR?'))         # Returns the horizontal sampling interval
        XZEro = float(scope.query('WFMPre:XZEro?'))         # Returns the time of first points in a waveform
        XUNit = scope.query('WFMPre:XUNit?')                # Returns the horizontal units
        PT_Off = float(scope.query('WFMPre:PT_Off?'))       # Query trigger offset

        # get number of points
        NR_Pt = int(scope.query('WFMPre:NR_Pt?'))           # Query the number of pts in the curve transfer from the scope

        temp_param = [YMUlt, YZEro, YOFf, YUNit, XINcr, XZEro, XUNit, PT_Off, NR_Pt]
        if channel == 'CH1':
            channel_1_param = dict(zip(channel_1_param, temp_param))
        if channel == 'CH2':
            channel_2_param = dict(zip(channel_2_param, temp_param))

    return channel_1_param, channel_2_param


def get_ascii_voltage(scope):
    ascii_voltage_channel1 = []
    ascii_voltage_channel2 = []

    for channel in channel_list:
        scope.write("DATA:SOURCE " + channel)
        data = scope.query('CURVe?')
        data = data.split(',')
        data[-1] = data[-1].split('\n')[0]
        data = [float(i) for i in data]

        if channel == 'CH1':
            ascii_voltage_channel1 = data
        if channel == 'CH2':
            ascii_voltage_channel2 = data

    return ascii_voltage_channel1, ascii_voltage_channel2


def get_WFM(ascii_voltage: list, WFM_param: dict):
    YZEro = WFM_param['YZEro']
    YMUlt = WFM_param['YMUlt']
    YOFf = WFM_param['YOFf']
    XINcr = WFM_param['XINcr'] * 1e2
    XZEro = WFM_param['XZEro']
    PT_Off = WFM_param['PT_Off']

    NR_Pt = WFM_param['NR_Pt']

    WFM_voltage = [YZEro + (YMUlt * (i - YOFf)) for i in ascii_voltage]     # unit [V]
    WFM_time = [XZEro + XINcr * (i - PT_Off) for i in range(NR_Pt)]         # unit [s]

    return WFM_time, WFM_voltage

def save_file(file_path, WFM_time, WFM_voltage_CH1, WFM_voltage_CH2):
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    with open(file_path + 'WFM' + '_' + str(current_time) + '.csv', mode='w') as opf:
        writer = csv.writer(opf, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['time (s)', 'Channel1 (V)', 'Channel2 (V)'])
        writer.writerows(zip(WFM_time, WFM_voltage_CH1, WFM_voltage_CH2))


# if __name__ == '__main__':
#     port = 'ASRL6::INSTR'  # RS-232
#     scope = Tektronix(port)
#     ch1_param, ch2_param = get_waveform_parameters(scope)
#     ch1_volt, ch2_volt = get_ascii_voltage(scope)
#     WFM_time1, WFM_voltage1 = get_WFM(ch1_volt, ch1_param)
#     WFM_time2, WFM_voltage2 = get_WFM(ch2_volt, ch2_param)
#     file_path ='/Users/'
#     save_file(file_path, WFM_time1, WFM_voltage1, WFM_voltage2)
