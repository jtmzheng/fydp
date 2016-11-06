// This program sends data the other PRU using the pru interupt
// r9 to r29 are used (21 registers)
// r7 is set to STOP_CMD to indicate to pruMem that processing has finished.
// r8 is set to DATA_AVAILABLE to indicate to pruMem that new data is available

.origin 0                       // start of program in PRU memory
.entrypoint START               // program entry point (for a debugger)

#define NOP                OR r1, r1, r1       // PRU NOP Operation
.macro  MOV32
.mparam dst, src
    MOV     dst.w0, src & 0xFFFF
    MOV     dst.w2, src >> 16
.endm
#define PRU_R31_EVENT_SIG   31      // 30 for PRU0 and 31 for PRU1      
#define ARM_PRU1_INTERRUPT  22
#define CONST_PRUSSINTC     C0
#define SICR_OFFSET         0x24

#define XFR_BANK           11
#define PRU0_R31_VEC_VALID 32       // allows notification of program completion
#define PRU_EVTOUT_0       3        // the event number that is sent back
#define DATA_AVAILABLE     1
#define DATA_UNAVAILABLE   0
#define STOP_CMD           2

#define NUM_XFR_BYTES      32       // Number of bytes (including r5 (communication register) to transfer)
#define NUM_DATA_BYTES     (NUM_XFR_BYTES - 8)      // Number of bytes per batch transfer

START:  // Initialization (Set up ADC, read some dummy samples, etc.)
        MOV     r8, DATA_AVAILABLE     // Start command set for PRU_MEM
        MOV     r7, 0
        MOV32   r1, (0x00000000 | ARM_PRU1_INTERRUPT)   // Set flag to clear interrupt
        SBCO    r1, CONST_PRUSSINTC, SICR_OFFSET, 4     // Clear interrupt
        
        MOV     r1, 0x00000000  // Set r1 as the temporary dummy register
        
SAMPLE_COLLECTION:              // NOTE, we collect samples out of the loop first
                                // so that at the end, when we transfer the data
                                // all the registers are full
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
        
MAINLOOP:
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
        //MOV     R31.b0, PRU0_R31_VEC_VALID | PRU_EVTOUT_0
        HALT                    // halt the pru program

        
