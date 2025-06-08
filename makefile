
DOC_UP:
	docker-compose up -d
DOC_BUILD:
	docker-compose build
DOC_DOWN:
	docker-compose down 

flask_container:
	docker exec  -it exercice_journe_observation-flaskapp-1 bash
log_flask_container:
	docker logs -f exercice_journe_observation-flaskapp-1
List_docker_container:
	docker ps -a