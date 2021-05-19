# libbk8500

This is a python module that allows for serial communication with BK Precision 85XX Programmable DC Loads. The
repository also contains some example code from BK in a submodule (see the `example` directory). Finally, the command
line tool `power_tool` is installed along with the library. This allows for easy data collection and graphing over a
range of values.

## Installation

The library and tool are packaged as a pip module. Just run

```bash
pip install .
```

while in the `bk8500_library` directory to install the module. To use it in your code, just import the module like so

```python
import libbk8500 as lbk

device = lbk.Device('/dev/ttyUSB0')
packet = lbk.packet.Mode(lbk.packet.LimitModeEnum.CV)
# etc...
```

## Usage
#### API

The `lbk.packet` module contains definitions for every packet that can be sent to the device (See the 
[manual](https://bkpmedia.s3.amazonaws.com/downloads/manuals/en-us/85xx_manual.pdf)). The class `lbk.Device` is used to
create a connection to the device. The constructor must be called with a string which indicates which serial port the
device is connected to. Common addresses are `/dev/ttyUSB0` for Linux and `COM1` for Windows. Device contains a couple
of convenience methods for common operations, and packets can be sent with the `command` method. The `request` method
requests data from the device. A common use case could be

```python
import libbk8500 as lbk

device = lbk.Device('COM1')
device.enable_remote(True)
device.command(lbk.packet.VoltageLevel(10))
device.enable_load(True)
current = device.request(lbk.packet.Measure).amps
```

#### power_tool

The package also installs a script called `power_tool`. This can be used to make measurements over a range of limits
using the device.

`power_tool` has two commands. `power_tool list` shows every serial device currently connected to the computer. This is
useful to find the serial port of the device. `power_tool test` is used for data collection.

The help screen for `power_tool test` is as follows
```bash
$ power_tool test --help
usage: power_tool test [-h] [--device DEVICE] [--baud RATE] [--out OUT | --name NAME] [--flush] [--graph] [--progress] {CC,CV,CW,CR} start stop step delta_t

positional arguments:
  {CC,CV,CW,CR}    the type of test to run (current, voltage, power, or resistance)
  start            the initial value of the limit (inclusive)
  stop             the final value of the limit (inclusive)
  step             the value to step by
  delta_t          the time to wait between steps in seconds

optional arguments:
  -h, --help       show this help message and exit
  --device DEVICE  the address of the serial connection. Defaults to the LBK_DEVICE environment variable
  --baud RATE      the baud rate of the serial connection (default: 9600)
  --out OUT        where to write the csv data to (defaults to stdout)
  --name NAME      the name of the array module under test, saves the plot if plotting is enabled
  --flush, -f      flush the output after every write
  --graph, -g      plot the result after collection
  --progress, -p   display a progress bar to stdout
```

For example, to take a measurement at 100, 200, 300, and 400 Ohms (each lasting 2 seconds), write it to the file
`data.csv`, and show progress along the way, use
```bash
power_tool test --out data.csv --progress CR 100 400 100 2
```

If you are running the test on a specific part, for example an array module labeled `c1`, you can use the `--name`
option instead. This will automatically select an output filename. In addition, this will cause the plot to be saved
with a similar filename if `-g` or `--graph` is selected. For example
```bash
power_tool test --progress --graph CV 0.5 5.5 0.1 0.5 --name c1
```