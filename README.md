# The Challenge Checker Service

## Technologies!

- The service will be written in [Python](https://python.org/) 3.6+.
- The main web framework will be [FastAPI](https://fastapi.tiangolo.com/).
- All the requirements for the env will be provided in requirements.txt file.
- Containerizing the service will be using [Docker](https://www.docker.com/).

### Installation

The service requires [Python](https://python.org/) v3.6+ to run.

To setup the dev environment run the following commands

```sh
# clone the Repo
$ git clone https://github.com/altooro/challenge-checker.git challenge-checker
# change dir into the service dir
$ cd challenge-checker
# make sure you have a virtual environment in the root dir of the service by running
$ python -m venv env
# an env folder should be created, that folder contains all the dependecies the service will need
# before runnng any python command you should make sure your terminal is using the virtual environment
$ source env/Scripts/activate
# now install all the libraries required by the service to the virtual environment by running
$ pip install -r requirements.txt
# if you ever had to install a new library make sure to update the requirements.txt
$ pip freeze > requirements.txt
# you will need also to create a .env file that has all the development environment variables for the service
# if everything worked, you should be able to run the following command to start the server
$ bash run.dev.sh
```

### Requires env vars

    * ORCH_URL="url to the coding orchestrator"
