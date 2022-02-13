# First line is image of Docker
# Go to hub.docker.com to search image
# alpine: light-weight
FROM python:3.7-alpine  

# Next line is maintainer line, your name/company name
MAINTAINER Phong Hua

# ENV to set environment variable
# PYTHONUNBUFFERED was recommended. It does not allow python to buffer the output,
# and just print directly
ENV PYTHONUNBUFFERED 1

# Install our dependency
# We store our dependencies in requirement file
# We copy requirement list from ./requirements.txt to requirement.txt on docker image
COPY ./requirements.txt /requirements.txt

# Take requirements we just copy and install them into docker image
RUN pip install -r /requirements.txt

# Create empty folder /app on docker image
RUN mkdir /app
# Switch to /app as default directory, any application we run using docker container
# will start from this directory, unless we specify different
WORKDIR /app
# Copy from our local machine the app folder to the app folder,
# we created before. This will take the code from app folder on local machine
# to the app folder on docker image
COPY ./app /app

# Create a user name user, -D mean this user is only allow to run the application,
# no home directory etc.. is created for this user.
# If we dont do this, the docker image will be run using root account => NOT RECOMMENDED for SECURITY REASON
RUN adduser -D user
# Switch to that user
USER user


