# set base image (host OS), to reduce the size use a package from alpine or python:3.8-slim
FROM python:3.8

# set the working directory in the container
WORKDIR /code

# copy the dependencies file to the working directory
COPY requirements.txt .

ENV http_proxy http://proxy01.wittag.local:9400
ENV https_proxy http://proxy01.wittag.local:9400

# install dependencies
RUN pip install -r requirements.txt

ENV http_proxy= 
ENV https_proxy=

# copy the content of the local src directory to the working directory
COPY src/ .

# command to run on container start
CMD [ "python", "./convertCynapseMqttDataToInfluxDbData.py" ]