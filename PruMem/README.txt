http://exploringbeaglebone.com/chapter13/

# Copy Build Directory
pscp build root@192.168.7.2:/root/pruMem
# On Linux, you need to remove \r by typing this command after you copied it over
sed -i 's/\r$//' build


# Copy c and assembly files
pscp *.c root@192.168.7.2:/root/pruMem
pscp *.p root@192.168.7.2:/root/pruMem