# -*- coding: utf-8 -*-

import os

from flask import Flask
from flask import request

from celery import Celery
from werkzeug.serving import WSGIRequestHandler

from controllers.AuthController import AuthController
from controllers.GithubController import GithubController

# Construction
app = Flask(__name__)

# Routing
@app.route("/")
def hello():
    return "Linkehub API - know about the best jobs in your city that match your coding profile"

@app.route("/login", methods=["POST"])
def login():
    try:
        username = request.form["username"]
        password = request.form["password"]

        authController = AuthController()
        return authController.loginWithUsernamePassword(username, password)

    except ValueError:
        return 'Failed to loginWithUsernamePassword'

@app.route("/has_expired_requests_per_hour_github/")
def hasExpiredRequestsPerHourGithub():
    try:
        githubController = GithubController()
        return githubController.hasExpiredRequestsPerHourGithub()

    except ValueError:
        return 'Failed to verify if hasExpiredRequestsPerHourGithub'

@app.route("/get_github_users_from_location/")
def getGithubUsersFromLocation():
    try:
        token = request.headers.get("access_token")
        storeInDb = request.args.get("store_in_db")
        location = request.args.get("location")
        pageNumber = request.args.get("page_number")
        
        githubController = GithubController()
        return githubController.getGithubUsersFromLocation(token, storeInDb, location, pageNumber)

    except ValueError:
        return 'Failed to getGithubUsersFromLocation'

@app.route("/scrap_basic_user_info_from_github/")
def scrapBasicUserInfoFromGithub():
    try:
        token = request.headers.get("access_token")
        githubUserId = request.args.get("githubUserId")

        githubController = GithubController()
        return githubController.scrapBasicUserInfoFromGithub(token, githubUserId)

    except ValueError:
        return 'Failed to scrapBasicUserInfoFromGithub'

@app.route("/scrap_user_commits_repo_language_github/")
def scrapUserCommitsRepoLanguageFromGithub():
    try:
        token = request.headers.get("access_token")
        githubUserId = request.args.get("githubUserId")
        language = request.args.get("language")
        repo = request.args.get("repo")

        githubController = GithubController()
        return githubController.scrapUserCommitsRepoLanguageFromGithub(token, githubUserId, repo, language)

    except ValueError:
        return 'Failed to scrapUserCommitsRepoLanguageFromGithub'

'''
    Initilization
'''
if __name__ == '__main__':
    app.run(host='0.0.0.0')
