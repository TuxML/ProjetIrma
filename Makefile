DOCDIR=Documentation

doc:
	cd $(DOCDIR) && $(MAKE) doc

cleandoc:
	cd $(DOCDIR) && $(MAKE) clean
