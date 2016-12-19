# coding: utf-8

import functools
import logging

import flask

import app_config

def requires_auth_session(func):
    """Decorator to require current authenticated session
    This can be used either at the class level - all methods would require it.
    Or it can be used at the method level to require it of a single method.
    At the class level create a class variable 'method_decorators' like so:
        method_decorators = [ authentication.requires_auth_session ]
    At the method level, use decorator syntax like so:
        @authentication.requires_auth_session
        def get(self, ...)

    :param func: function to be wrapped by decorator.
    :returns: internal 'decorated' function that does auth check.
    """

    @functools.wraps(func)
    def decorated(*args, **kwargs):
        """Internal function to verify active session and accurate csrf token"""

        logging.info('requires_auth_session entered')
        logging.info('headers:{}'.format(flask.request.headers))

        in_csrf_token = flask.request.headers.get('X-Csrf-Token')
        in_api_token = flask.request.headers.get('X-API-TOKEN')
        mc_client = app_config.MC.clone()
        if in_csrf_token:
            logging.error('in_csrf_token:{}'.format(in_csrf_token))
            token_obj = mc_client.get('{}{}'.format(app_config.MC_PREFIX, in_csrf_token))
            if token_obj:
                valid_api_token = token_obj.get('token')
                logging.info('valid_api_token:{}'.format(valid_api_token))
                logging.info('Expected:{} Received:{}'.format(valid_api_token, in_api_token))
                if valid_api_token == in_api_token:
                    flask.g.log_basics['user'] = token_obj.get('user')
                    return func(*args, **kwargs)
                else:
                    reason = 'Invalid api token. {};{}'.format(valid_api_token, in_api_token)
            else:
                reason = 'CSRF Token not valid or has expired'
        else:
            reason = 'Missing CSRF token request header.'

        message = 'Failed authentication: {}'.format(reason)
        logging.info(message)
        response_object = demo_shared.helpers.make_response_object(
            body=demo_shared.helpers.dump_json({'message': message}, pretty_print=True), response_code=401)
        return response_object
    return decorated

