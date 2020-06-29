# Variables below are already defined in conf.py
# See lines 24 to 28 of conf.py
# PYTHONPATH=./src
# export PYTHONPATH
SPHINXBUILD=/usr/bin/sphinx-build
SPHINXAPIDOC=sphinx-apidoc
CONFIGPATH=.
SOURCEDOC=sourcedoc
DOC=doc

.PHONY: clean doc

clean:
	rm -f *~ */*~
	rm -rf __pycache__
	rm -rf $(DOC)
	rm -rf $(SOURCEDOC)

sourcedoc:
	$(SPHINXAPIDOC) -o $(SOURCEDOC) .. --append-syspath
	$(SPHINXAPIDOC) -o $(SOURCEDOC)/compilation ../compilation --append-syspath
	$(SPHINXAPIDOC) -o $(SOURCEDOC)/docker_management ../docker_management --append-syspath
	$(SPHINXAPIDOC) -o $(SOURCEDOC)/miscellaneous ../miscellaneous --append-syspath
	printf "=====\nTuxML\n=====\n.. toctree::\n\t:glob:\n\n\t*\n\t*/*" > $(SOURCEDOC)/index.rst		

doc: sourcedoc
	$(SPHINXBUILD) -c $(CONFIGPATH) -b html $(SOURCEDOC) $(DOC)
