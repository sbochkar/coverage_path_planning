IMAGE="sbochkarev/cpp_dev:latest"

docker run --rm -it -v $PWD:/workspace -w /workspace ${IMAGE} bash
