from flask import Flask, Response, request
from json import dumps as jdumps
from subprocess import Popen, PIPE
from os import path, remove, makedirs
import re

app = Flask(__name__)
app.config['UPLOAD_DIR'] = 'upload'

@app.route("/")
def index():
	# dict describing the API usage, which will be converted to json
	helpdict = {
		"Available API endpoints": [
		{"GET /containers": "List all containers"},
		{"GET /containers?state=running": "List running containers"},
		{"GET /containers/<id>": "Inspect a specific container"},
		{"GET /containers/<id>/logs": "Dump specific container logs"},
		{"GET /images": "List all images"},
		{"GET /services": "List all services"},
		{"GET /nodes": "List all nodes"},
		{"POST /images": "Create a new image"},
		{"POST /containers": "Create a new container"},
		{"PATCH /containers/<id>": "Change a container\'s state"},
		{"PATCH /images/<id>": "Change a specific image\'s attributes"},
		{"DELETE /containers/<id>": "Delete a specific container"},
		{"DELETE /containers": "Delete all containers (including running)"},
		{"DELETE /images/<id>": "Delete a specific image"},
		{"DELETE /images": "Delete all images"}
		]
	}
	
	resp = jdumps(helpdict)
	return Response(response=resp, mimetype="application/json")

@app.route('/containers', methods=['GET'])
def containers_index():
	"""
	List all containers
 
	curl -s -X GET -H 'Accept: application/json' http://localhost:8080/containers
	curl -s -X GET -H 'Accept: application/json' http://localhost:8080/containers?state=running

	"""
	if request.args.get('state') == 'running': 
		output = docker('ps --format \'{{.ID}}\t{{.Image}}\t{{.Command}}\t{{.CreatedAt}}\t{{.Status}}\t{{.Ports}}\t{{.Names}}\'')
		resp = jdumps(docker_ps_to_array(output))
	else:
		
		cmd = ['docker', 'ps', '-a', '--format', '\'{{.ID}}\t{{.Image}}\t{{.Command}}\t{{.CreatedAt}}\t{{.Status}}\t{{.Ports}}\t{{.Names}}\'']
		process = Popen(cmd, stdout=PIPE, stderr=PIPE, universal_newlines=True)
		stdout, stderr = process.communicate()
	
		output = stderr + stdout
		resp = jdumps(docker_ps_to_array(output))
	
	return Response(response=resp, mimetype="application/json")

@app.route('/images', methods=['GET'])
def images_index():
	"""
	List all images 
	
	curl -s -X GET -H 'Accept: application/json' http://localhost:8080/images
	
	Complete the code below generating a valid response. 
	"""
	
	output = docker('images')
	resp = jdumps(docker_images_to_array(output))
	
	return Response(response=resp, mimetype="application/json")

@app.route('/services', methods=['GET'])
def services_index():
	"""
	List all services
	
	curl -s -X GET -H 'Accept: application/json' http://localhost:8080/services
	
	"""
	
	output = docker('service ls -q')
	services = output.split('\n')
	resp = jdumps(services)
	
	return Response(response=resp, mimetype="application/json")

@app.route('/nodes', methods=['GET'])
def nodes_index():
	"""
	List all nodes
	
	curl -s -X GET -H 'Accept: application/json' http://localhost:8080/nodes
	
	"""
	
	output = docker('node ls -q')
	nodes = output.split('\n')
	resp = jdumps(nodes)
	
	return Response(response=resp, mimetype="application/json")

@app.route('/containers/<id>', methods=['GET'])
def containers_show(id):
	"""
	Inspect specific container
	
	curl -s -X GET -H 'Accept: application/json' http://localhost:8080/containers/<id>
	
	"""
	output = docker('inspect {}'.format(id))
	resp = output
	return Response(response=resp, mimetype="application/json")

@app.route('/containers/<id>/logs', methods=['GET'])
def containers_log(id):
	"""
	Dump specific container logs
	
	curl -s -X GET -H 'Accept: application/json' http://localhost:8080/containers/<id>/logs

	"""
	output = docker('logs {}'.format(id))
	resp = jdumps('{{"logs": "{}"}}'.format(output))
	return Response(response=resp, mimetype="application/json")

@app.route('/images/<id>', methods=['DELETE'])
def images_remove(id):
	"""
	Delete a specific image
	
	curl -X DELETE http://localhost:8080/images/<id>
	
	"""
	docker ('rmi {}'.format(id))
	resp = '{"id": "%s"}' % id
	return Response(response=resp, mimetype="application/json")

@app.route('/containers/<id>', methods=['DELETE'])
def containers_remove(id):
	"""
	Delete a specific container - must be already stopped/killed
	
	curl -X DELETE http://localhost:8080/containers/<id>
	
	"""
	output = docker('rm {}'.format(id))
	resp = '{"output": "%s"}' % output
	return Response(response=resp, mimetype="application/json")

@app.route('/containers', methods=['DELETE'])
def containers_remove_all():
	"""
	Force remove all containers - dangrous!
	
	curl -X DELETE http://localhost:8080/containers

	"""
	containers = docker('ps -aq').replace('\n', ' ')
	
	if containers != '':
		output = docker('rm {}'.format(containers))
		resp = '{"Deleted": ['
		for id in output.split('\n'):
			if id != '':
				resp += '{{"id": "{}"}}, '.format(id)
		resp = resp[:-2] # remove extra comma
		resp += ']}'
	else:
		resp = '{"Error": "No containers exist"}'
	
	return Response(response=resp, mimetype="application/json")

