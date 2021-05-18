#!/usr/bin/env python
import argparse
import libbk8500 as lbk
from serial.tools import list_ports
import os
import sys
import csv
import time
import numpy as np
from matplotlib import pyplot as plt


def print_progress(start, stop, value, unit, length=20):
    progress = value - start
    total = stop - start
    percent = progress / total
    slot = int(percent * length)

    def bar_char(val):
        if val < slot:
            return '='
        elif val == slot:
            return '>'
        else:
            return ' '

    bar = ''.join(bar_char(i) for i in range(length))
    print(f' {value:8.3} {unit} [{bar}]', end='\r')
    sys.stdout.flush()


def run_test(device_addr, type, start, stop, step, delta_t, out, flush, plot, progress, name):
    print(f'Connecting to {device_addr}')
    unit, label = {
        lbk.packet.LimitModeEnum.CC: ('A', 'Current'),
        lbk.packet.LimitModeEnum.CV: ('V', 'Voltage'),
        lbk.packet.LimitModeEnum.CW: ('W', 'Power'),
        lbk.packet.LimitModeEnum.CR: ('Ω', 'Resistance'),
    }[type]
    device = lbk.Device(device_addr)
    device.enable_remote(True)
    device.enable_load(False)
    device.command(lbk.packet.Mode(type))
    device.set_level(type, start)
    device.enable_load(True)

    fieldnames = [f'Requested {label} ({unit})', 'voltage (V)', 'current (A)', 'power (W)']
    writer = csv.writer(out)
    writer.writerow(fieldnames)
    if flush:
        out.flush()
    data = []

    value = start
    while (value <= stop and step > 0) or (value >= stop and step < 0):
        if progress:
            print_progress(start, stop, value, unit)
        device.set_level(type, value)
        time.sleep(delta_t)
        meas = device.request(lbk.packet.Measure)
        row = (value, meas.volts, meas.amps, meas.watts)
        writer.writerow(row)
        if flush:
            out.flush()
        if plot:
            data.append(row)
        value += step

    if progress:
        print()

    print(f'Max Power: {max(record[3] for record in data)} W')

    if plot:
        ar = np.array(data)
        fig, axs = plt.subplots(3, sharex=True)
        fig.suptitle('Power Measurements')
        for ax in axs:
            ax.grid(True)
        axs[0].scatter(ar[:, 0], ar[:, 1])
        axs[0].set_ylabel('Voltage (V)')
        axs[1].scatter(ar[:, 0], ar[:, 2])
        axs[1].set_ylabel('Current (A)')
        axs[2].scatter(ar[:, 0], ar[:, 3])
        axs[2].set_ylabel('Power (W)')
        axs[2].set_xlabel(f'Requested {label} ({unit})')
        if name is not None:
            plt.savefig(f'{name}.png')
        else:
            plt.show()


def power_tool():
    parser = argparse.ArgumentParser(description='Make measurments using a BK Precision 85XX DC Load')
    parser.set_defaults(which=None)
    subparsers = parser.add_subparsers(help='action to perform')
    list_device = subparsers.add_parser('list', help='list connected serial devices')
    list_device.set_defaults(which='list')
    test = subparsers.add_parser('test', help='run a test and collect data')
    test.add_argument('--device', type=str, help='the address of the serial connection. Defaults to the LBK_DEVICE '
                                                 'environment variable', default=os.environ.get('LBK_DEVICE'))
    test.add_argument('--baud', type=int, help='the baud rate of the serial connection (default: 9600)', default=9600,
                      metavar='RATE')
    output_group = test.add_mutually_exclusive_group()
    output_group.add_argument('--out', type=argparse.FileType('w'), default=sys.stdout,
                      help='where to write the csv data to (defaults to stdout)')
    output_group.add_argument('--name', action='store', type=str, default=None,
                      help='the name of the array module under test, saves the plot if plotting is enabled')
    test.add_argument('--flush', '-f', action='store_true', help='flush the output after every write')
    test.add_argument('--graph', '-g', action='store_true', help='plot the result after collection')
    test.add_argument('--progress', '-p', action='store_true', help='display a progress bar to stdout')
    test.add_argument('kind', type=lbk.packet.LimitModeEnum.from_string, choices=list(lbk.packet.LimitModeEnum),
                      help='the type of test to run (current, voltage, power, or resistance)')
    test.add_argument('start', type=float, help='the initial value of the limit (inclusive)')
    test.add_argument('stop', type=float, help='the final value of the limit (inclusive)')
    test.add_argument('step', type=float, help='the value to step by')
    test.add_argument('delta_t', type=float, help='the time to wait between steps in seconds')
    test.set_defaults(which='test')

    args = parser.parse_args()

    if args.which == 'list':
        print('Available Serial Devices:')
        for port in list_ports.comports():
            print(f'\t{port.device}: {port.manufacturer} {port.description}')
    elif args.which == 'test':
        if args.device == None:
            print('No device selected, please specify a device with --device or the LBK_DEVICE environment variable')
            sys.exit()
        if args.step == 0:
            print('step cannot be zero')
            sys.exit()
        if args.name is not None:
            args.out = open(f'{args.name}.csv', 'w')
        if args.out == sys.stdout:
            args.progress = False
        run_test(args.device, args.kind, args.start, args.stop, args.step, args.delta_t, args.out, args.flush,
                 args.graph, args.progress, args.name)
    else:
        parser.print_help()


if __name__ == '__main__':
    power_tool()
