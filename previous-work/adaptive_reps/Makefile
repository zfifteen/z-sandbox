# Standalone Enhanced Demo Makefile - Links z5d_predictor.c + GMP for M1 Max
CC = gcc
CFLAGS = -std=c11 -Wall -Wextra -O3 -march=armv8.6-a+fp16 -DNDEBUG \
         -I.. -I../include \
         $(shell pkg-config --cflags gmp 2>/dev/null || echo "-I/opt/homebrew/include")
LDFLAGS = $(shell pkg-config --libs gmp 2>/dev/null || echo "-L/opt/homebrew/lib -lgmp") -lm

TARGET = adaptive_demo
SRCS = adaptive_demo.c ../z5d_predictor.c
OBJS = $(SRCS:.c=.o)

all: $(TARGET)

$(TARGET): $(OBJS)
	@echo "Linking $(TARGET)..."
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

%.o: %.c
	@echo "Compiling $<..."
	$(CC) $(CFLAGS) -c $< -o $@

run: $(TARGET)
	./$(TARGET)

clean:
	rm -f $(TARGET) $(OBJS)

.PHONY: all run clean
