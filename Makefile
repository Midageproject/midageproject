symread: tools/symread16.c tools/symread32.c
	mkdir -p work
	$(CC) -o work/symread16 tools/symread16.c
	$(CC) -o work/symread32 tools/symread32.c

clean:
	rm -rf work
