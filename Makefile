prepare: tools/symread16.c tools/symread32.c tools/unndname.c
	mkdir -p work dist
	$(CC) -o work/symread16 tools/symread16.c
	$(CC) -o work/symread32 tools/symread32.c
	$(CC) -o work/undname tools/undname.c

pipeline: 
		python3 tools/extract_symbols.py $(SYMBOL_DIR)
		python3 tools/fill_db.py $(SYMBOL_DIR)-output
		python3 tools/pathcrusher.py $(SYMBOL_DIR)
		python3 explorer/generate_explorer.py $(SYMBOL_DIR)-output

clean:
	rm -rf work

distclean:
	rm -rf dist/*

dbclean:
	rm -rf db/components/*.yaml db/components/*/*.yaml
