#!/bin/python3 -u
"""
trace.py [workname] [filepath]
"""
import bosa
import plot_generics
import numpy as np
import sys

def print_help():
    print("traceBOSA [-wl (frequency/wavelength)] [workname] [save path]
['(no)flip']")

"""
Constants, defs (load from jsons in future)
"""
if len(sys.argv) < 2 or len(sys.argv) > 5:
    print_help()
    sys.exit(1)
    
mode = sys.argv[1]
if mode != '-w' and mode != '-l':
    print_help()
    sys.exit(1)

workname = sys.argv[2]
path = sys.argv[3]

flip_axes = sys.argv[4]
if flip_axes == 'flip':
    flip_axes = True
elif flip_axes == 'noflip':
    flip_axes = False
else:
    print_help()
    sys.exit(1) 

# load from json in future
ip = '152.78.75.209'
port = 10000

fname_raw = path + workname + '_raw'
fname_csv = path + workname + '.csv'
fname_plot = path + workname + '.png'
fname_meta = path + workname + '.txt'

"""
Get data
"""
dev = bosa.connect(ip, port)

print("Fetching BOSA trace...")
raw = bosa.get_trace(dev, fname_raw, 'real')
print("done")

print("Parsing BOSA trace...", end='')
data = bosa.parse_trace(fname_raw, fname_csv)
print("done")

print("Writing metadata...", end='')
#bosa.dump_info(dev, fname_meta)
print("done")

#print("total power:", float(bosa.get_power(dev)), "dBm")

bosa.destroy(dev)

"""
Plot
"""
print("Plotting...", end='')
w = np.hsplit(data, 2)[0]
p = np.hsplit(data, 2)[1]

if mode == '-l':
    fig, ax = plot_generics.plot_generic(workname, 'Wavelength (nm)', 'Power (dBm)')
    plot_generics.line(ax, w, p, 'PSD', linewidth=1)
elif mode == '-w':
    fig, ax = plot_generics.plot_generic(workname, 'Frequency (GHz)', 'Power (dBm)')
    plot_generics.line(ax, w, p, 'PSD', linewidth=1)

plot_generics.save(ax, fname_plot)

print("done")
