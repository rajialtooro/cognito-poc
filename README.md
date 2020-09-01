# The Challenge Checker Service

## Request:
- Type: <b>POST</b>
- Route: /solution-orch
- Body:
```json
{
  "lang": "python/java/etc..",
  "code": "solution code goes here",
  "challengeId": "UID of challenge"
}
```

## Result(example):
- Option 1: 
```json
{
    "linter": null,
    "compiler": {
        "isError": false,
        "output": "78\n"
    },
    "solved": true
}
```

- Option 2(In case solution does not contain "white-listed" words):
```json
{
    "solved": false,
    "linter": null,
    "Compiler": null
}
```

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
$ git clone https://github.com/altooro/solution-orch.git solution-orchestrator
# change dir into the service dir
$ cd solution-orch
# make sure you have a virtual environment in the root dir of the service by running
$ python -m venv env
# an env folder should be created, that folder contains all the dependecies the service will need
# before runnng any python command you should make sure your terminal is using the virtual environment
$ source env/Scripts/activate # for Windows
$ source env/bin/activate # for Linux
# now install all the libraries required by the service to the virtual environment by running
$ pip install -r requirements.txt
# if you ever had to install a new library make sure to update the requirements.txt
$ pip freeze > requirements.txt
# you will need also to create a .env file that has all the development environment variables for the service
# if everything worked, you should be able to run the following command to start the server
$ bash run.dev.sh
```

### Requires env vars

    * FREE_ORCH_URL="url to the coding orchestrator"
    * CHALLENGES_SERVICE_URL="URL to the challenges service"
