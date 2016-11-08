/* This mem2file.c program is a modified version of devmem2 by Jan-Derk Bakker
 * as referenced below. This program was modified by Derek Molloy for the book
 * Exploring BeagleBone. It is used in Chapter 13 to dump the DDR External Memory
 * pool to a file. See: www.exploringbeaglebone.com/chapter13/
 *
 * devmem2.c: Simple program to read/write from/to any location in memory.
 *
 *  Copyright (C) 2000, Jan-Derk Bakker (J.D.Bakker@its.tudelft.nl)
 *
 *
 * This software has been developed for the LART computing board
 * (http://www.lart.tudelft.nl/). The development has been sponsored by
 * the Mobile MultiMedia Communications (http://www.mmc.tudelft.nl/)
 * and Ubiquitous Communications (http://www.ubicom.tudelft.nl/)
 * projects.
 *
 * The author can be reached at:
 *
 *  Jan-Derk Bakker
 *  Information and Communication Theory Group
 *  Faculty of Information Technology and Systems
 *  Delft University of Technology
 *  P.O. Box 5031
 *  2600 GA Delft
 *  The Netherlands
 *
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */

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

#define MAP_SIZE            0x0FFFFFFF
#define MAP_MASK            (MAP_SIZE)
#define MMAP_LOC            "/sys/class/uio/uio0/maps/map1/"
#define HEADER_SIZE         (8)
#define RING_BUFFER_SIZE    (8388576)
#define MAX(X, Y)           (((X) > (Y)) ? (X) : (Y))
#define MIN(X, Y)           (((X) < (Y)) ? (X) : (Y))

unsigned int readFileValue(char filename[]){
   FILE* fp;
   unsigned int value = 0;
   fp = fopen(filename, "rt");
   fscanf(fp, "%x", &value);
   fclose(fp);
   return value;
}

int main(int argc, char **argv) {
    int fd;
    void *map_base, *virt_addr;
    unsigned long read_result, writeval;
    unsigned int addr = readFileValue(MMAP_LOC "addr");
    unsigned int dataSize = readFileValue(MMAP_LOC "size");
    unsigned int numberOutputSamples = RING_BUFFER_SIZE;
    unsigned int ring_buffer_start, ring_buffer_rollover;
    off_t target = addr;
    
    puts("Content-type: text/html\n");

    puts("<!DOCTYPE html>");
    puts("<head>");
    puts("  <meta charset=\"utf-8\">");
    puts("</head>");
    puts("<body>");
    puts("   <h3>PRU ADC DATA</h3>");
    
    if(argc>1){     // There is an argument -- lists number of samples to dump
                    // this defaults to the total DDR Memory Pool x 2 (16-bit samples) 
        numberOutputSamples = atoi(argv[1]);
    }

    if((fd = open("/dev/mem", O_RDWR | O_SYNC)) == -1){
        printf("Failed to open memory!");
        return -1;
    }
    fflush(stdout);

    map_base = mmap(0, MAP_SIZE, PROT_READ | PROT_WRITE, MAP_SHARED, fd, target & ~MAP_MASK);
    if(map_base == (void *) -1) {
        printf("Failed to map base address");
        return -1;
    }
    fflush(stdout);

    virt_addr = map_base + (target & MAP_MASK);
    ring_buffer_start = *((uint32_t *) virt_addr);
    virt_addr = map_base + ((target + 4) & MAP_MASK);
    ring_buffer_rollover = read_result = *((uint8_t *) virt_addr);
    
    if (ring_buffer_rollover == 0)
    {
        // ring_buffer has not rolled over
        // Therefore the first address is zero, and num samples
        // is right before the 'read'
        
        numberOutputSamples = MIN(ring_buffer_start, numberOutputSamples);
        ring_buffer_start = 0;   
    }
    else
    {
        numberOutputSamples = MIN(RING_BUFFER_SIZE, numberOutputSamples);
    }
    
    printf("NumSamples: %d\n", numberOutputSamples);
    
    printf("0x");
    int i=0;
    for(i=0; i<numberOutputSamples; i++){
        int cur_offset = (i + ring_buffer_start) % RING_BUFFER_SIZE;
        virt_addr = map_base + ( (target + cur_offset + HEADER_SIZE) & MAP_MASK);
        read_result = *((uint8_t *) virt_addr);
        
        printf("%02X", read_result);
    }
    printf("\n");
    fflush(stdout);

    if(munmap(map_base, MAP_SIZE) == -1) {
       printf("Failed to unmap memory");
       return -1;
    }
    close(fd);
    
    puts("</body>");
    puts("</html>");
    fflush(stdout);
    return 0;
}