@app.route('/images', methods=['DELETE'])
def images_remove_all():
	"""
	Force remove all images - dangerous!
	
	curl -X DELETE http://localhost:8080/images

	"""
	
	images = docker('images -aq').replace('\n', ' ')
	if images != '':
		output = docker('rmi {}'.format(images))
		resp = '{"Deleted": ['
		for id in output.split('\n'):
			if id != '':
				if id.startswith('Deleted'):
					resp += '{{"id": "{}"}}, '.format(id.split(':')[2])
		resp = resp[:-2] # remove extra comma
		resp += ']}'
	else:
		resp = '{"Error": "No images exist"}'
	
	return Response(response=resp, mimetype="application/json")


@app.route('/containers', methods=['POST'])
def containers_run():
	"""
	Run container (from existing image using id or name)

	curl -X POST -H 'Content-Type: application/json' http://localhost:8080/containers -d '{"image": "my-app"}'
	curl -X POST -H 'Content-Type: application/json' http://localhost:8080/containers -d '{"image": "b14752a6590e"}'
	curl -X POST -H 'Content-Type: application/json' http://localhost:8080/containers -d '{"image": "b14752a6590e","publish":"8081:22"}'

	"""
	
	args = 'run -d '
	
	body = request.get_json(force=True)
	if 'image' in body:
		args += '{} '.format(body['image'])
		if 'publish' in body:
			args += '-p {}'.format(body['publish'])
		#id = dockerMultipleParams(*(args + (image,)))[0:12]
		id = docker(args)
		resp = '{{"id": "{}"}}'.format(id.replace('\n',''))
	else:
		resp = '{"Error":"no value specified for "image" attribute"}'
	return Response(response=resp, mimetype="application/json")


@app.route('/images', methods=['POST'])
def images_create():
	"""
	Create image (from uploaded Dockerfile)

	curl -H 'Accept: application/json' -F file=@Dockerfile http://localhost:8080/images

	"""
	dockerfile_path = path.join(app.config['UPLOAD_DIR'], 'Dockerfile')
	if 'file' not in request.files:
		output = '{"error": "No file uploaded"}'
	else:
		dockerfile = request.files['file']
		if dockerfile.filename == '':
			output = '{"error": "No selected file"}'
		else:
			dockerfile.save(dockerfile_path)
			output = docker('build {}'.format(app.config['UPLOAD_DIR']))
	
	remove(dockerfile_path)
	
	match = re.search('Successfully built (.+?)\n', output)
	if match:
		id = match.group(1)
		output = '{{"id": "{}"}}'.format(id)
	else:
		output = '{"Error": "Build unsuccessful"}'
	
	resp = output
	return Response(response=resp, mimetype="application/json")

@app.route('/containers/<id>', methods=['PATCH'])
def containers_update(id):
	"""
	Update container attributes (support: state=running|stopped)

	curl -X PATCH -H 'Content-Type: application/json' http://localhost:8080/containers/b6cd8ea512c8 -d '{"state": "running"}'
	curl -X PATCH -H 'Content-Type: application/json' http://localhost:8080/containers/b6cd8ea512c8 -d '{"state": "stopped"}'

	"""
	
	output = ''
	
	body = request.get_json(force=True)
	state = body['state']
	
	if state == 'running':
		output = docker('restart {}'.format(id))
	if state == 'stopped':
		output = docker('stop {}'.format(id))
	resp = '{{"id": "{}"}}'.format(output)
	
	return Response(response=resp, mimetype="application/json")

@app.route('/images/<id>', methods=['PATCH'])
def images_update(id):
	"""
	Update image attributes (support: name[:tag])  tag name should be lowercase only

	curl -s -X PATCH -H 'Content-Type: application/json' http://localhost:8080/images/7f2619ed1768 -d '{"tag": "test:1.0"}'

	"""
	
	output = ''
	
	body = request.get_json(force=True)
	tag = body['tag'].lower()
	
	output = docker('image tag {} {}'.format(id, tag))
	
	if output == '':
		resp = '{"status": "success"}'
	else:
		resp = '{{"status": "failure", "output": "{}"}}'.format(output)
	
	return Response(response=resp, mimetype="application/json")

def docker(args):
	cmd = ['docker']
	cmd += args.split()
	process = Popen(cmd, stdout=PIPE, stderr=PIPE, universal_newlines=True)
	stdout, stderr = process.communicate()
	
	return stderr + stdout

# 
# Docker output parsing helpers
#

#
# Parses the output of a Docker PS command to a python List
# 
def docker_ps_to_array(output):
	all = []
	for c in [line.split('\t') for line in output.splitlines()[1:]]:
		each = {}
		if len(c) == 1:
			return all
		each['Container ID'] = c[0][1:] # remove preceeding single quote
		each['Image'] = c[1]
		each['Command'] = c[2]
		each['Created'] = c[3]
		each['Status'] = c[4]
		each['Ports'] = c[5]
		each['Name'] = c[6]
		all.append(each)
	return all

#
# Parses the output of a Docker logs command to a python Dictionary
# (Key Value Pair object)
def docker_logs_to_object(id, output):
	logs = {}
	logs['id'] = id
	all = []
	for line in output.splitlines():
		all.append(line)
	logs['logs'] = all
	return logs

#
# Parses the output of a Docker image command to a python List
# 
def docker_images_to_array(output):
	all = []
	for c in [line.split() for line in output.splitlines()[1:]]:
		each = {}
		each['id'] = c[2]
		each['tag'] = c[1]
		each['name'] = c[0]
		all.append(each)
	return all

if __name__ == "__main__":
	# create folder to store POST request files
	if not path.exists(app.config['UPLOAD_DIR']):
		makedirs(app.config['UPLOAD_DIR'])
	
	app.run(host="0.0.0.0",port=8080, debug=True)
