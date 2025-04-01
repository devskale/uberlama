
default:
	@echo "Run 'make install' first"
	@echo "Then run 'make server' or 'make client'"
	@echo "Then run 'make test'"

install:
	python3 -m venv .venv 
	.venv/bin/pip install -r requirements.txt

server:
	.venv/bin/python3 server.py

client:
	.venv/bin/python3 client.py

test:
	.venv/bin/python3 test.py

uninstall:
	rm -rf .venv

.PHONY: install
