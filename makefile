default:
	FLASK_ENV=development FLASK_APP=main.py flask run --port=5001

host:
	FLASK_APP=main.py flask run --host=0.0.0.0 --port=5000

shell:
	FLASK_ENV=development FLASK_APP=main.py flask shell
