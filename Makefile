all :
	@echo "Run \`make workflow\` to create the Alfred workflow file after removing the old one if it exists."

distclean :
	rm -f ./alfred-chrome-history.alfredworkflow

clean :
	rm -f alfred.py
	rm -f docopt.py

install :
	pip install -r requirements.txt

lib :
	cp `python sitepackages.py`/alfred.py alfred.py
	cp `python sitepackages.py`/docopt.py docopt.py

zip :
	zip -r ./alfred-chrome-history.alfredworkflow . -x "*.git*" "*env*" .gitignore Makefile History requirements.txt README.md sitepackages.py screenshot.png

workflow : distclean \
	install \
	lib \
	zip \
	clean

