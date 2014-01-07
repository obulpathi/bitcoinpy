all:
	python bitcoinpy.py config.cfg

new:
	rm -rf ~/.bitcoinpy/*
	mkdir -p ~/.bitcoinpy/leveldb
	touch ~/.bitcoinpy/blocks.dat
	python bitcoinpy.py config.cfg
install:
	sudo apt-get install python-gevent libleveldb1 python-leveldb python-bsddb3 
