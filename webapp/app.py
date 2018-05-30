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
    return 'Linkehub API'

'''
    Request info from github
'''
@app.route('/scrap_user_info_from_github/')
def scrapUserInfoFromGithub():
    try:
        githubUserId = request.args.get('githubUserId')

        githubController = GithubController()
        return githubController.scrapUserInfoFromGithub(githubUserId)

    except ValueError:
        return 'Failed to scrapUserInfoFromGithub'

'''
    Initilization
'''
if __name__ == '__main__':
    app.run(host='0.0.0.0')
