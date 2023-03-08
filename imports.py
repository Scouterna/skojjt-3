# -*- coding: utf-8 -*-
import time
import json
import logging
from threading import Thread
from flask import Blueprint, render_template, request, redirect
from data import Semester
from dataimport import RunScoutnetImport
from progress import TaskProgress
from scoutnetuser import ScoutnetUser
from dbcontext import dbcontext, datastore_client
from user_access import user_access
import usersessions
import traceback


import_page = Blueprint('import_page', __name__, template_folder='templates')

@import_page.route('/', methods = ['POST', 'GET'])
@dbcontext
@user_access
def import_(user: ScoutnetUser):
    
    breadcrumbs = [{'link':'/', 'text':'Hem'},
                   {'link':'/import', 'text':'Import'}]

    groupid = ""
    apikey = ""
    # TODO: fix pre filled fields
    #if user.groupaccess is not None:
    #    scoutgroup = user.groupaccess.get()
    #    apikey = scoutgroup.apikey_all_members
    #    groupid = scoutgroup.scoutnetID

    if request.method == 'POST':
        apikey = request.form.get('apikey').strip()
        groupid = request.form.get('groupid').strip()
        semester_key = Semester.getOrCreateCurrent().key
        return startAsyncImport(apikey, groupid, semester_key, user, request)

    return render_template('updatefromscoutnetform.html',
                            heading="Import",
                            breadcrumbs=breadcrumbs,
                            user=user,
                            groupid=groupid,
                            apikey=apikey)


def startAsyncImport(api_key: str, groupid: str, semester_key: str, user: ScoutnetUser, request):
    """
    :type api_key: str
    :type groupid: str
    :type semester_key: google.appengine.ext.ndb.Key
    :type user: data.UserPrefs
    :type request: werkzeug.local.LocalProxy
    :rtype werkzeug.wrappers.response.Response
    """
    taskProgress = TaskProgress(name='Import', return_url=request.url)

    # TODO: Cloud Tasks is the replacement for App Engine Taskqueues
    # https://cloud.google.com/tasks/docs/migrating , https://www.youtube.com/watch?v=JbTJFUmc5_A&t=73s&ab_channel=GoogleCloudTech

    t = Thread(target=importTask, args=[api_key, groupid, semester_key, taskProgress.key, user.key])
    t.run()
    #create_task(func=importTask, api_key=api_key, groupid=groupid, semester_key=semester_key, taskProgress_key=taskProgress.key, user_key=user.key)
    return redirect('/progress/' + taskProgress.key.urlsafe())


def importTask(api_key: str, groupid: str, semester_key, taskProgress_key, user_key):
    logging.info("importTask thread running")
    start_time = time.time()
    semester = semester_key.get()  # type: Semester
    user = usersessions.get_user_by_uid(user_key)
    progress = TaskProgress.getTaskProgress(taskProgress_key)
    try:
        success = RunScoutnetImport(groupid, api_key, user, semester, progress)
        if not success:
            progress.info("Importen misslyckades")
            progress.failed = True
        else:
            progress.info("Import klar")
            if user.groupaccess is not None:
                progress.info('<a href="/start/%s/">Gå till scoutkåren</a>' % (user.groupaccess.urlsafe()))
    except Exception as e: # catch all exceptions so that defer stops running it again (automatic retry)
        progress.error("Importfel: " + str(e) + "CS:" + traceback.format_exc())

    end_time = time.time()
    time_taken = end_time - start_time
    progress.info("Tid: %s s" % str(time_taken))

    progress.done()
