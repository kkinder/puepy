build:
	docker build -f Dockerfile.pytests -t puepy-pytest .

test: build
	docker run -it --rm puepy-pytest
