import psutil
from psutil._common import bytes2human
import time
import signal
import sys

def cpu_ram():
    while True:
        #cpu = psutil.virtual_memory()
        print('MEMORY\n------')
        pprint_ntuple(psutil.virtual_memory())
        #ram = psutil.swap_memory()
        print('\nSWAP\n------')
        pprint_ntuple(psutil.swap_memory())
        #print ("CPU: %" + str(cpu)+ "\tRAM : %" + str(ram))
        time.sleep(15)

def pprint_ntuple(nt):
    for name in nt._fields:
        value = getattr(nt,name)
        if name != 'percent':
            value = bytes2human(value)
        print('%-10s : %7s' % (name.capitalize(), value))


if __name__ == "__main__" :
    cpu_ram()