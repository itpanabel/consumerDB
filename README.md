# consumerDB
This is a Flask application for the forms to collect customer data and insert it to the Mailchimp API.

## Software Requirement
To install the software requirements use the ```requirements.txt``` in the root folder.
```bash
pip install -r requirements.txt
```

It's important to add a new file on the root folder ```.env``` and the following variables:
```
API_KEY="<mailchimp-api>"
SERVER_PREFIX="<server prefix>"
SECRET_KEY="<secret-hash-db-flask-app>"
SENDGRID_API_KEY="<sendgrid-api-key>"
```

To generate a secure ```SECRET_KEY``` you can run the commmand:
``` bash
python -c 'import secrets; print(secrets.token_hex(32))'
```

## Database Setup

Initialize the SQLite database (required on first run):
```bash
flask --app api init-db
```

## Running in Development Mode

```bash
flask --app api run --debug
```

The app will be available at `http://127.0.0.1:5000`.

## Sending Tester Reports

A standalone script emails monthly tester reports via SendGrid. Run it manually or schedule it as a cron job:
```bash
python send_testers.py /path/to/consumerDB
```

It sends Panama's report on day 8 of the month, and Colombia's on the last day of the month.
