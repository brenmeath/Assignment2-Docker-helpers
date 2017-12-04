#!/bin/bash

# 1
curl -s -X GET -H 'Accept: application/json' http://localhost:8080/

# 2
curl -s -X GET -H 'Accept: application/json' http://localhost:8080/containers

# 3
curl -s -X GET -H 'Accept: application/json' http://localhost:8080/containers?state=running

# 4
curl -s -X GET -H 'Accept: application/json' http://localhost:8080/images

# 5
curl -s -X GET -H 'Accept: application/json' http://localhost:8080/services

# 6
curl -s -X GET -H 'Accept: application/json' http://localhost:8080/nodes

# 7
CONTAINER=$(docker ps -aq) # get first container in list
curl -s -X GET -H 'Accept: application/json' http://localhost:8080/containers/$CONTAINER

# 8
curl -s -X GET -H 'Accept: application/json' http://localhost:8080/containers/$CONTAINER/logs

# 9
IMAGE=$(docker images -q)
curl -X DELETE http://localhost:8080/images/$IMAGE

# 10
curl -X DELETE http://localhost:8080/containers/$CONTAINER

# 11
curl -X DELETE http://localhost:8080/containers

# 12
curl -X DELETE http://localhost:8080/images

# 13
curl -X POST -H 'Content-Type: application/json' http://localhost:8080/containers -d '{"image": "alpine","publish":"8081:22"}'

# 14
echo "FROM busybox" > Dockerfile
curl -H 'Accept: application/json' -F file=@Dockerfile http://localhost:8080/images

# 15
curl -X PATCH -H 'Content-Type: application/json' http://localhost:8080/containers/b6cd8ea512c8 -d '{"state": "running"}'

# 16
curl -s -X PATCH -H 'Content-Type: application/json' http://localhost:8080/images/7f2619ed1768 -d '{"tag": "test:1.0"}'
