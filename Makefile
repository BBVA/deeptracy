plugins_dependencycheck = plugins/dependencycheck
plugins_mvn = plugins/mvn
plugins_npm = plugins/npm
plugins_python = plugins/python
buildbot_plugins = $(plugins_dependencycheck) $(plugins_mvn) $(plugins_npm) $(plugins_python)

.PHONY: ALL image start stop down logs status plugins $(buildbot_plugins)

ALL: down image plugins start logs

image: docker_login
	docker build . -f Dockerfile.server -t bbvalabs/deeptracy-server
	docker build . -f Dockerfile.buildbot -t bbvalabs/deeptracy-buildbot
ifdef DOCKER_USER
		docker push bbvalabs/deeptracy-server
		docker push bbvalabs/deeptracy-buildbot
endif

start:
	cd compose && docker-compose -f docker-compose.yaml -f docker-compose-database.yml up --scale deeptracy-worker-analyses=8 --scale deeptracy-worker-providers=8 -d

stop:
	cd compose && docker-compose -f docker-compose.yaml -f docker-compose-database.yml stop

down:
	cd compose && docker-compose -f docker-compose.yaml -f docker-compose-database.yml down -v

logs:
	cd compose && docker-compose -f docker-compose.yaml -f docker-compose-database.yml logs -f

status:
	cd compose && docker-compose -f docker-compose.yaml -f docker-compose-database.yml ps

plugins: docker_login $(buildbot_plugins)

$(buildbot_plugins):
	$(MAKE) --directory=$@

docker_login:
ifdef DOCKER_USER
	docker login -u $${DOCKER_USER} -p $${DOCKER_PASS}
endif
