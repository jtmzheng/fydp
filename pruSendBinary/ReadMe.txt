Step 1:
Copy .out file from Debug in CC6 workspace. (Named test.out here)

Step 2: (bin.cmd and hexpru are found in <ccsv6_install_dir>/tools/compiler/ti-cgt-pru_2.1.3)
hexpru bin.cmd test.out

Step 3
pscp *.bin root@192.168.7.2:/root/pruMem