"""
Copyright 2016 NaviSite, LLC
This module provides the REST API interface for Session Management.
URLs:
  GET /customers/?bus_id=<bus_id>   - Fetch all contacts associated with customer having ID: bus_id
  GET /customers/<int:contact_id>   - Fetch contact having ID: contact_id
Optional query args for GET methods:
  include               - comma separated list of column names to include in response
  exclude               - comma separated list of column names to exclude from response
  NOTE: include and exclude are mutually exclusive.
"""
# coding: utf-8
import base64
import logging

import flask
import flask_restful
import marshmallow

import demo_shared.helpers

import app_config

class ValidateLoginForm(marshmallow.Schema):
    """ Schema to define data that accompanies a POST request to: /session. """

    username = marshmallow.fields.Field(required=True,
                                        description="User Name being logged in")
    password = marshmallow.fields.Field(required=True,
                                        description="Password for login attempt")

# The following is for demo purposes only and should be replaced by an authentication verification
# Backed by database or similar
USER_ENTRIES = {
    'User1': {'username': 'User1', 'password': 'T3st1', 'id': 1, 'email': 'foo@test1.org'},
    'User2': {'username': 'User2', 'password': 'T3st2', 'id': 2, 'email': 'foo2@test2.org'},
    'User3': {'username': 'User3', 'password': 'T3st3', 'id': 3, 'email': 'foo3@test3.org'}}

#pylint: disable=no-self-use
#pylint: disable=unused-argument
class Session(flask_restful.Resource):
    """Session Management
    """
    #pylint: disable=unused-argument, no-self-use
    method_decorators = [demo_shared.helpers.requires_auth]

    def post(self):
        """POST - Authenticate credentials and start session
        :param self: Session object
        """

        helpers = demo_shared.helpers
        logging.info('ENTER endpoint')
        form_data = helpers.convert_keys_to_lowercase(obj=flask.request.form)
        schema = ValidateLoginForm()
        data, error = schema.load(data=form_data)
        if not error:
            username = data['username']
            password = data['password']
            user_info = None
            # The following needs to be converted to db backed function calls outside of initial demo
            if username not in USER_ENTRIES:
                error = 'Username: {} not a valid username'.format(username)
            elif password != USER_ENTRIES[username]['password']:
                error = 'Incorrect Password'
            else:
                error = ''
                user_info = {
                    'username': USER_ENTRIES[username]['username'],
                    'id': USER_ENTRIES[username]['id'],
                    'email': USER_ENTRIES[username]['email']}

            if user_info:
                # Use a random generator function to generate your tokens, this is just for demo use
                # ID is only added to allow trying out multiple sessions
                csrf_token = '{}RANDOM_TOKEN'.format(user_info['id'])
                api_token = '{}ANOTHER_RND_TOKEN'.format(user_info['id'])
                mc_client = app_config.MC.clone()
                mc_client.set('{}{}'.format(app_config.MC_PREFIX, csrf_token), {'token': api_token, 'user': username},
                              app_config.SESSION_TIMEOUT)
                resp = {'success': True, 'csrf_token': csrf_token, 'api_token': api_token, 'user_info': user_info}
            else:
                resp = {'success': False, 'reason': error}
        else:
            resp = {'success': False, 'reason': error}
        logging.info('Response: {}'.format(resp))
        response_object = helpers.make_response_object(
            body=helpers.dump_json(data=resp, pretty_print=app_config.PRETTY_PRINT_JSON))
        return response_object

    def delete(self):
        """GET - End session (logout)
        :param self: session object
        """

        helpers = demo_shared.helpers
        in_csrf_token = flask.request.headers.get('X-CSRF-Token')
        in_api_token = flask.request.headers.get('X-API-TOKEN')
        if in_csrf_token:
            mc_client = app_config.MC.clone()
            mc_client.delete('{}{}'.format(app_config.MC_PREFIX, in_csrf_token))
            logging.warn('Session deleted for csrf:{} api:{}'.format(in_csrf_token, in_api_token))
        else:
            logging.warn('Session not active')
