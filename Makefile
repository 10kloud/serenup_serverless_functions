clean:
	@rm -r .aws-sam

build:
	@sam build --use-container

deploy: build
	@sam deploy --parameter-overrides $(shell cat .sam-params)