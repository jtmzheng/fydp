#include "dataBuffer.h"
#include "commUtils.h"
#include "pruCtrl.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h> 
#include <sys/socket.h>
#include <netinet/in.h>

int main(int argc, char **argv) {
    mapped_address_t mapped_address;
    data_buffer_t mapped_data_buffer;
    comm_handle_t command_handle;

    size_t addr = read_file_value(MMAP_LOC "addr");
    size_t data_size = read_file_value(MMAP_LOC "size");
    int ret = 0;
    int portno = 5555;

    if(argc>1){     // There is an argument -- lists number of samples to dump
                    // this defaults to the total DDR Memory Pool x 2 (16-bit samples) 
        portno = atoi(argv[1]);
    }

    if (ret == 0)
    {
        printf("Starting Server...\n");
        ret = start_server(&command_handle, portno);
        printf("Server Started!\n");
    }
    
    while (1)
    {

        if (ret == 0)
        {
            printf("Starting PRU!\n");
            pru_start();
        }

        if (ret == 0)
        {
            printf("Waiting for Client Request...\n");
            ret = get_request(&command_handle);
        }

        if (ret == 0)
        {
            printf("Stopping PRU\n");
            pru_end();
        }

        if (ret == 0)
        {
            printf("Opening Shared Memory\n");
            ret = open_mem_fd(&mapped_address, addr);
        }

        if (ret == 0)
        {
            printf("Parsing Shared Memory\n");
            ret = parse_data(&mapped_address, &mapped_data_buffer, addr);
        }

        if (ret == 0)
        {
            printf("Replying to Client with data\n");
            ret = send_request(&command_handle, &mapped_data_buffer);
        }

        if (ret == 0)
        {
            printf("Closing Shared Memory...\n");
            ret = close_mem_fd(&mapped_address);
        }
    }
    
    return ret;
}