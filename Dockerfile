FROM alpine:3.8
MAINTAINER Julio Gomez <jgomez2@cisco.com>

EXPOSE 5000

# Install basic utilities
RUN apk add -U \
#	 remove python as its package is not available for linux/amd64 required in GKE deployments
#        python \
        py-pip \
        ca-certificates \
  && rm -rf /var/cache/apk/* \
  && pip install --no-cache-dir \
          setuptools \
          wheel

# This is failing for some odd pip upgrade error commenting out for now
#RUN pip install --upgrade pip

COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt

WORKDIR /app
ADD ./myhero_spark /app/myhero_spark

CMD [ "python", "./myhero_spark/myhero_spark.py" ]

