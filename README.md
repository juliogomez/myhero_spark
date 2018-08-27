# MyHero Spark / WebEx Teams Bot

This is the a WebEx Teams Bot for a basic microservice demo application.
This provides an interactive chat service for a voting system where users can vote for their favorite movie superhero.

Details on deploying the entire demo to a Kubernetes cluster can be found at

* DevOps tutorial - [juliogomez/devops](https://github.com/juliogomez/devops)

The application was designed to provide a simple demo for Kubernetes. It is written as a simple Python Flask application and deployed as a docker container.

Other services are:

* Data - [juliogomez/myhero_data](https://github.com/juliogomez/myhero_data)
* App - [juliogomez/myhero_app](https://github.com/juliogomez/myhero_app)
* UI - [juliogomez/myhero_ui](https://github.com/juliogomez/myhero_ui)
* Ernst - [juliogomez/myhero_ernst](https://github.com/juliogomez/myhero_ernst)
  * Optional Service used along with an MQTT server when App is in "queue" mode
* WebEx Teams Bot - [juliogomez/myhero_spark](https://github.com/juliogomez/myhero_spark)
  * Optional Service that allows voting through IM/Chat with a Cisco WebEx Teams Bot


The docker containers are available at

* Data - [juliocisco/myhero_data](https://hub.docker.com/r/juliocisco/myhero-data/)
* App - [juliocisco/myhero_app](https://hub.docker.com/r/juliocisco/myhero-app)
* UI - [juliocisco/myhero_ui](https://hub.docker.com/r/juliocisco/myhero-ui)
* Ernst - [juliocisco/myhero_ernst](https://hub.docker.com/r/juliocisco/myhero-ernst)
  * Optional Service used along with an MQTT server when App is in "queue" mode
* WebEx Teams Bot - [juliocisco/myhero_spark](https://hub.docker.com/r/juliocisco/myhero-spark)
  * Optional Service that allows voting through IM/Chat with a Cisco WebEx Teams Bot

# WebEx Teams Developer Account Requirement

In order to use this service, you will need a Cisco WebEx Teams Account to use for the bot.  The bot is built for ease of use, meaning any message to the account used to create the Bot will be acted on and replied to.  This means you'll need to create a new WebEx Teams account for the demo.  

Creating an account is free and only requires a working email account (each WebEx Teams Account needs a unique email address).  Visit [www.webex.com/products/teams](https://www.webex.com/products/teams/index.html) to signup for an account.

Developer access to WebEx Teams is also free and information is available at [http://developer.webex.com](http://developer.webex.com).

In order to access the APIs of WebEx Teams, this bot needs the Developer Token for your account.  To find it:

* Go to [http://developer.webex.com](http://developer.webex.com) and login with the credentials for your account.
* In the upper right corner click on your picture and click `Copy` to copy your Access Token to your clipboard
* Make a note of this someplace for when you need it later in the setup
  * **If you save this in a file, such as in the `.env` you will use later, be sure not to commit this file.  Otherwise your credentials will be availabe to anyone who might look at your code later on GitHub.**

## Basic Application Details

Required

* flask
* ArgumentParser
* requests

# Environment Installation

    pip install -r requirements.txt

# Basic Usage

In order to run, the service needs several pieces of information to be provided:

* App Server Address
* App Server Authentication Key to Use
* WebEx Teams Bot Authentication Key to Require in API Calls
* WebEx Teams Bot URL
* WebEx Teams Account Details
  * WebEx Teams Account Email
  * WebEx Teams Account Token

These details can be provided in one of three ways.

* As a command line argument

	```
	python myhero_spark/myhero_spark.py \
	  --app "http://myhero-app.server.com" \
	  --appkey "APP AUTH KEY" \
	  --secret "BOT AUTH KEY" \
	  --boturl "http://myhero-spark.server.com" \
	  --botemail "myhero.demo@server.com" \
	  --token "HAAKJ1231KFSDFKJSDF1232132"
	```
  
* As environment variables

	```
	export myhero_app_server=http://myhero-app.server.com`
	export myhero_app_key=APP AUTH KEY`
	export myhero_spark_bot_email=myhero.demo@server.com`
	export spark_token=HAAKJ1231KFSDFKJSDF1232132`
	export myhero_spark_bot_url=http://myhero-spark.server.com`
	export myhero_spark_bot_secret="BOT AUTH KEY"`
	python myhero_spark/myhero_spark.py`
	```

* As raw input when the application is run

	```
	python myhero_app/myhero_app.py`
	What is the app server address? http://myhero-app.server.com`
	App Server Key: APP AUTH KEY`
	 .
	 .
	
	```

A command line argument overrides an environment variable, and raw input is only used if neither of the other two options provide needed details.

# Accessing

Upon startup, the service registers a webhook to send all new messages to the service address.


## Interacting with the WebEx Teams Bot
The WebEx Teams Bot is a very simple interface that is designed to make it intuitive to use.  Simply send any message to the WebEx Teams Bot Email Address to have the bot reply back with some instructions on how to access the features.

The bot is deisgned to look for commands to act on, and provide the basic help message for anything else.  The commands are:

* /options
  * return a list of the current available options to vote on
* /results
  * list the current status of voting results
* /vote {{ option }} 
  * Place a vote for the 'option'
* /help 
  * Provide a help message

## REST APIs

# /

The main service API is at the root of the applciation and is what is used for the WebEx Teams Webhooks.

# /hello/:email 

There is an API call that can be leveraged to have the WebEx Teams Bot initiate a chat session with a user.  This API responds to GET requests and then will send a WebEx Teams message to the email provided.  

Example usage

```
curl http://myhero-spark.domain.local/hello/user@email.com 
```

# /health 

This is an API call that can be used to test if the WebEx Teams Bot service is functioning properly.
  
```
curl -v http://myhero-spark.domain.local/health 

*   Trying...
* Connected to myhero-spark.domain.local (x.x.x.x)
> GET /health HTTP/1.1
> Host: myhero-spark.domain.local
> User-Agent: curl/7.43.0
> Accept: */*
> 
* HTTP 1.0, assume close after body
< HTTP/1.0 200 OK
< Connection: close
< 
* Closing connection 0
Service up. 
```


# Local Development with docker-compose

I've included the configuration files needed to do local development with docker-compose in the repo.  docker-compose will still use Docker for local development and requires the following be installed on your laptop: 

* [Docker](https://www.docker.com/community-edition)

Before running `docker-compose up` you will need to finish the .env file configuration by adding the WebEx Teams Account Email and Token to the environment variables used by the container.  To do this:

* Make a copy of .env.template to use
  * `cp .env.template .env`
* Edit `.env` and add your details where indicated
  * `vi .env`
  * Change the value for `MYHERO_SPARK_BOT_EMAIL` and `MYHERO_SPARK_BOT_TOKEN`

To start local development run:
* `docker-compose up`
* Now you can interact with the API or interface at localhost:15001 (configured in docker-compose.yml)
  - example:  from your local machine `curl -H "key: DevBot" http://localhost:15003/demoroom/members`
  - Environment Variables are configured in .env for development

Each of the services in the application (i.e. myhero_web, myhero_app, and myhero_data) include docker-compose support to allow working locally on all three simultaneously.


# Local Development with Vagrant

I've included the configuration files needed to do local development with Vagrant in the repo.  Vagrant will still use Docker for local development and requires the following be installed on your laptop: 

* [Vagrant 2.0.1 or higher](https://www.vagrantup.com/downloads.html)
* [Docker](https://www.docker.com/community-edition)

Before running `vagrant up` you will need to finish the Vagrant file configuration by adding the WebEx Teams Account Email and Token to the environment variables used by the container.  To do this:

* Make a copy of Vagrantfile.sample to use
  * `cp Vagrantfile.sample Vagrantfile`
* Edit `Vagrantfile` and add your details where indicated
  * `vim Vagrantfile`
  * Change the value for `myherospark_bot_email` and `spark_token` in the `docker.env` hash

To start local development run:
* `vagrant up`
* Now you can interact with the API or interface at localhost:15001 (configured in Vagrantfile)
  - example:  from your local machine `curl -H "key: DevBot" http://localhost:15003/demoroom/members`
  - Environment Variables are configured in Vagrantfile for development

Each of the services in the application (i.e. myhero_web, myhero_app, and myhero_data) include Vagrant support to allow working locally on all three simultaneously.
