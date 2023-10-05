# MTUInspector
  __  __ _____ ____  _____
 |  \/  |_   _/ ___|| ____|
 | |\/| | | | \___ \|  _|
 | |  | | | |  ___) | |___
 |_|  |_| |_| |____/|_____|

MTUProbe is a tool designed to help network administrators and enthusiasts debug MTU (Maximum Transmission Unit) issues in their network.

## Features
* Test and determine the optimal MTU value for a path.
* Supports dual-interface mode for comprehensive testing.
* Verbose mode for in-depth analysis.
* Option to set or unset the "Do Not Fragment" flag.
* Works on both Windows and Unix-like systems.

## Installation

1. Clone this repository:
```
git clone https://github.com/your_username/MTUProbe.git
```
2. Navigate to the directory:
```
cd MTUProbe
```

## Usage

To use MTUProbe in a standard mode:
```
python mtuprobe.py --target TARGET_IP
```

For advanced usage, dual-interface tests, and other options:
```
python mtuprobe.py --help
```

## Author
* Fer Valdovinos
* Luis Cosio
