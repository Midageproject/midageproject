symread: tools/symread16.c tools/symread32.c
	mkdir -p work
	$(CC) -o work/symread16 tools/symread16.c
	$(CC) -o work/symread32 tools/symread32.c

pipeline: 
		python3 tools/extract_symbols.py $(SYMBOL_DIR)

clean:
	rm -rf work
