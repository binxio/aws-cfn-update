FROM python:3.9-alpine

ADD . /app/

RUN apk add --no-cache g++ make libffi-dev libffi && \
	cd /app/ && \
        pip install --upgrade pip build && \
        python -m build && \
        pip uninstall -y build && \
	pip install dist/*.whl && \
	apk del g++ make libffi-dev && \
	rm -rf /app/ /root/.cache/


ENTRYPOINT ["aws-cfn-update"]


