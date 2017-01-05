#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h> 


#define RING_BUFFER_SIZE    (8388576)

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

int get_socket(int *pSockFd, int aPortNo, struct hostent *aServer)
{
    int sockfd;
    struct sockaddr_in serv_addr;
    int ret = 0;

    if (aServer == NULL) 
    {
        fprintf(stderr,"ERROR, no such host\n");
        return -1;
    }

    // Set up Socket Connection
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0)
    {
        printf("ERROR opening socket\n");
        ret = -1;
    }
    
    if (ret == 0)
    {
        bzero((char *) &serv_addr, sizeof(serv_addr));
        serv_addr.sin_family = AF_INET;
        bcopy((char *)aServer->h_addr, 
              (char *)&serv_addr.sin_addr.s_addr,
              aServer->h_length);
        serv_addr.sin_port = htons(aPortNo);
        
        if (connect(sockfd,(struct sockaddr *) &serv_addr,sizeof(serv_addr)) < 0)
        {
            printf("ERROR connecting\n");
            ret = -1;
        }
        else
        {
            (*pSockFd) = sockfd;    
        }
    }

    return ret;
}

int get_buffer(int aSockfd, int aNumRequestSamples, int *pNumActualSamples, char *aBuffer)
{
    int actualSamples;
    int ret = 0;
    int num_req_samples_nt = htonl(aNumRequestSamples);

    // Request for num_req_samples_nt bytes
    ret = write_data(aSockfd, (char*)&num_req_samples_nt, 4);

    if (ret == 0)
    {
        // Read number of bytes sent
        ret = read_data(aSockfd, (char*)&actualSamples, 4);

        actualSamples = ntohl(actualSamples);
        (*pNumActualSamples) = actualSamples;

        if (actualSamples > RING_BUFFER_SIZE || actualSamples < 0 || ret != 0)
        {
            printf("Incomming buffer size invalid. Got: %d, max: %d\n", actualSamples, RING_BUFFER_SIZE);
            ret = -1;
        }
    }

    if (ret == 0)
    {
        // Read Data Received
        ret = read_data(aSockfd, aBuffer, actualSamples);

        if (ret != 0)
        {
            printf("Error reading data!\n");
        }
    }
    return ret;
}

int main(int argc, char *argv[])
{
    
    int portno = 5555;
    int sockfd = -1;
    struct hostent *server;
    int numRequestSamples, numActualSamples;
    uint8_t *buffer;
    int ret = 0;

    if (argc < 3) 
    {
       fprintf(stderr,"usage %s hostname port\n", argv[0]);
       exit(0);
    }

    buffer = malloc(RING_BUFFER_SIZE);
    if (!buffer)
    {
        printf("Error could not allocate data!");
        ret = -1;
    }
    
    if (ret == 0)
    {
        portno = atoi(argv[2]);
        server = gethostbyname(argv[1]);
        memset(buffer, 0, RING_BUFFER_SIZE);
    }

    // Get Socket
    if (ret == 0)
    {   
        printf("Connecting to Socket\n");
        ret = get_socket(&sockfd, portno, server);
    }

    if (ret == 0)
    {
        // Scanf returns # of bytes read only when
        // it successfully reads an integer
        // Keep looping until this happens
        // Then reset ret to indicate no error.
        do {
            printf("Please enter number of bytes: ");
            ret = scanf("%d", &numRequestSamples);
        } while (ret < 0);
        ret = 0;        
    }

    if (ret == 0)
    {
        // numActualSamples is
        ret = get_buffer(sockfd, numRequestSamples, &numActualSamples, buffer);
    }

    if (ret == 0)
    {
        int i=0;

        printf("{\"NumSamples\": %d,\n", numActualSamples);
        printf("\"Data\":\"0x");
            
        for (i=0; i < numActualSamples; i++)
        {
            printf("%02X", buffer[i]);
        }
        printf("\"}\n");
        fflush(stdout);
    }
    
    close(sockfd);
    
    return 0;
}
