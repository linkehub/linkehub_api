# -*- coding: utf-8 -*-

import time
import datetime
import http.client
import urllib
import json

from bs4 import BeautifulSoup

from utils.NetworkingUtils import NetworkingUtils

'''
    Make requests to scrap data from github
'''
class GithubController():

    def __init__(self):
        self.netUtils = NetworkingUtils()

    def scrapInfoFromGithub(self):
        '''
        urls = [
            "fiocruz-app-oeds-api-dev.herokuapp.com"
        ]

        try:
            i = 1
            while i == 1:

                for url in urls:
                    # Make a request to get the HTML which contains the list of Cities of SIOPS
                    headers = {
                        'cache-control': "no-cache"
                    }
                    conn = http.client.HTTPConnection(url)
                    conn.request('GET', "", headers = headers)

                    # Process the response
                    res = conn.getresponse()
                    data = res.read()
                    text = data.decode(self.netUtils.SIOPS_RESPONSE_DATA_DECODER)

                    print("{0} - response: {1}".format(datetime.datetime.utcnow(),text))

                print("\n")

                time.sleep(60)

        except urllib.error.HTTPError:
            print("Failed to pingService")

        except urllib.error.URLError:
            print("Failed to pingService")

        finally:

            return ""
        '''

        try:
            # Make a request to get the HTML which contains the list of Cities of SIOPS
            url = ""
                    
            headers = {
                'cache-control': "no-cache"
            }
            conn = http.client.HTTPConnection(url)
            conn.request('GET', "", headers = headers)

            # Process the response
            res = conn.getresponse()
            data = res.read()
            text = data.decode(self.netUtils.SIOPS_RESPONSE_DATA_DECODER)

            print("{0} - response: {1}".format(datetime.datetime.utcnow(),text))

        except urllib.error.HTTPError:
            print("Failed to pingService")

        except urllib.error.URLError:
            print("Failed to pingService")

        finally:

            return "Done scraping info"
