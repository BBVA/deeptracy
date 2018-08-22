VERSIONS = 8.11.4 8.11 8 6.14.4 6.14 6 10.9.0 10.9 10

all: $(VERSIONS)

$(VERSIONS):%:%
	docker build --build-arg NODE_VERSION=$@ -t deeptracy-node:$@ .
