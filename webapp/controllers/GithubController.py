# -*- coding: utf-8 -*-

import time
import datetime
import http.client
import urllib
import json

from utils.NetworkingUtils import NetworkingUtils
from utils.StringUtils import StringUtils
from persistence.DBController import DBManager

'''
    Make requests to scrap data from Github
'''
class GithubController():

    def __init__(self):
        self.netUtils = NetworkingUtils()
        self.dbManager = DBManager()

    '''
        Returns true if the IP of this service has expired the number of requests per hour on the Github API
    '''
    def hasExpiredRequestsPerHourGithub(self):
        response = {
            "success" : False,
            "msg" : "Failed to make a request to the Github API to determine if the number of requests per hour has been exceeded",
            "has_expired_limit_requests_per_hour" : "",
            "usage" : ""
        }

        try:
            # Create a connection with the Github API
            connection = http.client.HTTPSConnection(self.netUtils.GITHUB_API_ROOT_URL)

            # Make a request to the Github API and verify if the limit of requests per hour has been exceeded
            print("Making request to the Github API to determine if limit of requests per hour has been exceeded  ...")

            connection.request("GET", "/rate_limit", headers={
                "cache-control": "no-cache",
                "User-Agent": "Linkehub-API",
                "Accept": "application/vnd.github.v3+json"
            })

            res = connection.getresponse()
            data = res.read()
            githubApiResponse = json.loads(data.decode(self.netUtils.UTF8_DECODER))

            if githubApiResponse is not None:
                    
                if "rate" in githubApiResponse:
                    usageRate = githubApiResponse["rate"]

                    response["success"] = True
                    response["msg"] = "We got a response from the Github API"
                    response["usage"] = usageRate

                    if "remaining" in usageRate:
                        response["has_expired_limit_requests_per_hour"] = usageRate["remaining"] is 0

        except Exception as err:
            print("Failed to verify if hasExpiredRequestsPerHourGithub {0}".format(err))

        return json.dumps(response)

    '''
       Returns a list of Github users from a given location.
    '''
    def getGithubUsersFromLocation(self, token, storeInDb, location, pageNumber):
        response = {
            "success" : False,
            "msg" : "Failed to get the list of Github users from the given location",
            "total_count" : -1,
            "stored_in_db" : False,
            "users" : []
        }

        try:

            if not token or not location or not pageNumber:
                response["msg"] = "{0}. {1}".format(response["msg"], "Invalid input parameters")
            else:
                # Create a connection with the Github API
                connection = http.client.HTTPSConnection(self.netUtils.GITHUB_API_ROOT_URL)

                # Make a request to get the list of users from a location
                print("Making request to the get the list of Github users from a location ...")

                headers = {
                    "cache-control": "no-cache",
	                "User-Agent": "Linkehub-API",
	                "Accept": "application/vnd.github.v3+json"
                }
                endpoint = "/search/users?q=location:{0}&page={1}".format(
                    urllib.parse.quote(location),
                    urllib.parse.quote(pageNumber)
                )
                
                connection.request("GET", endpoint, headers=headers)

                res = connection.getresponse()
                data = res.read()
                githubApiResponse = json.loads(data.decode(self.netUtils.UTF8_DECODER))

                if githubApiResponse is not None:

                    if "items" in githubApiResponse and "total_count" in githubApiResponse:
                        listUsers = githubApiResponse["items"]

                        response["total_count"] = githubApiResponse["total_count"]
                        response["success"] = True
                        response["msg"] = "We got a list of users from {0} ".format(location)
                        response["users"] = listUsers

                        # Store the list of users in the database
                        if storeInDb:
                            profileResponse = {}
                            profileResponse["success"] = False

                            for user in listUsers:
                                user["location"] = location

                                # Store the basic user profile into the database
                                if "login" in user:
                                    self.dbManager.storeBasicUserInfoFromGithub(token, user)

                            if profileResponse["success"]:
                                response["success"] = True
                                response["msg"] = "Stored user profile"
                                response["stored_in_db"] = True
                                response["users"] = listUsers

        except Exception as err:
            print("Failed to getGithubUsersFromLocation {0}".format(err))

        return json.dumps(response)

    '''
        Scrap the profile info of a Github user
    '''
    def scrapUserRepositoriesSkilsFromGithub(self, token, userId):
        response = {
            "success" : False,
            "msg" : "Failed to get profile info of the given Github user",
            "basic_github_user_info" : None,
            "github_user_repos" : None
        }

        try:

            if not token or not userId:
                response["msg"] = "Invalid userId"
            else:
                # Create a connection with the Github API
                connection = http.client.HTTPSConnection(self.netUtils.GITHUB_API_ROOT_URL)

                # GET the list of repositories of the user
                print("Requesting list of repositories ...")

                headers = {
                    "cache-control": "no-cache",
	                "User-Agent": "Linkehub-API",
	                "Accept": "application/vnd.github.v3+json"
                }
                endpoint = "/users/{0}/repos".format(
                    urllib.parse.quote(userId)
                )

                connection.request("GET", endpoint, headers=headers)

                res = connection.getresponse()
                data = res.read()
                userReposResponse = json.loads(data.decode(self.netUtils.UTF8_DECODER))

                if userReposResponse is not None:
                    userRepos = {}
                    userLanguages = {}
                    
                    if isinstance(userReposResponse, list):

                        for repo in userReposResponse:
                            cleanedRepo = {}
                            strUtils = StringUtils()

                            # Clean the repo
                            if "id" in repo:
                                cleanedRepo["id"] = strUtils.getCleanedJsonValue(repo["id"])

                            if "name" in repo:
                                cleanedRepo["name"] = strUtils.getCleanedJsonValue(repo["name"])

                            if "language" in repo:
                                cleanedRepo["language"] = strUtils.getCleanedJsonValue(repo["language"])

                            if "full_name" in repo:
                                cleanedRepo["full_name"] = strUtils.getCleanedJsonValue(repo["full_name"])

                            if "private" in repo:
                                cleanedRepo["private"] = strUtils.getCleanedJsonValue(repo["private"])

                            if "html_url" in repo:
                                cleanedRepo["html_url"] = strUtils.getCleanedJsonValue(repo["html_url"])

                            if "description" in repo:
                                cleanedRepo["description"] = strUtils.getCleanedJsonValue(repo["description"])

                            if "url" in repo:
                                cleanedRepo["url"] = strUtils.getCleanedJsonValue(repo["url"])

                            if "collaborators_url" in repo:
                                cleanedRepo["collaborators_url"] = strUtils.getCleanedJsonValue(repo["collaborators_url"])

                            if "languages_url" in repo:
                                cleanedRepo["languages_url"] = strUtils.getCleanedJsonValue(repo["languages_url"])

                            if "subscribers_url" in repo:
                                cleanedRepo["subscribers_url"] = strUtils.getCleanedJsonValue(repo["subscribers_url"])

                            if "commits_url" in repo:
                                cleanedRepo["commits_url"] = strUtils.getCleanedJsonValue(repo["commits_url"])

                            if "updated_at" in repo:
                                cleanedRepo["updated_at"] = strUtils.getCleanedJsonValue(repo["updated_at"])
                            
                            # Get only the main language of the repo and append it to the list of languages of the user
                            if "language" in cleanedRepo:

                                if cleanedRepo["language"] is not None:
                                    userLanguages[cleanedRepo["language"]] = True

                            userRepos[cleanedRepo["name"]] = cleanedRepo

                        # Fetch a success message
                        response["msg"] = response["msg"] + " We also got the list of repositories. "
                        response["success"] = True
                        response["github_user_repos"] = userRepos
                        response["user_languages"] = userLanguages

                    # Upsert the list of languages of the user
                    userLanguages = json.loads(json.dumps(userLanguages))
                    userRepos = json.loads(json.dumps(userRepos))

                    self.dbManager.storeGithubUserSkills(token, userId, userLanguages)

                    # Store the list of repositories of the user into the database
                    self.dbManager.storeReposGithubUser(token, userId, userRepos)

        except Exception as err:
            print("Failed to scrapBasicUserInfoFromGithub {0}".format(err))

        return json.dumps(response)

    '''
        Scrap the commits of a Github user made on a given language on a given repository
    '''
    def scrapUserCommitsRepoLanguageFromGithub(self, token, userId, repo, language):
        response = {
            "success" : False,
            "msg" : "Failed to get the commits and code samples of this Github user",
            "github_user_commits" : "",
            "code_samples" : []
        }

        try:

            if not userId or not repo or not language:
                response["msg"] = "Invalid userId"
            else:
                print("Requesting list of commits on a specific language in the given repository ...")

                # Create a connection with the Github API
                connection = http.client.HTTPSConnection(self.netUtils.GITHUB_API_ROOT_URL)

                # GET user commits x repo x language
                headers = {
                    "cache-control": "no-cache",
	                "User-Agent": "Linkehub-API",
	                "Accept": "application/vnd.github.v3+json"
                }
                endpoint = "/search/code?q=language:{0}+repo:{1}/{2}".format(
                    urllib.parse.quote(language),
                    urllib.parse.quote(userId),
                    urllib.parse.quote(repo)
                )

                connection.request("GET", endpoint, headers=headers)

                res = connection.getresponse()
                data = res.read()
                commitsPerLanguage = json.loads(data.decode(self.netUtils.UTF8_DECODER))

                # Fetch the results that are going to be stored in the database
                if commitsPerLanguage is not None:
                    
                    if "items" in commitsPerLanguage:
                        userCommits = {}
                        codeSamples = {}

                        for commit in commitsPerLanguage["items"]:

                            if "sha" in commit:
                                userCommits[commit["sha"]] = commit

                                # Clean the list of commits
                                if "repository" in commit:
                                    del commit["repository"]

                                # Create a link to the actual file in which the user commited
                                userCodeUrl = commit["html_url"]
                                userCodeUrl = userCodeUrl.replace("api.github.com", "github.com")
                                userCodeUrl = userCodeUrl.replace("blob", "raw")

                                codeSample = {
                                    "commit_sha" : commit["sha"],
                                    "language"   : language,
                                    "code_url"   : userCodeUrl
                                }
                                codeSamples[commit["sha"]] = codeSample

                                response["code_samples"].append(codeSample)

                        # Fetch a success message
                        response["msg"] = "We got a few commits made by the user in {0} ".format(language)
                        response["success"] = True
                        response["github_user_commits"] = userCommits

                        # Stores the user commits and code samples from Github on the database
                        self.dbManager.storeUserCommitsLanguageOnGithubRepo(token, userId, userCommits, codeSamples)

        except Exception as err:
            print("Failed to scrapUserCommitsRepoLanguageFromGithub {0}".format(err))

        return json.dumps(response)

    '''
        Scrap the commits of a Github user made using a given language
    '''
    def scrapUserCommitsLanguageFromGithub(self, token, userId, language):
        response = {
            "success" : False,
            "msg" : "Failed to get the commits and code samples of this Github user",
            "github_user_commits" : "",
            "code_samples" : []
        }

        try:

            if not userId or not language:
                response["msg"] = "Invalid input parameters"
            else:
                print("Requesting list of commits made using a specific language ...")

                # Create a connection with the Github API
                connection = http.client.HTTPSConnection(self.netUtils.GITHUB_API_ROOT_URL)

                # GET user commits x language
                headers = {
                    "cache-control": "no-cache",
	                "User-Agent": "Linkehub-API",
	                "Accept": "application/vnd.github.v3+json"
                }
                endpoint = "/search/code?q=language:{0}+user:{1}".format(
                    urllib.parse.quote(language),
                    urllib.parse.quote(userId)
                )

                connection.request("GET", endpoint, headers=headers)

                res = connection.getresponse()
                data = res.read()
                commitsPerLanguage = json.loads(data.decode(self.netUtils.UTF8_DECODER))

                # Fetch the results that are going to be stored in the database
                if commitsPerLanguage is not None:
                    
                    if "items" in commitsPerLanguage:
                        userCommits = {}
                        codeSamples = {}

                        for commit in commitsPerLanguage["items"]:

                            if "sha" in commit:
                                userCommits[commit["sha"]] = commit

                                # Clean the list of commits
                                if "repository" in commit:
                                    del commit["repository"]

                                # Create a link to the actual file in which the user commited
                                userCodeUrl = commit["html_url"]
                                userCodeUrl = userCodeUrl.replace("api.github.com", "github.com")
                                userCodeUrl = userCodeUrl.replace("blob", "raw")

                                codeSample = {
                                    "commit_sha" : commit["sha"],
                                    "language"   : language,
                                    "code_url"   : userCodeUrl
                                }
                                codeSamples[commit["sha"]] = codeSample

                                response["code_samples"].append(codeSample)

                        # Fetch a success message
                        response["msg"] = "We got a few commits made by the user in {0} ".format(language)
                        response["success"] = True
                        response["github_user_commits"] = userCommits

                        # Stores the user commits and code samples from Github on the database
                        self.dbManager.storeUserCommitsLanguageOnGithubRepo(token, userId, userCommits, codeSamples)

        except Exception as err:
            print("Failed to scrapUserCommitsRepoLanguageFromGithub {0}".format(err))

        return json.dumps(response)

    '''
        Get a list of ids of Github users from a location
    '''
    def getGithubUserIdsFromLocation(self, token, location):
        response = {
            "success" : False,
            "msg" : "Failed to get a list of github user ids",
            "github_user_ids" : ""
        }

        try:

            if not token or not location:
                response["msg"] = "Invalid input parameters"
            else:
                print("Requesting list of github user ids ...")

                # GET the list of ids from the project DB
                githubUserIds = self.dbManager.getListGithubUserIdsFromLocation(location)
                
                # Fetch a valid response to the user
                if githubUserIds is not None:
                    
                    # Fetch a success message
                    response["msg"] = "We got a list of github user ids from {0} ".format(location)
                    response["success"] = True
                    response["github_user_ids"] = githubUserIds

        except Exception as err:
            print("Failed to getGithubUserIdsFromLocation {0}".format(err))

        return json.dumps(response)
