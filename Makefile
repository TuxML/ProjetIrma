PROJECT=Projet Irma
AUTHOR=Projet Irma
# Variables below are already defined in conf.py
# See lines 24 to 28 of conf.py
# PYTHONPATH=./src
# export PYTHONPATH
SPHINXBUILD=/usr/bin/sphinx-build
SPHINXAPIDOC=sphinx-apidoc
CONFIGPATH=.
SOURCEDOC=sourcedoc
DOC=doc

.PHONY: clean doc archive author

clean:
	rm -f *~ */*~
	rm -rf __pycache__ src/__pycache__
	rm -rf $(DOC)
	rm -rf $(SOURCEDOC)
	rm -f $(PROJECT).zip

sourcedoc:
	$(SPHINXAPIDOC) -o $(SOURCEDOC) . --append-syspath
	$(SPHINXAPIDOC) -o $(SOURCEDOC) ./* --append-syspath
	printf ".. toctree::\n\t:glob:\n\n\t*" > $(SOURCEDOC)/index.rst

doc: author sourcedoc
	$(SPHINXBUILD) -c $(CONFIGPATH) -b html $(SOURCEDOC) $(DOC)

archive: clean
	zip -r $(PROJECT).zip images/* sourcedoc/* src/* _templates/* conf.py Makefile


author:
	sed -i -e 's/^project =.*/project = "$(PROJECT)"/g' conf.py
	sed -i -e 's/^copyright =.*/copyright = "2019, $(AUTHOR)"/g' conf.py
	sed -i -e 's/^author =.*/author = "$(AUTHOR)"/g' conf.py
