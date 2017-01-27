#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h>
#include "commUtils.h"

#define SAMPLES_FILE "samples.json"

int is_valid_hex(char aHexChar)
{
    return (aHexChar >='0' && aHexChar <= '9') ||
           (aHexChar >='a' && aHexChar <= 'f') ||
           (aHexChar >='A' && aHexChar <= 'F');
}

int hex_char_to_int(char aHexChar)
{
    int retVal = -1;
    if (aHexChar >='0' && aHexChar <= '9')
    {
        retVal = aHexChar - '0';
    }
    else if(aHexChar >= 'A' && aHexChar <= 'F')
    {
        retVal = aHexChar - 'A' + 10;
    }
    else if(aHexChar >= 'a' && aHexChar <= 'f')
    {
        retVal = aHexChar - 'a' + 10;
    }

    return retVal;
}

uint8_t get_hex_byte(const char *aHexStr)
{
    return (hex_char_to_int(aHexStr[0])*16 + hex_char_to_int(aHexStr[1]));
}

int get_buffer_from_file(const char *filename, uint8_t *aBuffer, int *pNumBytes)
{
    FILE *f;
    long fsize;
    int hex_start;
    char *string = NULL;
    int num_bytes;
    int ret = 0;

    if (ret == 0)
    {
        f = fopen(filename, "rb");
        if (f == NULL)
        {
            printf("Could not open file!\n");
            ret = -1;
        }
    }

    if (ret == 0)
    {
        fseek(f, 0, SEEK_END);
        fsize = ftell(f);
        fseek(f, 0, SEEK_SET);  //same as rewind(f);
        string = malloc(fsize + 1);

        if (string == NULL)
        {
            printf("Error could not allocate string!\n");
            ret = -1;
        }
    }

    if (ret == 0)
    {
        fread(string, fsize, 1, f);
        fclose(f);
        string[fsize] = 0;
        //printf("string: %s\n", string);
        for (hex_start = 0; hex_start < fsize; hex_start++)
        {
            if (strncmp(string+hex_start, ":\"0x", 4) == 0)
            {
                hex_start+=4;
                break;
            }
        }
    }

    if (ret == 0)
    {
        int cur_idx;
        num_bytes = 0;
        for (cur_idx = hex_start; cur_idx < fsize; cur_idx += 2)
        {
            if (is_valid_hex(*(string+cur_idx)) && is_valid_hex(*(string+cur_idx+1)))
            {
                aBuffer[num_bytes] = get_hex_byte(string+cur_idx);
                //printf("%c%c %d %d\n", *(string+cur_idx), *(string+cur_idx+1), cur_idx, aBuffer[num_bytes]);
                num_bytes++;
            }
            else
            {

                break;
            }
        }

        (*pNumBytes) = num_bytes;
    }
    printf("NumBytes: %d\n", num_bytes);

    if (string != NULL)
    {
        free(string);
    }

    return ret;
}

int main(int argc, char *argv[])
{
    data_buffer_t mapped_data_buffer;
    comm_handle_t command_handle;
    uint8_t *buffer;
    int num_bytes;
    int ret = 0;
    int portno = 5555;

    if(argc>1){     // There is an argument -- lists number of samples to dump
                    // this defaults to the total DDR Memory Pool x 2 (16-bit samples)
        portno = atoi(argv[1]);
    }

    buffer = malloc(RING_BUFFER_SIZE);
    if (buffer == NULL)
    {
        printf("Could not allocate buffer!\n");
        ret = -1;
    }

    if (ret == 0)
    {
        ret = get_buffer_from_file(SAMPLES_FILE, buffer, &num_bytes);
        printf("Number of Samples: %d\n", num_bytes);

        mapped_data_buffer.mData[0] = buffer;
        mapped_data_buffer.mData[1] = NULL;
        mapped_data_buffer.mBufferSize[0] = num_bytes;
        mapped_data_buffer.mBufferSize[1] = 0;
    }

    if (ret == 0)
    {
        printf("Starting Server...\n");
        ret = start_server(&command_handle, portno);
        printf("Server Started!\n");
    }

    while (ret == 0)
    {

        if (ret == 0)
        {
            printf("Waiting for Client Request...\n");
            ret = get_request(&command_handle);
        }

        if (ret == 0)
        {
            printf("Replying to Client with data\n");
            ret = send_request(&command_handle, &mapped_data_buffer);
        }
    }

    if (!buffer)
    {
        free(buffer);
    }

    return 0;
}