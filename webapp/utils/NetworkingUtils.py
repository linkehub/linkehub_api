# -*- coding: utf-8 -*-

'''
    NetworkingUtils is responsible for holding the external URLs and the default parameters 
    of each URL used by the API.
'''
class NetworkingUtils():

    def __init__(self):
        # Global attributes related to SIOPS
        self.JSON_PARSER = "json.parser"
        self.HTML_PARSER = "html.parser"
        self.UTF8_DECODER = "utf-8"
        self.ISO8859_15_DECODER = "iso8859-15"
        self.HTTPS_PREFIX = "https://"

        # Github
        self.GITHUB_API_ROOT_URL = "api.github.com"
        self.REGULAR_GITHUB_HEADER = {
            "cache-control": "no-cache",
            "User-Agent": "Linkehub-API",
            "Accept": "application/vnd.github.v3+json"
        }
        self.AUTH_GITHUB_HEADER = {
            "cache-control": "no-cache",
            "User-Agent": "Linkehub-API",
            "Accept": "application/vnd.github.v3+json"
        }