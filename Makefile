docs: docs/index.html

docs/index.html: api.yaml
	redoc-cli bundle -o docs/index.html api.yaml

.PHONY: clean
clean:
	rm docs/index.html
