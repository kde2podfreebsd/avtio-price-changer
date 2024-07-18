docker_build:
	docker build -t avito_price_changer .

docker_run:
	docker run -it -p 8000:8000 avito_price_changer

clean_repo:
	find . -name __pycache__ -type d -print0|xargs -0 rm -r --
	rm -rf .idea/

fix_git_cache:
	git rm -rf --cached .
	git add .

.PHONY clean: clean fix_git_cache

docker_clean:
	sudo docker stop $$(sudo docker ps -a -q) || true
	sudo docker rm $$(sudo docker ps -a -q) || true
