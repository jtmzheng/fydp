#include <stdint.h>

#define PRU0_R31_VEC_VALID (1<<5)
#define SIGNUM 3 // corresponds to PRU_EVTOUT_0

volatile register unsigned int __R31, __R30;

int main(void) {

	__asm__ __volatile__
		(
		// wait for specified period of time
		"DELAY_SECONDS .set 5 \n"
		"CLOCK .set 200000000 \n"
		"CLOCKS_PER_LOOP .set 2 \n"
		"DELAYCOUNT .set DELAY_SECONDS * CLOCK / CLOCKS_PER_LOOP \n"
	    " 	LDI32 r1, DELAYCOUNT \n" // 2*200e6/2
		"DELAY:"
		" 	SUB	r1, r1, 1 \n" // decrement loop counter
		" 	QBNE DELAY, r1, 0 \n"  // repeat loop unless zero
		);

    __R31 = PRU0_R31_VEC_VALID | SIGNUM;
    __halt();
    return 0;
}
