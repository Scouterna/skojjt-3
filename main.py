import logging
import datetime
from flask import Flask, render_template, request, make_response, redirect
from google.auth.transport import requests
from google.cloud import ndb
import google.oauth2.id_token
from access import user_access, login_user_from_id_token, remove_user
from data import dbcontext, Semester, datastore_client
from memcache import memcache
from scoutnetuser import ScoutnetUser

logging.getLogger().setLevel(logging.INFO) # make sure info logs are displayed on the console

firebase_request_adapter = requests.Request()

app = Flask(__name__)


@app.route('/login/')
def login():
    logging.info("In login()")
    return render_template('login.html')

@app.route('/logout/')
def logout():
    logging.info("In logout()")
    session_id = request.cookies.get("session_id")
    if session_id and len(session_id) > 0:
        remove_user(session_id)
    response = make_response(render_template('signed_out.html'), 200)
    response.set_cookie('session_id', "")
    return response

@app.route('/session_login/', methods=["POST"])
def session_login():
    if 'idToken' not in request.form:
        logging.error("Login request is missing data")

    idToken = request.form['idToken']
    #csrfToken = request.form['csrfToken']
    #logging.info("idToken=" + idToken)
    #logging.info("csrfToken" + csrfToken)
    (_, session_id) = login_user_from_id_token(idToken)
    response = make_response(redirect('/'))
    response.set_cookie('session_id', session_id)
    return response


@app.route('/sign_in_success/')
def sign_in_sucess():
    logging.info("sign_in_success()")
    logging.info(f"request.cookies={str(request.cookies)}")
    return render_template('signed_in.html')


# login flow -> @user_access -> /login -> @user_access -> / 
@app.route('/')
@dbcontext
@user_access
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


##############################################################################

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.

    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.

    memcache.set("TestMemcacheKey", "TestMemcacheData")
    assert(memcache.get("TestMemcacheKey") == b"TestMemcacheData") # if this fails, check the redis server

    # main app:
    app.run(host='127.0.0.1', port=8080, debug=True)

##############################################################################