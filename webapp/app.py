# -*- coding: utf-8 -*-

import os

from flask import Flask
from flask import request

from celery import Celery
from werkzeug.serving import WSGIRequestHandler

from controllers.GithubController import GithubController

# Construction
app = Flask(__name__)

# Routing
@app.route('/')
def hello():
    return 'Linkhub API'

'''
    Request info from github
'''
@app.route('/scrap_info_from_github/')
def scrapInfoFromGithub():
    try:
        githubController = GithubController()
        return githubController.scrapInfoFromGithub()

    except ValueError:
        return 'Failed to scrapInfoFromGithub'

'''
    Initilization
'''
if __name__ == '__main__':
    app.run(host='0.0.0.0')
