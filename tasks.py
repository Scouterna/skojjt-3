# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import logging
import pickle
import codecs
import random
import google.auth
from google.cloud import ndb, tasks_v2
from flask import Blueprint, request
from progress import TaskProgress
from dbcontext import dbcontext
from memcache import memcache


tasks = Blueprint('tasks', __name__, template_folder='templates')



"""
def create_task(func, **kwargs):
    logging.info("starting create_task")
    tasks_client = tasks_v2.CloudTasksClient()

    http_method=tasks_v2.HttpMethod.POST
    _, PROJECT_ID = google.auth.default()
    REGION_ID = 'europe-west1'
    QUEUE_NAME = 'default'
    QUEUE_PATH = tasks_client.queue_path(PROJECT_ID, REGION_ID, QUEUE_NAME)
    # Initialize request argument(s)
    request = tasks_v2.CreateTaskRequest(
        parent=QUEUE_PATH,
    )

    client = tasks_v2.CloudTasksClient()

    logging.info("get queue for task")
    build = client.get_queue(request={'name': "default"})
    #for q in tasks_client.list_queues(parent=QUEUE_PATH):
    #    print(q.name)

    task_nonce = codecs.encode(random.randbytes(33), "base64").decode()
    expires = datetime.utcnow() + timedelta(hours=1)
    memcache.set('task:'+task_nonce, '', expires)

    task = {
        'app_engine_http_request': {
            'relative_uri': '/tasks/handler/',
            "http_method": tasks_v2.HttpMethod.POST,
            'body': {'_func_name': func.__name__,
                     'args': codecs.encode(pickle.dumps(kwargs), "base64").decode(),
                     'nonce': task_nonce,
            },
            'headers': {
                'Content-Type:': 'application/json',
            },
        }
    }
    logging.info("creating task")
    response = tasks_client.create_task(request=request, task=task)


@tasks.route('/handler/', methods=['POST'])
@dbcontext
def task_handler():
    logging.info("task handler")
    request_json = request.get_json()
    method_name = request_json.get('_func_name')
    task_nonce = request_json.get('nonce')
    if memcache.get('task:'+task_nonce) is None:
        return 'task cookie missing', 200 # return 200 to remove the task from the queue
    
    memcache.remove('task:'+task_nonce)
    
    kwargs = pickle.loads(codecs.decode(request_json.get('args').encode(), "base64"))
    possibles = globals().copy()
    possibles.update(locals())
    method = possibles.get(method_name)
    if not method:
        raise NotImplementedError("Method %s not implemented" % method_name)
    method(**kwargs)
    return "", 200
"""