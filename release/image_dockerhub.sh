# Deploy to DockerHub
VERSION=$(cat VERSION)
docker build -t bbvalabs/deeptracy:$VERSION -t bbvalabs/deeptracy:latest .
docker login -u $DOCKER_USER -p $DOCKER_PASS
docker push bbvalabs/deeptracy:$VERSION
docker push bbvalabs/deeptracy:latest
