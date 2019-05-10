VERSIONS = 4.0.2

.PHONY : all $(VERSIONS)

all: $(VERSIONS)

$(VERSIONS):%:%
	docker build --build-arg DC_VERSION=$@ -t bbvalabs/deeptracy-plugin-owasp:$@ .
ifdef DOCKER_USER
		docker push bbvalabs/deeptracy-plugin-owasp:$@
endif
