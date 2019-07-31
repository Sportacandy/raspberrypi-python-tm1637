#!/usr/bin/env python3
#
# Schematic diagram for this clock is available at docs/clock-schematic.png
#
#

from tm1637 import TM1637_OSL40391
from time import time, sleep, localtime
import configparser
import os.path
import os

CLK=24
DIO=23
wakeup_config_file = '/etc/wakeup.ini'
wakeup_config = configparser.ConfigParser()
atomos_config_file = '/etc/bme280.ini'
atomos_config = configparser.ConfigParser()

def show_clock(tm):
    t = localtime()
    if scansleep(tm, 1 - time() % 1):
        return

    tm.numbers(t.tm_hour, t.tm_min, True)
    if scansleep(tm, .5):
        return
    tm.numbers(t.tm_hour, t.tm_min, False)

def scansleep(tm, t):
    while t > 0.1:
        code = tm.scan_key()
        #print('code={:02x}'.format(code))
        if code != 0xff:
            if code == 0xf7:
                os.system('killall -s TERM mpg123')
                enabled = False
                h = 0
                m = 0
                if os.path.isfile(wakeup_config_file):
                    wakeup_config.read(wakeup_config_file)
                    enabled = wakeup_config['user']['enabled'] == str(True)
                    h = int(wakeup_config['user']['hour'])
                    m = int(wakeup_config['user']['minute'])
                if enabled:
                    tm.write(bytearray(b'\x80'), 5)
                    tm.numbers(h, m, True)
                    sleep(0.3)
                    code = tm.scan_key()
                    if code == 0xf7:
                        if display_atomos(tm):
                            return True
                    sleep(2.7)
                else:
                    tm.write(bytearray(b'\x00'), 5)
                    tm.show(' OFF', False)
                    sleep(0.3)
                    code = tm.scan_key()
                    if code == 0xf7:
                        if display_atomos(tm):
                            return True
                    sleep(2.7)
            return True
        sleep(0.1)
        t -= 0.1
    sleep(t)
    return False

def display_atomos(tm):
    if not os.path.isfile(atomos_config_file):
        return False
    atomos_config.read(atomos_config_file)
    t = atomos_config['atomos']['temperature']
    h = atomos_config['atomos']['humidity']
    p = atomos_config['atomos']['pressure']
    pstr = "{:.0f}".format(float(p))
    tm.temperature(float(t))
    sleep(2.5)
    tm.scroll('Humidity')
    tm.percent(float(h))
    sleep(2.5)
    tm.scroll('Air Pressure')
    tm.show(pstr)
    sleep(1.5)
    tm.scroll(pstr + ' hPa', preset=0)
    sleep(0.5)
    return True

    
#print("\n")
#print("============================")
#print(" Starting clock application")
#print("============================")
    
tm = TM1637_OSL40391(CLK, DIO)
tm.brightness(1)
#tm.brightness(7) # 0 <= brightness <= 7
    
while True:
    segments = bytearray(b'\x00')
    if os.path.isfile(wakeup_config_file):
        wakeup_config.read(wakeup_config_file)
        if wakeup_config['user']['enabled'] == str(True):
            segments = bytearray(b'\x80')
    tm.write(segments, 5)
        
    for i in range(10):
        show_clock(tm)

