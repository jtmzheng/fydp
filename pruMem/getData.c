#include <stdio.h>
#include <stdlib.h>
#include <prussdrv.h>
#include <pruss_intc_mapping.h>

#define PRU_MEM_NUM	0   // using PRU0 for Memory
#define PRU_ADC_NUM 1   // Use PRU1 for ADC
#define MMAP_LOC "/sys/class/uio/uio0/maps/map1/"

unsigned int readFileValue(char filename[]){
   FILE* fp;
   unsigned int value = 0;
   fp = fopen(filename, "rt");
   fscanf(fp, "%x", &value);
   fclose(fp);
   return value;
}

int main (void)
{
   if(getuid()!=0){
      printf("You must run this program as root. Exiting.\n");
      exit(EXIT_FAILURE);
   }
   // Initialize structure used by prussdrv_pruintc_intc
   // PRUSS_INTC_INITDATA is found in pruss_intc_mapping.h
   tpruss_intc_initdata pruss_intc_initdata = PRUSS_INTC_INITDATA;

   // Read in the location and address of the shared memory. This value changes
   // each time a new block of memory is allocated.
   unsigned int values[2];
   values[0] = readFileValue(MMAP_LOC "addr");
   values[1] = readFileValue(MMAP_LOC "size");
   printf("The shared memory has location: %x and size %x\n", values[0], values[1]);

   // Allocate and initialize memory
   prussdrv_init ();
   prussdrv_open (PRU_EVTOUT_0);

   // Write the address and size into PRU0 Data RAM0. You can edit the value to
   // PRUSS0_PRU1_DATARAM if you wish to write to PRU1
   prussdrv_pru_write_memory(PRUSS0_PRU0_DATARAM, 0, values, 8);

   // Map PRU's interrupts
   prussdrv_pruintc_init(&pruss_intc_initdata);

   // Load and execute the PRU program on the PRU
   prussdrv_exec_program (PRU_ADC_NUM, "./pruADC.bin");
   // We let pruADC get into a consistent state first 
   usleep(100);
   prussdrv_exec_program (PRU_MEM_NUM, "./pruMem.bin");
   
   printf("Running Program. Press any key to stop...");
   getchar();  
     
   printf("Stopping\n");
   prussdrv_pru_send_event(ARM_PRU1_INTERRUPT);
   
   // Wait for event completion from PRU, returns the PRU_EVTOUT_0 number
   int n = prussdrv_pru_wait_event (PRU_EVTOUT_0);
   printf("EBB PRU program completed, event number %d.\n", n);

   // Disable PRU and close memory mappings
   prussdrv_pru_disable(PRU_MEM_NUM);
   prussdrv_pru_disable(PRU_ADC_NUM);
   prussdrv_exit ();
   return EXIT_SUCCESS;
}