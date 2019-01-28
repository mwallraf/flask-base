# INSTALLATION

## DEFAULT LOCAL DEVELOPMENT INSTALLATION

The default development installation starts a development flask server + Redis server + SQLite database on the local server.
It is highly recommended that a production server runs its own seperate Redis instance and uses a Postgres database.

1. Download project from github and store in folder ```epiroc-toolbox```

	```
	git clone https://github.com/mwallraf/flask-base.git epiroc-toolbox
	```

2. Create a python virtual environment and load the required python modules

	```
	cd epiroc-toolbox
	python3.7 -m venv venv
	source venv/bin/activate
	pip install -r requirements.txt
	```

3. Initialize the database

	For development only:

	```
	bash dev_init.sh
	```

	For production, create Postgres DB + user

	```
	sudo -u postgres createuser epiroc-toolbox
	sudo -u postgres createdb epiroc-toolbox
	sudo -u postgres psql
	psql=# alter user epiroc-toolbox with encrypted password 'epiroc-toolbox';
	psql=# grant all privileges on database epiroc-toolbox to epiroc-toolbox ;
	```

4. Start the application

	```
	bash dev_start.sh
	```

5. Start the web interface.

	Open the web interface on ```http://localhost:5000/```

	Default username + password are ```flas-base-admin@example.com``` and ```password```



## CUSTOMIZING THE DEFAULT SETTINGS

The default settings are configured in the file ```config.py``` however they can be customized by overriding several environment variables.
To easiest way to do this is to create a new files ```config.env``` with the environment files that you want to override.

An example of these settings are:

	```
	MAIL_USERNAME=<mail user>
	MAIL_PASSWORD=<mail password>
	SECRET_KEY=SuperRandomStringToBeUsedForEncryption
	APP_NAME=Epiroc Toolbox
	MAIL_SERVER=<mail server>
	ADMIN_EMAIL=maarten@2nms.com
	ADMIN_PASSWORD=maarten
	FLASK_CONFIG=development
	```	


