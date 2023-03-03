public_certificate=cert/cert.pem
private_key=cert/key.pem
certs=--cert=${public_certificate} --key=${private_key}

withcerts:
	FLASK_ENV=development FLASK_APP=main.py flask run ${certs} --host=0.0.0.0 --port=5000

open:
	FLASK_ENV=development FLASK_APP=main.py flask run --host=0.0.0.0 --port=5000

dev:
	FLASK_ENV=development FLASK_APP=main.py flask run --port=5001

host:
	FLASK_APP=main.py flask run --host=0.0.0.0 --port=5000

shell:
	FLASK_ENV=development FLASK_APP=main.py flask shell

port:
	sudo netstat -nlp | grep 5000
	sudo netstat -nlp | grep 5001

killports:
	-sudo fuser -k 5000/tcp
	-sudo fuser -k 5001/tcp

cert:
	mkdir cert/
	openssl req -x509 -newkey rsa:4096 -nodes -out ${public_certificate} -keyout ${private_key} -days 365 -subj "/C=US/ST=Washington/L=Seattle/O=kazematics/OU=PipelineSecurity/CN=Pipeline"\
	   -addext "subjectAltName=IP:10.50.50.2"
