Client/Server communcation.
client.c is used to get microphone data.
server.c is a testing server that runs in Linux. This is to simulate DataServer.c which runs on the beaglebone.

For testing on linux:
1) Execute ./build in fydp/comm/ directory to create server and client executable
2) Run server: ./server <portno> (For example: ./server 5555)
3) In another tab, run the client with the same port number and 127.0.0.1 (localhost): ./client <host> <portno> 
   (For example: ./client 127.0.0.1 55555)
4) In the client code, enter the number of bytes you want to receive. To receive all the data, enter -1

For testing on Beaglebone
1) Execute DataServer on beaglebone (For example: ./server 5555)
2) Run client, similar to on linux, except us Beaglebone IP address (For example: ./client 192.168.7.2 5555)
3) On client, enter the number of bytes you want to receive, to receive all data, enter -1