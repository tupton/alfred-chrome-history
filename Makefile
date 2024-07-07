VENV=venv

all :
	@echo "Run \`make workflow\` to create the Alfred workflow file after removing the old one if it exists."

distclean :
	rm -f ./alfred-chrome-history.alfredworkflow

clean :
	rm -f docopt.py
	rm -rf ${VENV}
	find . -iname "*.pyc" -delete

venv : ${VENV}/bin/activate

venv/bin/activate : requirements.txt
	test -d ${VENV} || virtualenv ${VENV}
	. ${VENV}/bin/activate
	touch ${VENV}/bin/activate

install : venv
	. ${VENV}/bin/activate
	pip3 install -r requirements.txt --upgrade --force-reinstall

lib :
	cp `python3 sitepackages.py`/docopt.py docopt.py

dev : install \
	lib

zip :
	zip -r ./alfred-chrome-history.alfredworkflow . -x "*.git*" "*venv*" .gitignore Makefile History requirements.txt README.md sitepackages.py screenshot.png

workflow : distclean \
	install \
	lib \
	zip

