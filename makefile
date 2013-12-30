all:
	python bitcoinpy.py config.cfg
new:
	rm -rf ~/.bitcoinpy/*
	mkdir -p ~/.bitcoinpy/leveldb
	touch ~/.bitcoinpy/blocks.dat
	python bitcoinpy.py config.cfg
