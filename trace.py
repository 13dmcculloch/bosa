#!/bin/python3 -u
"""
trace.py [workname] [filepath]
"""
import numpy as np
import sys
import os
import json

sys.path.append('/usr/local/include/bosa')

import bosa
import plot_generics

def print_help():
    print("traceBOSA [-wl (frequency/wavelength)] [workname] [save path] \
[\'(no)flip\']")

"""
Constants, defs (load from jsons in future)
"""
config_path = os.path.expanduser("~") + '/.local/bosa/config.json'
f = open(config_path, 'r')
if f.closed:
  print("Failed to open config file at", config_path)
  sys.exit(1)
d = json.load(f)
f.close()

if len(sys.argv) < 2 or len(sys.argv) > 5:
    print_help()
    sys.exit(1)
    
mode = sys.argv[1]
if mode != '-w' and mode != '-l':
    print_help()
    sys.exit(1)

workname = sys.argv[2]
path = sys.argv[3] + '/'

flip_axes = sys.argv[4]
if flip_axes == 'flip':
    flip_axes = True
elif flip_axes == 'noflip':
    flip_axes = False
else:
    print_help()
    sys.exit(1) 

ip4 = 0
port = 0

if 'addr4' in d.keys():
  ip4 = d['addr4']
if 'port' in d.keys():
  port = d['port']
if 'addr6' in d.keys():
  print("IPv6 support not implemented. BOSA network config dialog shows IPv4
  only, but registers an IPv6 address anyway so it is possible.")

if not ip4 or not port:
  print("Failed to load IPv4 address and port from", config_path)
  sys.exit(1)

fname_raw = path + workname + '_raw'
fname_csv = path + workname + '.csv'
fname_plot = path + workname + '.png'
fname_meta = path + workname + '.txt'

"""
Get data
"""
dev = bosa.connect(ip4, port)

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
if flip_axes:
  w = np.hsplit(data, 2)[1]
  p = np.hsplit(data, 2)[0]
else:
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
