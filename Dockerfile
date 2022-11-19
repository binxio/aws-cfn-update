FROM python:3.9-alpine

ADD . /app/

RUN apk add --no-cache g++ make libffi-dev libffi && \
	pip install --upgrade pip setuptools_rust && \
	cd /app/ && \
	python3 setup.py install && \
        pip uninstall -y setuptools_rust && \
	apk del g++ make libffi-dev


ENTRYPOINT ["aws-cfn-update"]


