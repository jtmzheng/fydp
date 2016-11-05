#include <stdio.h>
#include <stdlib.h>
#include <prussdrv.h>
#include <pruss_intc_mapping.h>

#define MEM_PRU_NUM	   0   // using PRU1 memory data transfer
#define ADC_PRU_NUM	   1   // using PRU0 for the ADC capture
#define MMAP0_LOC   "/sys/class/uio/uio0/maps/map0/"
#define MMAP1_LOC   "/sys/class/uio/uio0/maps/map1/"

// Short function to load a single unsigned int from a sysfs entry
unsigned int readFileValue(char filename[]){
    FILE* fp;
    unsigned int value = 0;
    fp = fopen(filename, "rt");
    fscanf(fp, "%x", &value);
    fclose(fp);
    return value;
}


int main(int argc, char **argv) {
	
    if(getuid()!=0){
        printf("You must run this program as root. Exiting.\n");
        exit(EXIT_FAILURE);
    }
        
    if (argc != 2 && argc != 3) {
        printf("Usage: %s loader text.bin [data.bin]\n", argv[0]);
        return 1;
    }
    
    // Initialize structure used by prussdrv_pruintc_intc
    // PRUSS_INTC_INITDATA is found in pruss_intc_mapping.h
    tpruss_intc_initdata pruss_intc_initdata = PRUSS_INTC_INITDATA;
    
    // Read in the location and address of the shared memory. This value changes
    // each time a new block of memory is allocated.
    unsigned int pruData[2];
    pruData[0] = readFileValue(MMAP1_LOC "addr");
    pruData[1] = readFileValue(MMAP1_LOC "size");
    printf("The DDR External Memory pool has location: 0x%x and size: 0x%x bytes\n", pruData[0], pruData[1]);
    
    // Allocate and initialize memory
    prussdrv_init();
    if (prussdrv_open(PRU_EVTOUT_0) == -1) {
        printf("prussdrv_open() failed\n");
        return 1;
    }
    
    // Write the address and size into PRU0 Data RAM0. You can edit the value to
    // PRUSS0_PRU1_DATARAM if you wish to write to PRU1
    prussdrv_pru_write_memory(PRUSS0_PRU0_DATARAM, 0, pruData, 8); // sample clock
    
    // Map the PRU's interrupts
    prussdrv_pruintc_init(&pruss_intc_initdata);
    
    printf("Executing program and waiting for termination\n");
    if (argc == 3) {
        if (prussdrv_load_datafile(MEM_PRU_NUM /* PRU0 */, argv[2]) < 0) {
            fprintf(stderr, "Error loading %s\n", argv[2]);
            exit(-1);
        }
    }
    if (prussdrv_exec_program(MEM_PRU_NUM /* PRU0 */, argv[1]) < 0) {
        fprintf(stderr, "Error loading %s\n", argv[1]);
        exit(-1);
    }

    // Wait for the PRU to let us know it's done
    int n = prussdrv_pru_wait_event(PRU_EVTOUT_0);
    printf("EBBADC PRU0 program completed, event number %d.\n", n);
    printf("All done\n");

    prussdrv_pru_disable(MEM_PRU_NUM /* PRU0 */);
    prussdrv_exit();

    return 0;
}