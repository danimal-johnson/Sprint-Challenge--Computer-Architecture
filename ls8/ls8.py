#!/usr/bin/env python3

"""Main."""

import sys
from cpu import *

cpu = CPU()

if len(sys.argv) == 2:
    cpu.load(sys.argv[1])
else:
    cpu.load()

cpu.run()
