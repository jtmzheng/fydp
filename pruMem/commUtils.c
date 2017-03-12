#include "commUtils.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>

int read_data(int aNewSockFd, char *aBuffer, int aBytesExpected)
{
    int bytesDone = 0;
    int ret = 0;

    while (bytesDone < aBytesExpected && ret == 0)
    {
        int n;
        n = read(aNewSockFd, aBuffer + bytesDone, aBytesExpected - bytesDone);

        if (n < 0)
        {
            printf("ERROR reading from socket\n");
            ret = -1;
        }
        else
        {
            bytesDone += n;
        }
    }

    return ret;
}

int write_data(int aNewSockFd, char *aBuffer, int aBytesExpected)
{
    int bytesDone = 0;
    int ret = 0;

    while (bytesDone < aBytesExpected && ret == 0)
    {
        int n;
        n = write(aNewSockFd, aBuffer + bytesDone, aBytesExpected - bytesDone);

        if (n < 0)
        {
            printf("ERROR writing to socket\n");
            ret = -1;
        }
        else
        {
            bytesDone += n;
        }
    }

    return ret;
}

int start_server(comm_handle_t *pCommHandle, int aPortNo)
{
    int ret = 0;
    struct sockaddr_in serv_addr;
    printf("start_server\n");
    // Init struct to zero
    memset(pCommHandle, 0, sizeof(comm_handle_t));

    pCommHandle->mSockFd = socket(AF_INET, SOCK_STREAM, 0);
    if (pCommHandle->mSockFd < 0)
    {
        printf("ERROR opening socket\n");
        ret = -1;
    }

    if (ret == 0)
    {
        memset(&serv_addr, 0, sizeof(serv_addr));
        serv_addr.sin_family = AF_INET;
        serv_addr.sin_addr.s_addr = INADDR_ANY;
        serv_addr.sin_port = htons(aPortNo);
        if (bind(pCommHandle->mSockFd,
                 (struct sockaddr *) &serv_addr,
                 sizeof(serv_addr)) < 0)
        {
            printf("ERROR on binding\n");
            ret = -1;
        }
    }

    return ret;
}

int get_request(comm_handle_t *pCommHandle)
{
    int ret = 0;
    int newsockfd;
    socklen_t clilen;
    char buffer[256];
    struct sockaddr_in cli_addr;
    int numberOutputSamples;

    // Get new client connection
    listen(pCommHandle->mSockFd, 5);
    printf("Listening!\n");
    clilen = sizeof(cli_addr);
    memset(buffer, 0, sizeof(buffer));

    newsockfd = accept(pCommHandle->mSockFd,
                       (struct sockaddr *) &cli_addr,
                       &clilen);
    printf("Got new Conection!\n");

    if (newsockfd < 0)
    {
        printf("ERROR on accept\n");
        ret = -1;
    }

    if (ret == 0)
    {
        // Get number of bytes to send
        int bytesDone = 0;
        ret = read_data(newsockfd, (char*)&numberOutputSamples, 4);
        printf("Received Request %d!\n", numberOutputSamples);
    }

    if (ret == 0)
    {
        pCommHandle->mNewSocketFd = newsockfd;
        numberOutputSamples = ntohl(numberOutputSamples);

        if (numberOutputSamples <= 0)
        {
            numberOutputSamples = RING_BUFFER_SIZE;
        }
        pCommHandle->mNumOutputSamples = MIN(numberOutputSamples, RING_BUFFER_SIZE);
        printf("Number Output Samples: %d!\n", numberOutputSamples);
        printf("pCommHandle->mNumOutputSamples: %d!\n", pCommHandle->mNumOutputSamples);
    }

    return ret;
}

int send_request(comm_handle_t *pCommHandle, data_buffer_t *pMappedDataBuffer)
{
    int ret = 0;
    int num_samples_to_send = pMappedDataBuffer->mBufferSize[0] + pMappedDataBuffer->mBufferSize[1];
    int num_samples_to_send_nt;
    num_samples_to_send = MIN(pCommHandle->mNumOutputSamples, num_samples_to_send);
    num_samples_to_send_nt = htonl(num_samples_to_send);

    printf("Sending Data Size: %d\n", num_samples_to_send);
    ret = write_data(pCommHandle->mNewSocketFd, (char*)&num_samples_to_send_nt, 4);

    if (ret == 0 && num_samples_to_send > pMappedDataBuffer->mBufferSize[1])
    {
        int num_to_send_buf0 = num_samples_to_send - pMappedDataBuffer->mBufferSize[1];
        char *buff_start = ((char*)pMappedDataBuffer->mData[0]) + pMappedDataBuffer->mBufferSize[0] - num_to_send_buf0;

        ret = write_data(pCommHandle->mNewSocketFd, buff_start, num_to_send_buf0);
        num_samples_to_send -= num_to_send_buf0;
    }

    if (ret == 0 && num_samples_to_send > 0)
    {
        int num_to_send_buf1 = MIN(pMappedDataBuffer->mBufferSize[1], num_samples_to_send);
        char *buff_start = ((char*)pMappedDataBuffer->mData[1]) + pMappedDataBuffer->mBufferSize[1] - num_to_send_buf1;

        ret = write_data(pCommHandle->mNewSocketFd, buff_start, num_to_send_buf1);
    }
    close(pCommHandle->mNewSocketFd);
    pCommHandle->mNewSocketFd = 0;
    pCommHandle->mNumOutputSamples = 0;

    return ret;
}
