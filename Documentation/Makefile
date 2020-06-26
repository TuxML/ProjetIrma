PROJECT=TuxML
AUTHOR=Projet Irma, DiverSE
# Variables below are already defined in conf.py
# See lines 24 to 28 of conf.py
# PYTHONPATH=./src
# export PYTHONPATH
SPHINXBUILD=/usr/bin/sphinx-build
SPHINXAPIDOC=sphinx-apidoc
CONFIGPATH=.
SOURCEDOC=sourcedoc
DOC=doc

.PHONY: clean doc author

clean:
	rm -f *~ */*~
	rm -rf __pycache__
	rm -rf $(DOC)
	rm -rf $(SOURCEDOC)

sourcedoc:
	$(SPHINXAPIDOC) -o $(SOURCEDOC) .. --append-syspath
	$(SPHINXAPIDOC) -o $(SOURCEDOC) ../* --append-syspath
	printf ".. toctree::\n\t:glob:\n\n\t*" > $(SOURCEDOC)/index.rst

doc: author sourcedoc
	$(SPHINXBUILD) -c $(CONFIGPATH) -b html $(SOURCEDOC) $(DOC)

author:
	sed -i -e 's/^project =.*/project = "$(PROJECT)"/g' conf.py
	sed -i -e 's/^copyright =.*/copyright = "2019, $(AUTHOR)"/g' conf.py
	sed -i -e 's/^author =.*/author = "$(AUTHOR)"/g' conf.py
