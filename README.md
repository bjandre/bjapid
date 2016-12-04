# PID controller library

Simple PID, proportional-integral-derivative, controller library. The
implementation is a plain C library with no dependancies so it can be
used on a microcontroller or in a numerical simulation.  Uses single
precision floating point, so it is only appropriate for for embedded
systems with FPU. Simple python interface for driving numerical
simulations.

This is a learning toy. Please don't use it if you are doing serious
control work. Try something like the PID interface defined in the ARM
CMSIS-DSP.

C based unit tests, systems level testing through a python interface.

# Installation

## Requirements

* C11 compiler

* python 3.5, numpy, matplotlib

## Build

Build has only been testing on macOS with clang-800.0.42.1.

* C static library

```SHELL

    cd src
    make staticlib

```

* unit testing with cmocka

```SHELL

    cd 3rd-party
    make cmocka
    cd ../src
    make test

```

* build dynamic library for python driver, macOS only

```SHELL

    cd src
    make dylib
    
    pid-driver.py --help

```
