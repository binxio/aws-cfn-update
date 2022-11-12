include Makefile.mk
NAME=aws-cfn-update


test:
	PYTHONPATH=tests pipenv run which pytest
