# -*- coding: utf-8 -*-
import datetime
import urllib.parse
import json
import logging
from flask import Blueprint, render_template, request, make_response
from memcache import memcache


progress = Blueprint('progress_page', __name__, template_folder='templates')


class TaskProgressKey():
    def __init__(self, taskProgress):
        self.taskProgress = taskProgress

    def urlsafe(self):
        return self.taskProgress.urlsafe()

class TaskProgress():
    def __init__(self, name, return_url):
        self.created = datetime.datetime.now()
        self.name = name
        self.return_url = return_url
        self.messages = []
        self.key = self
        self.failed = False
        self.completed = None
        memcache.replace_pickled(self.urlsafe(), self)

    def urlsafe(self):
        return urllib.parse.quote(self.name + str(self.created))

    @staticmethod
    def getTaskProgress(url_safe):
        if isinstance(url_safe, TaskProgressKey):
            return url_safe.taskProgress
        if isinstance(url_safe, TaskProgress):
            return url_safe
        return memcache.get_unpickled(urllib.parse.quote(url_safe))

    def append(self, message):
        self.messages.append(message)
        memcache.replace_pickled(self.urlsafe(), self)

    def info(self, message):
        self.append(message)
        logging.info(message)

    def warning(self, message):
        self.append('Warning:' + message)
        logging.warning(message)

    def error(self, message):
        self.failed = True
        self.append('Error:' + message)
        logging.error(message)

    def done(self):
        self.completed = datetime.datetime.now()
        memcache.replace_pickled(self.urlsafe(), self)

    def isRunning(self):
        return self.completed is None

    def put(self):
        pass

    @staticmethod
    def cleanup():
        pass

    def toJson(self, cursor=None):
        start_index = 0
        if cursor is not None:
            start_index = int(cursor)
        
        messages = self.messages[start_index:]
        cursor = len(self.messages)

        return '{"datetime": "' + self.created.strftime("%Y%m%d%H%M")+ '",' + \
            '"name": "' + self.name + '",' + \
            '"return_url":"' + self.return_url + '",' + \
            '"messages":' + json.dumps(messages) + ',' + \
            '"failed":' + json.dumps(self.failed) + ',' + \
            '"running":' + json.dumps(self.isRunning()) + ',' + \
            '"cursor":"' + str(cursor) + '"}'



@progress.route('/<progress_url>')
@progress.route('/<progress_url>/')
@progress.route('/<progress_url>/<update>')
@progress.route('/<progress_url>/<update>/')
def importProgress(progress_url, update=None):
    taskProgress = TaskProgress.getTaskProgress(progress_url)

    if update is not None:
        if taskProgress is not None:
            urlsafeCursor = request.args["cursor"] if "cursor" in request.args else ''
            cursor = urlsafeCursor if urlsafeCursor else None # note: empty strings are "Falsy"
            s = taskProgress.toJson(cursor)
        else:
            s = '{"messages": ["Error: Hittar inte uppgiften"], "failed": "true", "running": "false"}'

        response = make_response(s)
        response.headers['Content-Type'] = 'application/json'
        return response

    if taskProgress is not None:
        breadcrumbs = [{'link':'/', 'text':'Hem'}, {'link':taskProgress.return_url, 'text':'Tillbaka'}]
        return render_template('progressreport.html', tabletitle=taskProgress.name, rowtitle='Result', breadcrumbs=breadcrumbs, return_url=taskProgress.return_url)
    else:
        breadcrumbs = [{'link':'/', 'text':'Hem'}, {'link':'', 'text':'Tillbaka'}]
        return render_template('progressreport.html', tabletitle='<raderad>', rowtitle='Result', breadcrumbs=breadcrumbs, return_url='')
