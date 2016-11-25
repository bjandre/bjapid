HEADERS = \
	pid.h

SRCS = \
	pid.c

OBJS = \
	$(SRCS:%.c=%.o)

LIB = libbjautil.a

TEST_PID_SRCS = test-pid.c
TEST_PID_OBJS = $(TEST_PID_SRCS:%.c=%.o)
TEST_PID_EXE = pid.test

THIRD_PARTY_DIR = ../3rd-party
CMOCKA_INCLUDE_DIR = $(THIRD_PARTY_DIR)/build-Debug/include
CMOCKA_LIBRARY = $(THIRD_PARTY_DIR)/build-Debug/lib/libcmocka.a

CC = cc
CFLAGS = -std=c11 -g -I$(CMOCKA_INCLUDE_DIR)

#
# Generic rule to generate objects
#
%.o : %.c $(HEADERS)
	$(CC) $(CFLAGS) -c -o $@ $<


$(LIB) : $(OBJS)
	$(AR) $(ARFLAGS) $@ $(OBJS)

pid.test : $(TEST_PID_OBJS) $(LIB)
	$(CC) $(CMOCKA_LIBRARY) $(TEST_PID_OBJS) $(LIB) -o $@

all : $(LIB)

test : $(LIB) $(TEST_PID_EXE)
	./$(TEST_PID_EXE)

clean :
	rm -rf *~ *.o $(LIB) $(TEST_PID_EXE)

