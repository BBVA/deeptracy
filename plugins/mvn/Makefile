VERSIONS = 3.5-ibmjava-8 3.5-jdk-10 3.5-jdk-11 3.5-jdk-7 3.5-jdk-8 3.5-jdk-9

.PHONY : all $(VERSIONS)

all: $(VERSIONS)

$(VERSIONS):%:%
	docker build --build-arg MVN_VERSION=$@ -t bbvalabs/deeptracy-plugin-mvn:$@ .
ifdef DOCKER_USER
		docker push bbvalabs/deeptracy-plugin-mvn:$@
endif
