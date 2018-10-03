.PHONY: ALL image start stop down logs status plugins


ALL: down image plugins start logs

image:
	docker build . -f Dockerfile.server -t deeptracy-server
	docker build . -f Dockerfile.buildbot -t deeptracy-buildbot
start:
	docker-compose up --scale deeptracy-worker-analyses=8 --scale deeptracy-worker-providers=8 -d
stop:
	docker-compose stop
down:
	docker-compose down -v
logs:
	docker-compose logs -f
status:
	docker-compose ps
plugins:
	cd plugins/dependencycheck && make
	cd plugins/mvn && make
	cd plugins/npm && make
	cd plugins/python && make
