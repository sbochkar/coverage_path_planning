IMAGE="sbochkarev/cpp_dev:latest"

xhost +

docker run --rm -it \
    -e DISPLAY=$DISPLAY \
    --net=host \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v $PWD:/workspace -w /workspace ${IMAGE} bash
