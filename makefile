all:
	python bitcoin.py config.cfg
new:
	rm -rf ~/.bitcoin/*
	mkdir -p ~/.bitcoin/leveldb
	touch ~/.bitcoin/blocks.dat
	python bitcoin.py config.cfg
node:
	rm -rf ~/.bitcoin1/*
	mkdir -p ~/.bitcoin1/leveldb
	touch ~/.bitcoin1/blocks.dat
	python bitcoin.py config1.cfg
node1:
	python bitcoin.py config1.cfg
node2:
	python bitcoin.py config2.cfg
node3:
	python bitcoin.py config3.cfg
install:
	sudo apt-get --yes install python-gevent libleveldb1 python-leveldb
	git clone git@github.com:obulpathi/python-bitcoinlib.git ~/bitcoin1
	mv ~/bitcoin1/bitcoin ~/bitcoin
	rm -rf ~/bitcoin1
