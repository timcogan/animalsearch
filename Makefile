PYTHON=pdm run python
PROJECT=PytorchWildlife
LINE_LEN=120
DOC_LEN=120
CODE_PATHS=$(PROJECT)/cli.py tests

init: pdm.lock
	which pdm || pip install --user pdm
	pdm venv create -n $(PROJECT)
	pdm sync -d

check:
	$(MAKE) style
	$(MAKE) quality
	$(MAKE) types
	$(MAKE) test

style:
	$(PYTHON) -m autoflake -r -i $(CODE_PATHS)
	$(PYTHON) -m isort $(CODE_PATHS)
	$(PYTHON) -m autopep8 -a -r -i $(CODE_PATHS)
	$(PYTHON) -m black $(CODE_PATHS)

quality:
	$(PYTHON) -m black --check $(CODE_PATHS)
	$(PYTHON) -m flake8 --max-doc-length $(DOC_LEN) --max-line-length $(LINE_LEN) $(CODE_PATHS)

node_modules:
	npm install

types: node_modules
	pdm run npx --no-install pyright tests $(CODE_PATHS)

pdm.lock:
	$(MAKE) update

update:
	pdm install -d

test:
	${PYTHON} -m pytest tests -s --cov=./${SRC}

clean:
	find $(CLEAN_DIRS) -path '*/__pycache__/*' -delete
	find $(CLEAN_DIRS) -type d -name '__pycache__' -empty -delete
	find $(CLEAN_DIRS) -name '*@neomake*' -type f -delete
	find $(CLEAN_DIRS) -name '*,cover' -type f -delete
	find $(CLEAN_DIRS) -name '*.orig' -type f -delete
	pdm venv remove -y $(PROJECT)
	rm -f .pdm-python

reset:
	$(MAKE) clean
	$(MAKE) init
	$(MAKE) check

pypi:
	$(PYTHON) -m build
	$(PYTHON) -m twine upload dist/*
	
circleci:
	circleci config validate 
	circleci local execute test