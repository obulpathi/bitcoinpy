.PHONY: genesis

# Code from here
# https://bitcointalk.org/index.php?topic=181981.0

default:
	gcc genesis.c -o genesis -lcrypto

install:
	sudo apt-get install libssl-dev

generate:
	python genesis.py

sign:
	python signtx.py

genesis:
	./genesis 048b943243eb1419323ca6f13f88cdfa6e90f842468a5c265f3847a40f6390f72721c5ce06e4147bd0eac09424125cb647b686166c0f4da2b9661eb0e40d93954d "Time stamp" 100728831
