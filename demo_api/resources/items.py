# coding: utf-8
import logging

import flask_restful

import demo_shared.helpers

import app_config

#pylint: disable=no-self-use
#pylint: disable=unused-argument
class Items(flask_restful.Resource):
    """Retrieve a list of quote records (GET)."""
    #pylint: disable=unused-argument, no-self-use
    def get(self):
        """GET test
        :returns: test message
        """
        #pylint: disable=line-too-long
        #This is a test resource using static data so line length limitation isn't necessary here
        item_data = [{"item_number": "Item 1", "status": "Foobar", "description": "This is an example description of item 1.","related_id": 1001, "sample_date": "2016-12-13", "sample_phone": "(555) 432-1212"}, {"item_number": "Item 2", "status": "OK", "description": "This is an example description of item 2.","related_id": 1002, "sample_date": "2015-01-13", "sample_phone": "(555) 222-3232"}, {"item_number": "Item 3", "status": "Unknown", "description": "This is an example description of item 3.","related_id": 1003, "sample_date": "2001-01-01", "sample_phone": "(555) 611-4141"}]
        helpers = hss_shared.helpers
        helpers.log(func=logging.warning, content_dict=dict(message='ENTER endpoint'))
        response = helpers.make_response_object(body=helpers.dump_json(data={'items': item_data},
                                                                       pretty_print=app_config.PRETTY_PRINT_JSON))
        return response
