http://exploringbeaglebone.com/chapter13/

# Follow steps to get the pasm (PRU assembler in path)
http://mythopoeic.org/bbb-pru-minimal/
https://github.com/beagleboard/am335x_pru_package

After copying commands over, I suggest you run every
command in build manually for the first time (The script is bad at reporting errors)

====================
USEFUL COMMANDS
====================
# Copy Build Directory
pscp build root@192.168.7.2:/root/pruData
pscp *.dts root@192.168.7.2:/root/pruData

# On Linux, you need to remove \r by typing this command after you copied it over
sed -i 's/\r$//' build
chmod +x build


# Copy c and assembly files
pscp *.c root@192.168.7.2:/root/pruData
pscp *.p root@192.168.7.2:/root/pruData

To get first 40 samples from memory:
./dumpSamples 40

# Getting stuff from matlab:
tmp = urlread('http://192.168.7.2:8080/cgi-bin/dumpSamples');