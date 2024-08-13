# -*- coding: utf-8 -*-
"""
BOSA control scripts

Created on Mon Jul 29 14:50:01 2024

@author: drm1g20
"""

import socket
import struct
import numpy as np
import csv

BUFSIZE = 1024

def connect(ip: str, port: int):
    sock = socket.create_connection((ip, port))
    
    return sock


def write(sock, command: str, rlen=BUFSIZE):
    sock.send(bytes(command, 'utf-8'))

    chunk_size = 4096
    
    if rlen > chunk_size:
        response = bytearray()
        b = 0
        chunks_total = rlen // chunk_size
        chunks = 0
        remaining = rlen
        while True:
            chunk = sock.recv(chunk_size)
            response.extend(chunk)
            remaining -= len(chunk)
            chunks += 1
            #print("chunk received, length", len(chunk), ", remaining", remaining)
            print('\r' + str(chunks) + '/', str(chunks_total), end=' est. ')
            if remaining < chunk_size:
                chunk = sock.recv(remaining)
                response.extend(chunk)
                #print("last chunk received, length", len(chunk))
                print('(' + str(chunks - chunks_total) + ' over)...', end='')
                break
        return response
    
    return sock.recv(rlen)


def get_idn(sock):
    return write(sock, '*idn?')


def get_trace(sock, filename, trace_format="ascii", n_points=0):
    """
    filename is for a raw 2xfloat64 file
    """
    if not n_points:
        if trace_format == 'ascii':
            if write(sock, "format ascii,3") != b'OK\r\n':
                print("Error setting format")
        elif trace_format == 'real':
            if write(sock, "format real") != b'OK\r\n':
                print("Error setting format")
                
        n_points = write(sock, "trace:count?")
    
    trace_data = write(sock, "trace?", 
                       rlen=(int(n_points) * 8 * 2))

    size_est = int(n_points) * 8 * 2
    size_actual = len(trace_data)

    if size_est == size_actual:
        with open(filename, 'wb') as f:
            f.write(trace_data)

        # flush socket because I don't know how they work
        sock.setblocking(0)
        while True:
            try:
                sock.recv(1)
            except:
                break
        sock.setblocking(1)

        return trace_data
    
    else:
        print("Data transfer failure. Retrying.",
              size_actual, "/", size_est, "B")
        
        get_trace(sock, filename, trace_format=trace_format, n_points=n_points)
    


def parse_trace(filename_raw, filename_csv):
    """
    This is a separate function to make it easier to debug.
    filename_raw: 2xfloat64 raw file
    filename_csv: csv filename w/ extension
    """
    f = open(filename_raw, 'rb')
    
    # Even -> wavelength, nm
    # Odd -> power, dBm
    fl = np.frombuffer(f.read(), dtype='d')
    
    f.close()

    w = fl[::2].copy()
    p = fl[1::2].copy()
    
    data = np.stack((w, p), axis=-1)
    
    np.savetxt(filename_csv, data, delimiter=',')

    return data


def get_power(sock):
    if write(sock, "calculate:tpower on") == b'OK\r\n':
        return write(sock, "calculate:tpower?")
    else:
        return 'error'


def dump_info(sock, fname):
    f = open(fname, 'w')

    f.write("Measurement mode: " + str(write(sock, "INSTrument:STATe:MODE?"), encoding='utf-8') + '\n')
    f.write("Polarisation: " + str(write(sock, "INPut:POLarization?"), encoding='utf-8') + '\n')
    f.write("Resolution: " + str(write(sock, "SENSe:WAVelength:RESolution?"), encoding='utf-8') + ' GHz\n')
    f.write("SUT power: " + str(write(sock, "INPut:POWer?"), encoding='utf-8') + ' dBm\n')
    f.write("Points: " + str(write(sock, "trace:count?"), encoding='utf-8') + '\n')
    f.write("Integral power: " + str(get_power(sock), encoding='utf-8') + " dBm\n")

    f.close()


def destroy(sock):
    sock.close()
