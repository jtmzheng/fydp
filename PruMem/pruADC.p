// This program sends data the other PRU the shared memory bank (XOUT/XIN assembly command)
// The shared memory bank is used to cache register values. In this case, we fill up the current register
// values up until a certain point and then we send over the relevant register values over to the other PRU.
// This program keeps sending data until it receives an interrupt signal from Linux, at which point it halts execution
// The data is transfered by sending registers r9 to rXX (maximum up to r29) to the shared memory bank
// and alerting the other pru (PRU_MEM) by sending r8 to the shared memory bank
// If r7, with a value of STOP_CMD is sent to the other register bank, the other PRU terminates
// Each register is 4 bytes
//
// Shared Registers (Sent through XOUT/XIN): 
// r7: Set to STOP_CMD to indicate to pruMem that processing has finished.
// r8: Set to DATA_AVAILABLE to indicate to pruMem that new data is available
// r9 to rXX (maximum up to r29): Sample data to send over
//
// Internal Registers (Registers not shared):
// r1: Dummy register containing value to send over (TODO: Replace this with actual sampled data)
// 

.origin 0                       // start of program in PRU memory
.entrypoint START               // program entry point (for a debugger)

#define NOP                OR r1, r1, r1        // PRU NOP Operation
.macro  MOV32                                   // Used to do a 32 bit move
.mparam dst, src
    MOV     dst.w0, src & 0xFFFF
    MOV     dst.w2, src >> 16
.endm

#define PRU_R31_EVENT_SIG   31      // 30 for PRU0 and 31 for PRU1 This is 
                                    // a magical bit in R31 that is set when 
                                    // an interrupt occurs
// Interrupt related constants     
#define ARM_PRU1_INTERRUPT  22  
#define CONST_PRUSSINTC     C0
#define SICR_OFFSET         0x24

// Transfer related constants
#define XFR_BANK           11       // The shared register bank we use (10, 11 and 12 are valid)
#define PRU0_R31_VEC_VALID 32       // allows notification of program completion
#define PRU_EVTOUT_0       3        // the event number that is sent back
#define DATA_AVAILABLE     1        // Value for r8 to indicate data is available (Set by this PRU)
#define DATA_UNAVAILABLE   0        // Value r8 to indicate data is unavailable (Set by other PRU to indicate data is processed)
#define STOP_CMD           2        // Value for r7 to indicate that the program should halt

#define NUM_XFR_BYTES      32       // Number of bytes to transfer (includes all shared registers)
#define NUM_DATA_BYTES     (NUM_XFR_BYTES - 8)      // Number of data bytes per batch transfer (we subtract 8 to remove r7 and r8)

START:  // Initialization (Set up ADC, read some dummy samples, etc.)
        MOV     r8, DATA_AVAILABLE     // We transfer DATA_AVAILABLE in r8 whenever we send new data
        MOV     r7, 0
        MOV32   r1, (0x00000000 | ARM_PRU1_INTERRUPT)   // Create flag to clear linux interrupt
        SBCO    r1, CONST_PRUSSINTC, SICR_OFFSET, 4     // Some command to clear the linux interrupt
        
        MOV     r1, 0x00000000  // Set r1 as the temporary dummy register containing data to send over
        
SAMPLE_COLLECTION:              // NOTE, we collect samples out of the loop first
                                // so that we can replace some of the NOP operations
                                // associated with r9 with clean up instructions (if needed) at the end
        MOV     r9.b0, r1
        ADD     r1, r1, 1
        NOP
        MOV     r9.b1, r1
        ADD     r1, r1, 1
        NOP
        MOV     r9.b2, r1
        ADD     r1, r1, 1
        NOP
        MOV     r9.b3, r1
        ADD     r1, r1, 1
        NOP
        
MAINLOOP: // The NOP operations are to ensure that we always sample at a consistent rate
        MOV     r10.b0, r1
        ADD     r1, r1, 1
        NOP
        MOV     r10.b1, r1
        ADD     r1, r1, 1
        NOP
        MOV     r10.b2, r1
        ADD     r1, r1, 1
        NOP
        MOV     r10.b3, r1
        ADD     r1, r1, 1
        NOP
        
        MOV     r11.b0, r1
        ADD     r1, r1, 1
        NOP
        MOV     r11.b1, r1
        ADD     r1, r1, 1
        NOP
        MOV     r11.b2, r1
        ADD     r1, r1, 1
        NOP
        MOV     r11.b3, r1
        ADD     r1, r1, 1
        NOP
        
        MOV     r12.b0, r1
        ADD     r1, r1, 1
        NOP
        MOV     r12.b1, r1
        ADD     r1, r1, 1
        NOP
        MOV     r12.b2, r1
        ADD     r1, r1, 1
        NOP
        MOV     r12.b3, r1
        ADD     r1, r1, 1
        NOP
        
        MOV     r13.b0, r1
        ADD     r1, r1, 1
        NOP
        MOV     r13.b1, r1
        ADD     r1, r1, 1
        NOP
        MOV     r13.b2, r1
        ADD     r1, r1, 1
        NOP
        MOV     r13.b3, r1
        ADD     r1, r1, 1
        NOP
        
        MOV     r14.b0, r1
        ADD     r1, r1, 1
        NOP
        MOV     r14.b1, r1
        ADD     r1, r1, 1
        NOP
        MOV     r14.b2, r1
        ADD     r1, r1, 1
        NOP
        MOV     r14.b3, r1
        ADD     r1, r1, 1
        XOUT    XFR_BANK, r7, NUM_XFR_BYTES       // Move all samples to Bank0
        
        MOV     r9.b0, r1
        ADD     r1, r1, 1
        NOP
        MOV     r9.b1, r1
        ADD     r1, r1, 1
        NOP
        MOV     r9.b2, r1
        ADD     r1, r1, 1
        NOP
        MOV     r9.b3, r1
        ADD     r1, r1, 1
        QBBC    MAINLOOP, r31, PRU_R31_EVENT_SIG      // Exit when receive an interrupt
        
        MOV     r7, STOP_CMD
        XOUT    XFR_BANK, r7, 8       // Inform PRU_MEM that we have finished
END:
        //MOV     R31.b0, PRU0_R31_VEC_VALID | PRU_EVTOUT_0 // Not needed here because the other PRU signals Linux that execution is done
        HALT                    // halt the pru program

        
