# SETTLE
> ## Backend for Settle, an expense management app. Built with FastAPI, SQLModel & PostgreSQL. Deployed on AWS EC2 using ECR.

### [WEBSITE](https://settle-frontend-ochre.vercel.app/)

This project is a Dockerised FastAPI backend built for an expense management app designed to solve problems that I faced while keeping track of and splitting expenses with people.

## PREQUISITES
- Python
- FastAPI
- PostgreSQL
- Pytest
- Docker

## Installation

Create a virtual environment:

```sh
python3 -m venv venv 
```

Install dependencies:

```sh
pip install -r requirements.txt
```

Configuration
--------------

Replace `.env.template` with real `.env`, changing placeholders

```
JWT_SECRET_KEY = "abcdefg"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30
JWT_ALGORITHM = HS256

POSTGRES_USER=username
POSTGRES_PASSWORD=password
POSTGRES_DB=db_name
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

Run with Docker
--------------
You must have ``docker`` and ``docker-compose`` installed on your machine to start this application.

Setup PostgreSQL database with docker-compose:

```sh
docker-compose up -d --build
```

OR

Manually create a database 

```sh
MAKE DATABASE YOUR_DATABASE_NAME
```

Run the migrations:

```sh
alembic upgrade head
```

Run the application server:

```sh
export APP_ENV=dev && fastapi dev
```

Also, you can run the fully Dockerized application with `docker-compose`:

```sh
make docker_build
```

And after that run migrations:

```sh
docker exec -it settle-web alembic upgrade head
```

Run tests

```
export APP_ENV=test && pytest
```

## CI/CD

This app has two actions:
- Testing: Spins up the docker container test db and runs the tests inside it.
- Deployment: 
  - Spins up the docker container
  - Publishes it to ECR
  - SSHs into the EC2 instance using the Github Actions runner
  - Fetches the docker image from ECR
  - Stops the running web container and re-runs it using the latest image.


## TODOS
- Password recovery/rest system
- Refresh + access token session management
- Standardized error handling
- Standardized access management
- Bloom filter for username validation (Redis/in-app)
- Personal registor
- Family register
- SQL optimisation