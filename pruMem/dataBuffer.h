#ifndef DATA_BUFFER_H
#define DATA_BUFFER_H

#include "commUtils.h"

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#define MAP_SIZE            0x0FFFFFFF
#define MAP_MASK            (MAP_SIZE)
#define HEADER_SIZE         (8)
#define MMAP_LOC            "/sys/class/uio/uio0/maps/map1/"

typedef struct mapped_address_s
{
    int mFd;
    void *mMapBase;
} mapped_address_t;

int open_mem_fd(mapped_address_t *pMappedAddress, off_t aTarget);
int close_mem_fd(mapped_address_t *pMappedAddress);
int parse_data(mapped_address_t *pMappedAddress, data_buffer_t *pMappedDataBuffer, off_t aTarget);

#endif