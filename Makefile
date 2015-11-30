all :
	@echo "Run \`make workflow\` to create the Alfred workflow file after removing the old one if it exists."

clean :
	rm -f ./alfred-chrome-history.alfredworkflow

workflow : clean
	zip -r ./alfred-chrome-history.alfredworkflow . -x "*.git*" .gitignore "*env*" History requirements.txt

