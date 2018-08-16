image:
	docker build . -t deeptracy
start:
	docker-compose up --scale deeptracy-worker=8 -d
stop:
	docker-compose stop
down:
	docker-compose down -v
logs:
	docker-compose logs -f
