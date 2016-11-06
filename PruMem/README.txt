http://exploringbeaglebone.com/chapter13/

# Copy Build Directory
pscp build root@192.168.7.2:/root/pruData
# On Linux, you need to remove \r by typing this command after you copied it over
sed -i 's/\r$//' build
chmod +x build


# Copy c and assembly files
pscp *.c root@192.168.7.2:/root/pruData
pscp *.p root@192.168.7.2:/root/pruData