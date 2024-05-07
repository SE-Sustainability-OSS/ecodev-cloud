# Line 1 to 20 are here to render the help output pretty, not to be read and even less understood!! :)
GREEN  := $(shell tput -Txterm setaf 2)
WHITE  := $(shell tput -Txterm setaf 7)
YELLOW := $(shell tput -Txterm setaf 3)
RESET  := $(shell tput -Txterm sgr0)
# From https://gist.github.com/prwhite/8168133#gistcomment-1727513
# Add the following 'help' target to your Makefile
# And add help text after each target name starting with ##
# A category can be added with @category
HELP_DESCRIPTION = \
    %help; \
    while(<>) { push @{$$help{$$2 // 'options'}}, [$$1, $$3] if /^([a-zA-Z\-]+)\s*:.*\#\#(?:@([a-zA-Z\-]+))?\s(.*)$$/ }; \
    print "usage: make [target]\n\n"; \
    for (sort keys %help) { \
    print "${WHITE}$$_:${RESET}\n"; \
    for (@{$$help{$$_}}) { \
    $$sep = " " x (32 - length $$_->[0]); \
    print "  ${YELLOW}$$_->[0]${RESET}$$sep${GREEN}$$_->[1]${RESET}\n"; \
    }; \
    print "\n"; }

# If the first argument is "produce-cordex-output"...
ifeq (produce-cordex-output,$(firstword $(MAKECMDGOALS)))
  # use the rest as arguments for "produce-cordex-output"
  RUN_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  # ...and turn them into do-nothing targets
  $(eval $(RUN_ARGS):;@:)
endif

# If the first argument is "produce-non-cordex-output"...
ifeq (produce-non-cordex-output,$(firstword $(MAKECMDGOALS)))
  # use the rest as arguments for "produce-non-cordex-output"
  RUN_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  # ...and turn them into do-nothing targets
  $(eval $(RUN_ARGS):;@:)
endif

# If the first argument is "quality-check"...
ifeq (quality-check,$(firstword $(MAKECMDGOALS)))
  # use the rest as arguments for "quality-check"
  RUN_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  # ...and turn them into do-nothing targets
  $(eval $(RUN_ARGS):;@:)
endif

# If the first argument is "create-master-file"...
ifeq (create-master-file,$(firstword $(MAKECMDGOALS)))
  # use the rest as arguments for "create-master-file"
  RUN_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  # ...and turn them into do-nothing targets
  $(eval $(RUN_ARGS):;@:)
endif

help:		## Show this help.
	@perl -e '$(HELP_DESCRIPTION)' $(MAKEFILE_LIST)

setup:		##@setup Install the pre-commit
	pip install pre-commit
	pre-commit install

all-tests:		##@tests Run all the tests
	docker exec ecodev_cloud python3.11 -m unittest discover tests

tests-unitary:		##@tests Run the unitary tests
	docker exec ecodev_cloud python3.11 -m unittest discover tests.unitary

tests-functional:		##@tests Run the functional tests
	docker exec ecodev_cloud python3.11 -m unittest discover tests.functional

prod-stop:            ##@docker Stop and remove a currently running ecodev_cloud container
	docker-compose -f docker-compose.yml down

prod-launch:            ##@docker Create all ecodev_cloud production containers in production configuration
	docker-compose -f docker-compose.yml up -d

dev-launch:            ##@docker Create all ecodev_cloud dev containers in dev configuration
	docker-compose up -d

prod-build:            ##@docker Build production ecodev_cloud image
	docker build --tag ecodev_cloud .

dev-build:            ##@docker Build dev ecodev_cloud image
	docker build --tag ecodev_cloud .  -f Dockerfile-dev

launch-jupyter:            ##@docker Launch a jupyter notebook from a fresh ecodev_cloud container. Only valid locally and on staging
	docker exec ecodev_cloud jupyter notebook --no-browser --ip 0.0.0.0 --allow-root --port 5000
