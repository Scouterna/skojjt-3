import logging
import datetime
from flask import Flask, render_template, request
from google.auth.transport import requests
from google.cloud import ndb
import google.oauth2.id_token
from access import checkAccess, login_user_from_id_token
from data import dbcontext, Semester, datastore_client
from memcache import memcache
from scoutnetuser import ScoutnetUser

logging.getLogger().setLevel(logging.INFO) # make sure info logs are displayed on the console

firebase_request_adapter = requests.Request()

app = Flask(__name__)


@app.route('/login/')
def login():
    logging.info("In login()")
    return render_template(
        'login.html')

@app.route('/session_login/', methods=["POST"])
def session_login():
    if 'idToken' not in request.form or 'csrfToken' not in request.form:
        logging.error("Login request is missing data")

    idToken = request.form['idToken']
    csrfToken = request.form['csrfToken']
    logging.info("idToken=" + idToken)
    logging.info("csrfToken" + csrfToken)
    login_user_from_id_token(idToken)
    return "", 200


@app.route('/sign_in_success/')
def sign_in_sucess():
    logging.info("sign_in_success()")
    logging.info(f"request.cookies={str(request.cookies)}")
    return render_template(
        'signed_in.html')


# login flow -> @checkAccess -> /login -> @checkAccess -> / 
@app.route('/')
@dbcontext
@checkAccess
def start(user):
    logging.info("In start()")
    return render_template(
        'start.html',
        user=user,
        starturl='',
        personsurl='',
        badgesurl='',
        logouturl='')


@app.route('/semester_test')
@dbcontext
def semester_test():
    semester = Semester.getOrCreateCurrent()
    return semester.getname()


@app.route('/test_firebase_login')
def root():
    # Verify Firebase auth.
    id_token = request.cookies.get("token")
    error_message = None
    claims = None
    times = None
    user_data = None

    if id_token:
        try:
            # Verify the token against the Firebase Auth API. This example
            # verifies the token on each page load. For improved performance,
            # some applications may wish to cache results in an encrypted
            # session store (see for instance
            # http://flask.pocoo.org/docs/1.0/quickstart/#sessions).
            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, firebase_request_adapter)

            user_data = claims['firebase']['sign_in_attributes']
            # print(user_data)
            email = user_data['email']

            store_time(email, datetime.datetime.now())
            times = fetch_times(email, 10)

        except ValueError as exc:
            # This will be raised if the token is expired or any other
            # verification checks fail.
            error_message = str(exc)



##############################################################################

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.

    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.

    # TODO: test code move to test file
    memcache.set("Hello", "Skojjt")
    assert(memcache.get("Hello"), "Skojjt") # if this fails there is a problem with Redis

    testuser = ScoutnetUser("Test User", "abc@xyz.qwe", 1111, 2222, 3333, True)
    memcache.set_picked("testuser", testuser)
    x = memcache.get_unpickled("testuser")
    assert(x.getname() == testuser.getname())

    # main app:
    app.run(host='127.0.0.1', port=8080, debug=True)

##############################################################################