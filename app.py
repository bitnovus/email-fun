import uuid
import os
import requests
import argon2
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


def constant_time_compare(val1, val2):
    if len(val1) != len(val2):
        return False
    result = 0

    # https://security.stackexchange.com/questions/83660/simple-string-comparisons-not-secure-against-timing-attacks
    for x, y in zip(val1, val2):
        result |= x ^ y
    return result == 0


def primitive_auth(input):
    salt = "some_salt_here"
    test_hash = argon2.argon2_hash(input, salt)
    stored_hash = b'\xb6$\x96\\|\xab\xbe*\x16\xa1\x01t\x1a\x87\n\x03ea16\xe7a\xaen\xf7\x9du\xa4F\x08\xb2\r\x87\x8c\x9a\xcf\\D\x86\x9c\x02\xf9\xd5\x9azM\xc7\xe0lWq@\xdb\xc0\xc9\xd8h\x03eKJ_\xa9\r$\xfa\x17[O\xe6\xc8bN4\xa3\xb0j}\xdb9\xc8\xda\x11+\x9fl\xcc\xf5\r\xfaj\x02He\x8e\x8a`o\xdc.\xcb\xb4\x1a\xbdky\x81\x08b\xd0\xfe\x96\x92<\x0e4\xdc>:\xf7\xb1\x1b\xcdby0sd'
    return constant_time_compare(stored_hash, test_hash)


@app.route("/fun", methods=['POST', 'GET'])
def fun():
    if request.method == 'POST' and primitive_auth(request.form['password']):
        print(request)
        email_id = submit_test_email()
        return f'id is <a href="/verify?test_id={email_id}">{email_id}</a>'
    else:
        return "no fun for you"


@app.route("/verify", methods=['GET'])
def verify():
    if 'test_id' in request.args:
        test_id = str(request.args['test_id'])
        result = verify_test_email(test_id)
        return f'test pass? {result}'
    else:
        return render_template('verify.html')
