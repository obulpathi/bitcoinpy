all:
	python bitcoin.py config.cfg
new:
	rm -rf ~/.bitcoinpy/*
	mkdir -p ~/.bitcoinpy/leveldb
	touch ~/.bitcoinpy/blocks.dat
	python bitcoin.py config.cfg
