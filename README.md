[![Python package](https://github.com/colav-playground/Kahi/actions/workflows/python-package.yml/badge.svg)](https://github.com/colav-playground/Kahi/actions/workflows/python-package.yml)
<center><img src="https://raw.githubusercontent.com/colav/colav.github.io/master/img/Logo.png"/></center>

# Quyca
This is the documentation for the Python project located in the `quyca` directory. The project pretend to follow the Domain Driven Design (DDD) architecture.


## Installation

To install the package, you can use the following command:
```shell
pip install quyca
```

But this package us deployed with docker, then you need to install docker and docker-compose to run the package.

To deploy you need to edit .env.example file and rename it to:
.env.local to test the code in your local machine.
.env.prod to deploy the code in a production environment.
.env.dev to deploy the code in a development environment.

### Format the code

Dependencies:
```shell
pip install black poetry autoflake
```

To format the code, you can use the following command:
```shell
python format.py
```


# Usage
Please read the Makefile to see the available commands to run the package.
https://github.com/colav/quyca/blob/develop/Makefile

To tests requests to the API, you can use the next urls:
- :8010/app/your/endpoint/here
- :8010/api/your/endpoint/here

where /app is the endpoint for the web application and /api is the endpoint for the expert API.
:8010 is the default port for the application but it can be changed in the .env file.


# Contributing
If you are interested in contributing to KAHI or creating your own plugins, please refer to the kahi-plugins repository. It contains the necessary resources and documentation to implement new plugins easily. Feel free to submit pull requests or report any issues you encounter.

# License
BSD-3-Clause License

# Links
http://colav.udea.edu.co/
