VERSIONS = 8.11.4 8.11 8 6.14.4 6.14 6 10.9.0 10.9 10

.PHONY : all $(VERSIONS)

all: $(VERSIONS)

$(VERSIONS):%:%
	docker build --build-arg NODE_VERSION=$@ -t bbvalabs/deeptracy-plugin-npm:$@ .
ifdef DOCKER_USER
		docker push bbvalabs/deeptracy-plugin-npm:$@
endif
