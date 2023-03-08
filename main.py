import logging
from flask import Flask, render_template, request, make_response, redirect, url_for
from google.auth.transport import requests
from google.appengine.api import wrap_wsgi_app
import usersessions
from user_access import user_access
from dbcontext import dbcontext
from data import Semester
#from memcache import memcache
from google.appengine.api import memcache as my_memcache # TODO: investigate this

from scoutnetuser import ScoutnetUser

logging.getLogger().setLevel(logging.INFO) # make sure info logs are displayed on the console

my_memcache.set("test", "123")
assert(my_memcache.get("test") == "123") # on dev this must run through dev_appserver.py on linux/macos (not windows)

firebase_request_adapter = requests.Request()

# setting the static folder to root url, then all subfolders will be from / on the server.
app = Flask(__name__, static_url_path='')

# this is to get the app engine services back
app.wsgi_app = wrap_wsgi_app(app.wsgi_app, use_deferred=True)

# page routes:
#from groupsummary import groupsummary
#from persons import persons
#from scoutgroupinfo import scoutgroupinfo
#from start import start
from imports import import_page
from progress import progress
#from admin import admin
from tasks import tasks
#from terminsprogram import terminsprogram
#from stats import stats
#app.register_blueprint(start, url_prefix='/start')
#app.register_blueprint(persons, url_prefix='/persons')
#app.register_blueprint(scoutgroupinfo, url_prefix='/scoutgroupinfo')
#app.register_blueprint(groupsummary, url_prefix='/groupsummary')
app.register_blueprint(import_page, url_prefix='/import')
app.register_blueprint(progress, url_prefix='/progress')
#app.register_blueprint(admin, url_prefix='/admin')
app.register_blueprint(tasks, url_prefix='/tasks')
#app.register_blueprint(badges, url_prefix='/badges')
#app.register_blueprint(terminsprogram, url_prefix='/terminsprogram')
#app.register_blueprint(stats, url_prefix='/stats')


# user session handling
@app.route('/login/')
def login():
    logging.info("In login()")
    return render_template('login.html')

@app.route('/logout/')
def logout():
    logging.info("In logout()")
    session_id = request.cookies.get("session_id")
    if session_id and len(session_id) > 0:
        usersessions.remove_user_session(session_id)
    response = make_response(render_template('signed_out.html'), 200)
    response.set_cookie('session_id', "")
    return response

@app.route('/session_login/', methods=["POST"])
def session_login():
    if 'idToken' not in request.form:
        logging.error("Login request is missing data")

    idToken = request.form['idToken']
    (_, session_id) = usersessions.login_user_from_id_token(idToken)
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
def home(user: ScoutnetUser):
    logging.info("In home()")
    return render_template(
        'start.html',
        user=user,
        starturl='/start/',
        personsurl='',
        badgesurl='',
        logouturl=url_for("logout"))


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
    assert(memcache.get("TestMemcacheKey") == "TestMemcacheData") # if this fails, check the redis server

    # main app:
    app.run(host='127.0.0.1', port=8080, debug=True)

##############################################################################