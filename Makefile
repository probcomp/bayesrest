docs: docs/index.html

docs/index.html: api.yaml
	docker run --entrypoint docker-entrypoint.sh \
                   -v ${PWD}:/app bayesrest_app redoc-cli bundle \
                   -o docs/index.html api.yaml

.PHONY: clean
clean:
	rm docs/index.html
