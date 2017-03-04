# call this at the start of using the beaglebone, sets up the device tree, and calls source /.profile.
cd ~

source .profile

cd /lib/firmware
dtc -O dtb -o /lib/firmware/bspm_P8_45_2e-00A0.dtbo -b 0 -@ /lib/firmware/bspm_P8_45_2e-00A0.dts
echo bspm_P8_45_2e > /sys/devices/bone_capemgr.?/slots

dtc -O dtb -o /lib/firmware/bspm_P8_46_2e-00A0.dtbo -b 0 -@ /lib/firmware/bspm_P8_46_2e-00A0.dts
echo bspm_P8_46_2e > /sys/devices/bone_capemgr.?/slots

dtc -O dtb -o /lib/firmware/bspm_P8_43_2e-00A0.dtbo -b 0 -@ /lib/firmware/bspm_P8_43_2e-00A0.dts
echo bspm_P8_43_2e > /sys/devices/bone_capemgr.?/slots

dtc -O dtb -o /lib/firmware/bspm_P8_44_2e-00A0.dtbo -b 0 -@ /lib/firmware/bspm_P8_44_2e-00A0.dts
echo bspm_P8_44_2e > /sys/devices/bone_capemgr.?/slots

dtc -O dtb -o /lib/firmware/bspm_P8_41_2e-00A0.dtbo -b 0 -@ /lib/firmware/bspm_P8_41_2e-00A0.dts
echo bspm_P8_41_2e > /sys/devices/bone_capemgr.?/slots

dtc -O dtb -o /lib/firmware/bspm_P8_42_2e-00A0.dtbo -b 0 -@ /lib/firmware/bspm_P8_42_2e-00A0.dts
echo bspm_P8_42_2e > /sys/devices/bone_capemgr.?/slots

dtc -O dtb -o /lib/firmware/bspm_P8_39_2e-00A0.dtbo -b 0 -@ /lib/firmware/bspm_P8_39_2e-00A0.dts
echo bspm_P8_39_2e > /sys/devices/bone_capemgr.?/slots

dtc -O dtb -o /lib/firmware/bspm_P8_40_2e-00A0.dtbo -b 0 -@ /lib/firmware/bspm_P8_40_2e-00A0.dts
echo bspm_P8_40_2e > /sys/devices/bone_capemgr.?/slots

dtc -O dtb -o /lib/firmware/bspm_P8_27_2e-00A0.dtbo -b 0 -@ /lib/firmware/bspm_P8_27_2e-00A0.dts
echo bspm_P8_27_2e > /sys/devices/bone_capemgr.?/slots

dtc -O dtb -o /lib/firmware/bspm_P8_29_2e-00A0.dtbo -b 0 -@ /lib/firmware/bspm_P8_29_2e-00A0.dts
echo bspm_P8_29_2e > /sys/devices/bone_capemgr.?/slots

dtc -O dtb -o /lib/firmware/bspm_P8_28_2e-00A0.dtbo -b 0 -@ /lib/firmware/bspm_P8_28_2e-00A0.dts
echo bspm_P8_28_2e > /sys/devices/bone_capemgr.?/slots

dtc -O dtb -o /lib/firmware/bspm_P8_30_2e-00A0.dtbo -b 0 -@ /lib/firmware/bspm_P8_30_2e-00A0.dts
echo bspm_P8_30_2e > /sys/devices/bone_capemgr.?/slots

dtc -O dtb -o /lib/firmware/bspm_P8_21_d-00A0.dtbo -b 0 -@ /lib/firmware/bspm_P8_21_d-00A0.dts
echo bspm_P8_21_d > /sys/devices/bone_capemgr.?/slots

dtc -O dtb -o /lib/firmware/bspm_P8_20_d-00A0.dtbo -b 0 -@ /lib/firmware/bspm_P8_20_d-00A0.dts
echo bspm_P8_20_d > /sys/devices/bone_capemgr.?/slots

dtc -O dtb -I dts -o /lib/firmware/PRU-GPIO-EXAMPLE-00A0.dtbo -b 0 -@ /lib/firmware/PRU-GPIO-EXAMPLE-00A0.dts
echo PRU-GPIO-EXAMPLE > /sys/devices/bone_capemgr.?/slots





cat /sys/devices/bone_capemgr.?/slots
cd ~

lsmod
rmmod uio_pruss
modprobe uio_pruss extram_pool_sz=0x800000

pasm -V3b pruADC3.p
pasm -V3b pruMem.p
gcc dumpSamples.c dataBuffer.c -o dumpSamples
gcc getDataSlow.c -o getDataSlow -lpthread -lprussdrv
cp dumpSamples /usr/lib/cgi-bin/dumpSamples
chmod +s /usr/lib/cgi-bin/dumpSamples
