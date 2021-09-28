default:
	FLASK_ENV=development FLASK_APP=main.py flask run --port=5001

host:
	FLASK_APP=main.py flask run --host=0.0.0.0 --port=5000

shell:
	FLASK_ENV=development FLASK_APP=main.py flask shell

port:
	sudo netstat -nlp | grep 5000
	sudo netstat -nlp | grep 5001

killports:
	sudo fuser -k 5000/tcp
	sudo fuser -k 5001/tcp
