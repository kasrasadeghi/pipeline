default:
	FLASK_ENV=development FLASK_APP=main.py flask run
	@# google-chrome-stable "/home/kasra/projects/notes-website/dist/index.html"


shell:
	FLASK_ENV=development FLASK_APP=main.py flask shell

