<center><img src="https://raw.githubusercontent.com/colav/colav.github.io/master/img/Logo.png"/></center>

# Quyca
ImpactU Backend written in Python with flask, it is used to provide the API for the Colav platform.


# Installation

## Dependencies
Docker and docker-compose is required.
* https://docs.docker.com/engine/install/ubuntu/ (or https://docs.docker.com/engine/install/debian/, etc)
* Install `docker-compose`:  
```bash
apt install docker-compose
```
or
```bash
pip install docker-compose
```

* https://docs.docker.com/engine/install/linux-postinstall/

* Deploy Elastic Search from Chia https://github.com/colav/Chia/tree/main/elasticsaerch


## Data 
Required data is stored in MongoDB, produced with kahi.
usually  database named kahi or kahi_dev, please read 



# Usage
edit the .env.example  renaming it to .env.dev or .env.prod and set the variables.

```bash
APP_NAME=quyca
APP_VERSION=0.0.1
APP_PORT=8010
APP_DOMAIN=localhost:8010
APP_DEBUG=True

APP_URL_PREFIX=/app
API_URL_PREFIX=/api

MONGO_SERVER=localhost
MONGO_USERNAME=
MONGO_PASSWORD=
MONGO_DATABASE=kahi_dev
MONGO_PORT=27017
MONGO_CALCULATIONS_DATABASE=kahi_calculations_dev

#ElasticSearch
ES_SERVER=http://localhost:9200
ES_USERNAME=
ES_PASSWORD=
ES_PERSON_COMPLETER_INDEX=kahi_dev_person
ES_INSTITUTION_COMPLETER_INDEX=kahi_dev_institution
ES_GROUP_COMPLETER_INDEX=kahi_dev_group
ES_DEPARTMENT_COMPLETER_INDEX=kahi_dev_department
ES_FACULTY_COMPLETER_INDEX=kahi_dev_faculty

SENTRY_DSN=
```

# Start the application
```bash
make up-dev  # to call "docker-compose up -d" for development
```
or
```bash
make up-prod  # to call "docker-compose up -d" for production
```

## Running tests
```bash
make tests-dev    # to run the tests
```
could be the same for prod with 
```bash
make tests-prod    # to run the tests
```

# List of endpoints
Run the next command to see the list of endpoints
```bash
docker compose  exec dev bash
```
luego dentro del contenedor
```bash
FLASK_APP='app' flask routes
```

# License
BSD-3-Clause License

# Links
http://colav.udea.edu.co/



