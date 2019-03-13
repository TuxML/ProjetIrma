#!/bin/sh
jupyter nbconvert --to markdown --ExecutePreprocessor.timeout=None --execute TUXML-basic.ipynb
