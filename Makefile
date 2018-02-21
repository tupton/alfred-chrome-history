all :
	@echo "Run \`make workflow\` to create the Alfred workflow file after removing the old one if it exists."

distclean :
	rm -f ./alfred-chrome-history.alfredworkflow

clean :
	rm -f alfred.py
	rm -f docopt.py
	rm -rf venv
	find . -iname "*.pyc" -delete

venv : venv/bin/activate

venv/bin/activate : requirements.txt
	test -d venv || virtualenv venv
	. venv/bin/activate
	touch venv/bin/activate

install : venv
	. venv/bin/activate
	pip install -r requirements.txt

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

