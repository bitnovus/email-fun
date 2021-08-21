import uuid
import os
import requests
from flask.templating import render_template
from flask import Flask, request
from flask_mail import Mail, Message


app = Flask(__name__, template_folder='templates')

app.config['MAIL_SERVER'] = 'smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['INBOX_ID'] = 1444368
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)


def set_all_env():
    for key in dict(os.environ):
        app.config[key] = os.environ.get(key)


def submit_test_email():
    test_id = uuid.uuid4()
    msg = Message(f'{test_id} - Hello from the other side!',
                  sender='peter@mailtrap.io', recipients=['paul@mailtrap.io'])
    msg.body = f"This is a test email. This email has test id: [{test_id}]"
    mail.send(msg)
    return test_id


def verify_test_email(search):
    headers = {'Api-Token': app.config['API_TOKEN']}
    params = {'search': search}
    inbox_id = app.config['INBOX_ID']
    api_url = f'https://mailtrap.io/api/v1/inboxes/{inbox_id}/messages'
    r = requests.get(api_url, headers=headers, params=params)
    req_reply = r.json()
    mailtrap_email_path = req_reply[0]['txt_path']
    html_api_url = f'https://mailtrap.io{mailtrap_email_path}'
    r2 = requests.get(html_api_url, headers=headers)
    return "This is a test email." in r2.text


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/fun", methods=['POST', 'GET'])
def fun():
    if request.method == 'POST':
        email_id = submit_test_email()
        return f'id is <a href="/verify?test_id={email_id}">{email_id}</a>'
    else:
        return "fun"


@app.route("/verify", methods=['GET'])
def verify():
    if 'test_id' in request.args:
        test_id = str(request.args['test_id'])
        result = verify_test_email(test_id)
        return f'test pass? {result}'
    else:
        return render_template('verify.html')
