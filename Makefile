symread: tools/symread.c
	mkdir -p work
	$(CC) -o work/symread tools/symread.c

clean:
	rm -rf work
