#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <unistd.h>
#include <string.h>
#include <errno.h>
#include <signal.h>
#include <fcntl.h>
#include <ctype.h>
#include <termios.h>
#include <sys/types.h>
#include <sys/mman.h>
#include "dataBuffer.h"


size_t read_file_value(char filename[]){
   FILE* fp;
   size_t value = 0;
   fp = fopen(filename, "rt");
   fscanf(fp, "%x", &value);
   fclose(fp);
   return value;
}

int open_mem_fd(mapped_address_t *pMappedAddress, off_t aTarget)
{
    if((pMappedAddress->mFd = open("/dev/mem", O_RDWR | O_SYNC)) == -1){
        printf("Failed to open memory!");
        return -1;
    }

    if((pMappedAddress->mFd = open("/dev/mem", O_RDWR | O_SYNC)) == -1){
        printf("Failed to open memory!");
        return -1;
    }

    pMappedAddress->mMapBase = mmap(0, MAP_SIZE, PROT_READ | PROT_WRITE, MAP_SHARED, pMappedAddress->mFd, aTarget & ~MAP_MASK);
    if(pMappedAddress->mMapBase == (void *) -1) {
        printf("Failed to map base address");
        return -1;
    }

    fflush(stdout);
    return 0;
}

int close_mem_fd(mapped_address_t *pMappedAddress)
{
    if(munmap(pMappedAddress->mMapBase, MAP_SIZE) == -1) {
       printf("Failed to unmap memory");
    }
    close(pMappedAddress->mFd);
    
    fflush(stdout);
    return 0;
}

int parse_data(mapped_address_t *pMappedAddress, data_buffer_t *pMappedDataBuffer, off_t aTarget)
{
    uint8_t *cur_addr;
    size_t ring_buffer_start, ring_buffer_rollover;

    cur_addr = pMappedAddress->mMapBase + (aTarget & MAP_MASK);
    ring_buffer_start = *((uint32_t *) cur_addr);
    cur_addr = pMappedAddress->mMapBase + ((aTarget + 4) & MAP_MASK);
    ring_buffer_rollover = *((uint8_t *) cur_addr);

    if (ring_buffer_rollover == 0)
    {
        // ring_buffer has not rolled over
        // Therefore the first sample is at the start of the ring buffer and ring_buffer_start
        // is the next index to write
        pMappedDataBuffer->mData[0] = pMappedAddress->mMapBase + ((aTarget + HEADER_SIZE) & MAP_MASK);
        pMappedDataBuffer->mBufferSize[0] = ring_buffer_start;
        pMappedDataBuffer->mData[1] = NULL;
        pMappedDataBuffer->mBufferSize[1] = 0;

    }
    else
    {
        pMappedDataBuffer->mData[0] = pMappedAddress->mMapBase + ((aTarget + ring_buffer_start + HEADER_SIZE) & MAP_MASK);
        pMappedDataBuffer->mBufferSize[0] = RING_BUFFER_SIZE - ring_buffer_start;
        pMappedDataBuffer->mData[1] = pMappedAddress->mMapBase + ((aTarget + HEADER_SIZE) & MAP_MASK);
        pMappedDataBuffer->mBufferSize[1] = ring_buffer_start;
    }

    return 0;
}