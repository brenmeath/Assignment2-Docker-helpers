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
|Request|Resource                             |Explanation                                        |
|-------|-------------------------------------|---------------------------------------------------|
|GET    |/containers	                        |List all containers                                |
|GET    |/containers?state=running		        |List running containers                            |
|GET    |/containers/<id>	                    |Inspect a specific container                       |
|GET    |/containers/<id>/logs	              |"Dump specific container logs"                     |
4	
GET /images	"List all images"
5	
GET /services	"List all services"
6	
GET /nodes	"List all nodes"
7	
POST /images	"Create a new image"
8	
POST /containers	"Create a new container"
9	
PATCH /containers/<id>	"Change a container's state"
10	
PATCH /images/<id>	"Change a specific image's attributes"
11	
DELETE /containers/<id>	"Delete a specific container"
12	
DELETE /containers	"Delete all containers (including running)"
13	
DELETE /images/<id>	"Delete a specific image"
14	
DELETE /images	"Delete all images"

### Video
[![Video](http://img.youtube.com/vi/ixmQ9d7WFaQ/0.jpg)](https://www.youtube.com/watch?v=ixmQ9d7WFaQ)
