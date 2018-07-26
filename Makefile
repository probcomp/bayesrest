BDB := bdb/counties_v6.bdb
TAR := loom/loom.tar

NB_UID := $(shell id -u)

docs: docs/index.html

docs/index.html: api.yaml
	redoc-cli bundle -o docs/index.html api.yaml

.PHONY: clean
clean:
	rm docs/index.html

extract: $(TAR)
	tar -xvf loom/loom.tar

up:
	@NB_UID=${NB_UID} docker-compose\
		up
