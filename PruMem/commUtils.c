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
            error("ERROR reading from socket");
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
            error("ERROR writing to socket");
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
        error("ERROR opening socket");
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
            error("ERROR on binding");
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
    size_t numberOutputSamples;

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
        error("ERROR on accept");
        ret = -1;
    }

    if (ret == 0)
    {
        // Get number of bytes to send
        int bytesDone = 0;   
        ret = read_data(newsockfd, (char*)&numberOutputSamples, 4);
        printf("Received Request!\n");
    }

    if (ret == 0)
    {
        pCommHandle->mNewSocketFd = newsockfd;
        numberOutputSamples = ntohl(numberOutputSamples);

        if (numberOutputSamples < 0)
        {
            numberOutputSamples = RING_BUFFER_SIZE;
        }
        pCommHandle->mNumOutputSamples = MIN(numberOutputSamples, RING_BUFFER_SIZE);
        printf("Number Output Samples: %d!\n", numberOutputSamples);
    }

    return ret;
}

int send_request(comm_handle_t *pCommHandle, data_buffer_t *pMappedDataBuffer)
{
    int ret = 0;
    size_t num_samples_to_send = pMappedDataBuffer->mBufferSize[0] + pMappedDataBuffer->mBufferSize[1];
    size_t num_samples_to_send_nt;
    num_samples_to_send = MIN(pCommHandle->mNumOutputSamples, num_samples_to_send);
    num_samples_to_send_nt = htonl(num_samples_to_send);

    printf("a\n");
    ret = write_data(pCommHandle->mNewSocketFd, (char*)&num_samples_to_send_nt, 4);
    printf("b\n");
    if (ret == 0 && num_samples_to_send > 0)
    {
        printf("c\n");
        size_t num_sent_data = MIN(pMappedDataBuffer->mBufferSize[0], num_samples_to_send);
        ret = write_data(pCommHandle->mNewSocketFd, (char*)pMappedDataBuffer->mData[0], num_sent_data);
        num_samples_to_send -= num_sent_data;
        printf("d\n");
    }

    if (ret == 0 && num_samples_to_send > 0)
    {
        printf("e\n");
        size_t num_sent_data = MIN(pMappedDataBuffer->mBufferSize[1], num_samples_to_send);
        ret = write_data(pCommHandle->mNewSocketFd, (char*)pMappedDataBuffer->mData[1], num_sent_data);
        printf("f\n");
    }
    printf("g\n");
    close(pCommHandle->mNewSocketFd);
    pCommHandle->mNewSocketFd = 0;
    pCommHandle->mNumOutputSamples = 0;

    return ret;
}
