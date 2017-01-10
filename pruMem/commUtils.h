#ifndef COMM_UTILS_H
#define COMM_UTILS_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <stdint.h>

#define RING_BUFFER_SIZE    (8388576)
#define MAX(X, Y)           (((X) > (Y)) ? (X) : (Y))
#define MIN(X, Y)           (((X) < (Y)) ? (X) : (Y))

typedef struct comm_handle_s
{
    int mSockFd;
    
    int mNewSocketFd; // Socket for each client connection
    int mNumOutputSamples;

} comm_handle_t;

// Data Buffer contains 2 pointers and sizes
// This is to deal with the wrap around in ring buffer
typedef struct data_buffer_s
{
    uint8_t *mData[2];
    int mBufferSize[2];
} data_buffer_t;


// All communications is done in TCP,
// this means that data is sent over in a connectioned protocal with in a 
// guarentee that the order is what was origially sent
// Steps that happen:
// 1) Client requests X number of bytes
// 2) Server sends integer Y, indicating the number of samples it actually will send
// 3) Server sends Y bytes of data
// 4) Server goes back to listening
int start_server(comm_handle_t *pCommHandle, int aPortNo);

int get_request(comm_handle_t *pCommHandle);

int send_request(comm_handle_t *pCommHandle, data_buffer_t *pMappedDataBuffer);

#endif