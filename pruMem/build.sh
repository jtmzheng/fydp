#!/bin/sh
# This creates stuff memory info in cd /sys/class/uio/uio0/maps/map1

dtc -O dtb -I dts -o /lib/firmware/EBB-PRU-ADC.dtbo -b 0 -@ EBB-PRU-ADC.dts
echo EBB-PRU-ADC > $SLOTS
cat $SLOTS
lsmod
rmmod uio_pruss
modprobe uio_pruss extram_pool_sz=0x800000


pasm -V3b pruMem.p
pasm -V3b pruADC.p
gcc dumpSamples.c dataBuffer.c -o dumpSamples
gcc getData.c -o getData -lpthread -lprussdrv
cp dumpSamples /usr/lib/cgi-bin/dumpSamples
chmod +s /usr/lib/cgi-bin/dumpSamples

# Run Makefile
make all
