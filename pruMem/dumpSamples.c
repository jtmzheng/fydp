#include "dataBuffer.h"

int main(int argc, char **argv) {
    mapped_address_t mapped_address;
    data_buffer_t mapped_data_buffer;
    size_t addr = read_file_value(MMAP_LOC "addr");
    size_t data_size = read_file_value(MMAP_LOC "size");
    size_t numberOutputSamples = RING_BUFFER_SIZE;
    int ret;

    if(argc>1){     // There is an argument -- lists number of samples to dump
                    // this defaults to the total DDR Memory Pool x 2 (16-bit samples) 
        numberOutputSamples = atoi(argv[1]);
    }

    ret = open_mem_fd(&mapped_address, addr);

    if (ret == 0)
    {
        ret = parse_data(&mapped_address, &mapped_data_buffer, addr);
    }

    if (ret == 0)
    {
        printf("{\"NumSamples\": %d,\n", numberOutputSamples);
        
        printf("\"Data\":\"0x");
        int i=0;
        for(i=0; i<numberOutputSamples; i++){

            if (i < mapped_data_buffer.mBufferSize[0])
            {
                printf("%02X", (mapped_data_buffer.mData[0])[i]);
            }
            else if (mapped_data_buffer.mData[1] != NULL)
            {
                printf("%02X", (mapped_data_buffer.mData[1])[i - mapped_data_buffer.mBufferSize[0]]);
            }
            
            
        }
        printf("\"}\n");
        fflush(stdout);
    }

    ret = close_mem_fd(&mapped_address);    
    
    
    return ret;
}