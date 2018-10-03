VERSIONS = latest

all: $(VERSIONS)

$(VERSIONS):%:%
	docker build --build-arg DC_VERSION=$@ -t deeptracy-owasp-dependency-check:$@ .
