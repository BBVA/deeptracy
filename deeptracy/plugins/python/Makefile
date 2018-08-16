VERSIONS = 2.7 3.4 3.5 3.6 3.7

all: $(VERSIONS)

$(VERSIONS):%:%
	docker build --build-arg PYTHON_VERSION=$@ -t deeptracy-python:$@ .
