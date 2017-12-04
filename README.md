# Docker HTTP API
A HTTP api written in python for my Cloud Computing assignment 
Date of submission: 03/12/2017  

### How to run
```bash
python3 container-server.py
```

### Python module dependencies
* Flask

### API endpoints
|Request  |Resource                             |Explanation                                    |
|---------|-------------------------------------|-----------------------------------------------|
|`GET`    |`/containers`                        |List all containers                            |
|`GET`    |`/containers?state=running`		      |List running containers                        |
|`GET`    |`/containers/<id>`	                  |Inspect a specific container                   |
|`GET`    |`/containers/<id>/logs`	            |Dump specific container logs                   |
|`GET`    |`/images`	                          |List all images                                |
|`GET`    |`/services`	                        |List all services                              |
|`GET`    |`/nodes`	                            |List all nodes                                 |
|`POST`   |`/images`	                          |Create a new image                             |
|`POST`   |`/containers`	                      |Create a new container                         |
|`PATCH`  |`/containers/<id>`	                  |Change a container's state                     |
|`PATCH`  |`/images/<id>`	                      |Change a specific image's attributes           |
|`DELETE` |`/containers/<id>`	                  |Delete a specific container                    |
|`DELETE` |`/containers`	                      |Delete all containers (including running)      |
|`DELETE` |`/images/<id>`	                      |Delete a specific image                        |
|`DELETE` |`/images`	                          |Delete all images                              |

### Video
[![Video](http://img.youtube.com/vi/ixmQ9d7WFaQ/0.jpg)](https://www.youtube.com/watch?v=ixmQ9d7WFaQ)
