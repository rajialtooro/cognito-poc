# The Solutions Checking and Orchestrating Service

### APIs:

- [Single challlenge submission](#challenge)
- [Assignment submission](#assignment)

## <a name="challenge"></a>Check a single challenge:

### Request:

- Type: <b>POST</b>
- Route: /solution-orch
- Body:

```json
{
  "lang": "python/java/etc..",
  "code": "solution code goes here",
  "challengeId": "UID of challenge",
  "courseId": "UID of course",
  "toSubmit": true || false,
  "time_spent: time it took to solved,
  "lint": true || false
}
```

### Result(example):

- Option 1:

```json
{
  "solved": true,
  "feedback": {
    "approvedMissing": "Code contains all key elements",
    "illegalFound": ""
  },
  "linter": null,
  "compiler": {
    "isError": false,
    "output": "\ncorrect\n"
  }
}
```

- Option 2(In case solution does not contain "white-listed" words):

```json
{
  "solved": false,
  "feedback": {
    "approvedMissing": "Your code is missing some key-elements, like: for, if",
    "illegalFound": ""
  },
  "linter": null,
  "compiler": null
}
```

- Option 3(In case the solution has all required-elements, but has a syntax error)

```json
{
  "solved": false,
  "feedback": {
    "approvedMissing": "Code contains all required elements",
    "illegalFound": ""
  },
  "linter": {
    "violations": [
      {
        "line": 3,
        "column": 20,
        "id": "; expected"
      }
    ],
    "exitCode": 2
  },
  "compiler": {
    "isError": false,
    "output": null
  }
}
```

## <a name="assignment"></a>Submit an assignment for checking:

### Request:

- Type: <b>POST</b>
- Route: /solution-orch/assignment/submit
- Headers: Auth headers required
- Body:

```json
{
  "course_id": "UID of course",
  "assignment_id": "UID of assignment",
  "user_id": "UUID of user",
  "challenges_data": {
    "challenge_id1":
      {
         "time_spent": 10000,
          "coding_time":  1000,
          "time_out_tab": 1000, 
           "error": "STRING", 
           "lang": "cs|python|js"
      },
      "challenge_id1":
      {
         "time_spent": 10000,
          "coding_time":  1000,
          "time_out_tab": 1000, 
           "error": "STRING", 
           "lang": "cs|python|js"
      }
  }
}
```

### Result(example):

```json
{
  "result": "Solution is being checked"
}
```

## <a name="test"></a>Test an app:

### Request:

- Type: <b>POST</b>
- Route: /solution-orch/app/test
- Headers: Auth headers required
- Body:

```json
{
  "appId": "ID of the app"
}
```

### Result(example):

```json
{
  "exitCode": 0, // the exitCode 0 = good, anything else = bad
  "logs": "returned logs from the container"
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
# an env folder should be created, that folder contains all the dependencies the service will need
# before running any python command you should make sure your terminal is using the virtual environment
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

```env
FREE_ORCH_URL="url to the coding orchestrator"
CHALLENGES_SERVICE_URL="URL to the challenges service"
AUTH_SERVICE_URL="url to the authentication service"
COURSES_SERVICE_URL="url to the courses service"
FS_COMPILER_SERVICE_URL="url to the full-stack compiler"
```
