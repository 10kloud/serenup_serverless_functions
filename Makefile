clean:
	@rm -r .aws-sam

build:
	@sam build --use-container

deploy: build
	@sam deploy --no-confirm-changeset --parameter-overrides $(shell cat .sam-params)

local-api:
	@sam local start-api --parameter-overrides $(shell cat .sam-params)