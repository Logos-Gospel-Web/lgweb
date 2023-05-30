.PHONY: all play install

all: venv/pyvenv.cfg

venv/pyvenv.cfg:
	python3 -m venv venv

play:
	ansible-playbook base.yml -i inventory.yml

install:
	pip install -U pip
	pip install -r requirements.txt
	ansible-galaxy collection install community.general
