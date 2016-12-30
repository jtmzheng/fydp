#ifndef COMM_UTILS_H
#define COMM_UTILS_H

#include "dataBuffer.h"

typedef struct comm_handle_s
{
    int mSockFd;
    
    int mNewSocketFd; // Socket for each client connection
    size_t mNumOutputSamples;

} comm_handle_t;

int start_server(comm_handle_t *pCommHandle, int aPortNo);

int get_request(comm_handle_t *pCommHandle);

int send_request(comm_handle_t *pCommHandle, data_buffer_t *pMappedDataBuffer);

#endif