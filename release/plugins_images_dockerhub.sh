## Deploy plugin images to DockerHub
for d in $(find $(pwd)/plugins -maxdepth 2)
do
  # Build docker image
  if [[ $d == *"Dockerfile" ]]; then
        PLUGIN_PATH=$(echo $d | sed 's/Dockerfile//g')

        # Go to the plugin home
        cd $PLUGIN_PATH

        # Build docker
        VERSION=$(cat VERSION)
        IMAGE_NAME=$(cat IMAGE_NAME)

        echo "[*] Building image for $IMAGE_NAME"

        docker build -t bbvalabs/$IMAGE_NAME:$VERSION .
        docker login -u $DOCKER_USER -p $DOCKER_PASS

        echo "[*] Uploading image"
        docker push bbvalabs/$IMAGE_NAME:$VERSION
        docker push bbvalabs/$IMAGE_NAME:latest
  fi
done
