VENV=.venv

all :
	@echo "Run \`make workflow\` to create the Alfred workflow file after removing the old one if it exists."

distclean :
	rm -f ./alfred-chrome-history.alfredworkflow

clean :
	rm -f alfred.py
	rm -f docopt.py
	rm -rf ${VENV}
	find . -iname "*.pyc" -delete

venv : venv/bin/activate

venv/bin/activate : requirements.txt
	test -d ${VENV} || virtualenv ${VENV}
	. ${VENV}/bin/activate
	touch ${VENV}/bin/activate

install : venv
	. ${VENV}/bin/activate
	pip install -r requirements.txt --upgrade --force-reinstall

lib :
	cp `python sitepackages.py`/alfred.py alfred.py
	cp `python sitepackages.py`/docopt.py docopt.py

dev : install \
	lib

zip :
	zip -r ./alfred-chrome-history.alfredworkflow . -x "*.git*" "*venv*" .gitignore Makefile History requirements.txt README.md sitepackages.py screenshot.png

workflow : distclean \
	install \
	lib \
	zip

