// This program uploads data sent from the other PRU into DDR3 memory
// This waits for r8 to be set and transfers the chunk of data over.
// r7 is set to STOP_CMD to indicate execution has finished
//
// The output ring buffer:
// First 4 bytes: (RingBuffer Tail + 1) If there was roll over, this is the RingBuffer Head
// Next 4 Bytes: Number of times rolled over
// Rest: Ring buffer Data
//
// Shared Registers (Sent through XOUT/XIN):
// r7: Set to STOP_CMD to indicate to pruMem that processing has finished.
// r8: Set to DATA_AVAILABLE to indicate to pruMem that new data is available
// r9 to rXX (maximum up to r29): Sample data to send over
//
// Internal Registers (Registers not shared):
// r0: Address to PRU_DATA_RAM where the DDR3 memory address is passed in
// r1: DDR3 memory address
// r2: DDR3 memory SIZE (NOTE: We assume this is 8MB here)
// r3: Current address to write data
// r4: Number of bytes until we have to reset the ringBuffer tail
// r5: Number of times we wrote around the ring buffer
// r6: RingBuffer Tail
//
// ASIDE: r4 and r5 is necessary because PRU only can do 8-bit ADD, COMPARE, and SUBTRACT

.origin 0                        // start of program in PRU memory
.entrypoint START                // program entry point (for a debugger)

#define NOP                OR r1, r1, r1        // PRU NOP Operation
.macro  MOV32                                   // Used to do a 32 bit move
.mparam dst, src
    MOV     dst.w0, src & 0xFFFF
    MOV     dst.w2, src >> 16
.endm

#define PRU0_R31_VEC_VALID 32       // allows notification of program completion
#define PRU_EVTOUT_0       3        // the event number that is sent back
#define DATA_AVAILABLE     1        // Value for r8 to indicate data is available (Set by the other PRU)
#define DATA_UNAVAILABLE   0        // Value r8 to indicate data is unavailable (Set by this PRU to indicate data is processed)
#define STOP_CMD           2        // Value for r7 to indicate that the program should halt
#define XFR_BANK           11

#define RING_BUFFER_SIZE   8388576                  // Number of bytes of ring buffer
                                                    // (Should be divisibly by 3 AND number of registers per chunk) (Don't modify)
#define NUM_COMM_BYTES     8                                        // Number of communication bytes per batch transfer
#define NUM_DATA_BYTES     12                                       // Number of data bytes per batch transfer
#define NUM_XFR_BYTES      (NUM_COMM_BYTES + NUM_DATA_BYTES)        // Number of bytes to transfer (includes all shared registers)

START:
        // Enable the OCP master port (Required for write to DDR3)
        LBCO    r0, C4, 4, 4     // load SYSCFG reg into r0 (use c4 const addr)
        CLR     r0, r0, 4        // clear bit 4 (STANDBY_INIT)
        SBCO    r0, C4, 4, 4     // store the modified r0 back at the load addr

        MOV     r0, 0x00000000   // the address from which to load the address
        LBBO    r1, r0, 0, 4     // load the Linux address that is passed in
        LBBO    r2, r0, 4, 4     // load the size that is passed in

        MOV     r7, 0            // r7 is the STOP_CMD register. We
                                 //initialize it to zero and exit with this is set to STOP_CMD

        ADD     r3, r1, 8                   // r3 contains the current address to write
        MOV32   r4, RING_BUFFER_SIZE        // r4 bytes left in ring buffer
        MOV32   r5, 0                       // r5 Counts number of times ring buffer rolls over
                                            // (non-zero value means ring buffer is full)
        MOV32   r6, 0                       // the location of the ring buffer tail

MAINLOOP:
        XIN     XFR_BANK, r7, NUM_XFR_BYTES             // Load registers from bank
        QBEQ    MAINLOOP, r8, DATA_UNAVAILABLE          // Keep looping until data is available
        QBEQ    FINISH_XFR, r7, STOP_CMD                // Jump to end if Top received
        MOV     r8, DATA_UNAVAILABLE                    // Set data unavailable
        XOUT    XFR_BANK, r8, 4                         // Clear the data available register in shared memory

        SBBO    r9, r3, 0, NUM_DATA_BYTES   // store samples to the address stored in r3
        ADD     r3, r3, NUM_DATA_BYTES      // increment r3 address
        SUB     r4, r4, NUM_DATA_BYTES      // decrement number of bytes left before reseting ring buffer
        ADD     r6, r6, NUM_DATA_BYTES      // Keep track of the tail of the ring buffer
        QBNE    FINISH_XFR, r4, 0           // Go to FINISH_XFR if ring buffer not full

        ADD     r3, r1, 8                   // Reset Ring Buffer
        MOV32   r6, 0
        MOV32   r4, RING_BUFFER_SIZE        // Reset bytes to write in ring buffer
        ADD     r5, r5, 1                   // Keep track of how many times r5 has rolled over
        QBEQ    FINISH_XFR, r5, 0           // If r5 is zero, it means it rolled over and we need to add one again
        ADD     r5, r5, 1                   // Add one to r5 so r5 is non-zero (to indicate that it is full)

FINISH_XFR:
        QBNE    MAINLOOP, r7, STOP_CMD  // keep looping until STOP_CMD

        SBBO    r6, r1, 0, 4   // Location of Ring Buffer Tail
        SBBO    r5, r1, 4, 4   // Number of times ring buffer rolled over (if non-zero, then ring buffer is full)
END:
        MOV     R31.b0, PRU0_R31_VEC_VALID | PRU_EVTOUT_0 // Alert linux that we are done
        HALT                     // halt the pru program
