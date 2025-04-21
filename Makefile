symread: tools/symread16.c tools/symread32.c
	mkdir -p work
	$(CC) -o work/symread16 tools/symread16.c
	$(CC) -o work/symread32 tools/symread32.c

pipeline: 
		python3 tools/extract_symbols.py $(SYMBOL_DIR)
		python3 tools/fill_db.py $(SYMBOL_DIR)-output
		python3 tools/pathcrusher.py $(SYMBOL_DIR)

undname: tools/undname.c
	mkdir -p work
	$(CC) -o work/undname tools/undname.c

clean:
	rm -rf work

distclean:
	rm -rf db/components/*.yaml db/components/*/*.yaml