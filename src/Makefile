HEADERS = \
	pid.h

SRCS = \
	pid.c

OBJS = \
	$(SRCS:%.c=%.o)

LIB = libbjapid.a
DYLIB = libbjapid.A.dylib

TEST_PID_SRCS = test-pid.c
TEST_PID_OBJS = $(TEST_PID_SRCS:%.c=%.o)
TEST_PID_EXE = pid.test

THIRD_PARTY_DIR = ../3rd-party
CMOCKA_INCLUDE_DIR = $(THIRD_PARTY_DIR)/build-Debug/include
CMOCKA_LIBRARY = $(THIRD_PARTY_DIR)/build-Debug/lib/libcmocka.a

CC = cc
CFLAGS = -std=c11 -g -I$(CMOCKA_INCLUDE_DIR)
AR = ar
ARFLAGS = rv
LIBTOOL = libtool
LIBTOOLFLAGS = -dynamic -macosx_version_min 10.11 -lSystem

#
# Generic rule to generate objects
#
%.o : %.c $(HEADERS)
	$(CC) $(CFLAGS) -c -o $@ $<

%.o : %.c $(HEADERS)
	$(CC) $(CFLAGS) -c -o $@ $<


$(LIB) : $(OBJS)
	$(AR) $(ARFLAGS) $@ $(OBJS)

$(DYLIB) : $(OBJS)
	$(LIBTOOL) $(LIBTOOLFLAGS) -o $@ $(OBJS)

$(TEST_PID_EXE) : $(TEST_PID_OBJS) $(LIB)
	$(CC) $(CMOCKA_LIBRARY) $(TEST_PID_OBJS) $(LIB) -o $@

staticlib : $(LIB)

dylib : $(DYLIB)

all : $(LIB) $(DYLIB)

test : $(LIB) $(TEST_PID_EXE)
	./$(TEST_PID_EXE)

clean :
	rm -rf *~ *.o *.pyc __pycache__/ $(LIB) $(DYLIB) $(TEST_PID_EXE)

