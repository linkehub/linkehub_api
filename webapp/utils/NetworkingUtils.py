# -*- coding: utf-8 -*-

'''
    NetworkingUtils is responsible for holding the external URLs and the default parameters 
    of each URL used by the API.
'''
class NetworkingUtils():

    def __init__(self):
        # Global attributes related to SIOPS
        self.SIOPS_BEAUTIFUL_SOUP_PARSER = 'html.parser'
        self.SIOPS_RESPONSE_DATA_DECODER = 'iso8859-15'