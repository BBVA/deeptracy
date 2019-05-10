VERSIONS = 2.7 3.4 3.5 3.6 3.7

.PHONY : all $(VERSIONS)

all: $(VERSIONS)

$(VERSIONS):%:%
	docker build --build-arg PYTHON_VERSION=$@ -t bbvalabs/deeptracy-plugin-python:$@ .
ifdef DOCKER_USER
		docker push bbvalabs/deeptracy-plugin-python:$@
endif
