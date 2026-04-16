{
  "name": "DevOps OS - Multi-Language Development Environment",
  "build": {
    "dockerfile": "Dockerfile",
    "args": __BUILD_ARGS__
  },
  "features": __FEATURES__,
  "mounts": [
    "source=/var/run/docker.sock,target=/var/run/docker.sock,type=bind"
  ],
  "customizations": {
    "vscode": {
      "extensions": __EXTENSIONS__
    }
  }__FORWARD_PORTS_BLOCK__,
  "postCreateCommand": __POST_CREATE_COMMAND__
}
