# consumerDB
This is a Flask application for the forms to collect customer data and insert it to the Mailchimp API.

## Software Requirement
To install the software requirements use the ```requirements.txt``` in the root folder.
```bash
$ pip install -r requirements.txt
```

It's important to add a new file on the root folder ```.env``` and the following variables:
```
API_KEY="<mailchimp-api>"
SERVER_PREFIX="<server prefix>"
SECRET_KEY="<secret-hash-db-flask-app>"
```

To generate a secure ```SECRET_KEY``` you can run the commmand:
``` bash
$ python -c 'import secrets; print(secrets.token_hex(32))'
```

