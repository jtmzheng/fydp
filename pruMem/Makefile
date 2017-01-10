CC = gcc

TARGET = DataServer

LDLIBS = -lpthread \
	-lprussdrv \

DEPS = commUtils.o \
	dataBuffer.o \
	pruCtrl.o \

all: $(TARGET)

$(TARGET): clean $(DEPS) $(TARGET).c
	$(CC) $(CFLAGS) $(DEPS) $(TARGET).c -o DataServer $(LDLIBS)

dataBuffer.o: dataBuffer.c
	$(CC) $(CFLAGS) -c dataBuffer.c -o dataBuffer.o

commUtils.o: commUtils.c
	$(CC) $(CFLAGS) -c commUtils.c -o commUtils.o

pruCtrl.o: pruCtrl.c
	$(CC) $(CFLAGS) -c pruCtrl.c -o pruCtrl.o

clean:
	rm -f *.o $(TARGET)
