# coding: utf-8
import copy
import functools
import json
import logging

import flask

import app_config

CONTENT_TYPE_JSON = 'application/json; charset=utf-8'

def convert_keys_to_lowercase(obj):
    """Function to convert all keys in a dict to lowercase.

    :param obj: Initially a dictionary, called recursively with many types.
    :returns: Dictionary with all lower cased keys.
    """
    # Dictionaries and Dict like objects
    # NOTE: everything comes out as dictionaries
    if hasattr(obj, 'items'):
        out_dict = {}
        for key, value in obj.items():
            if isinstance(key, (tuple,)):
                new_key = tuple([x.lower() for x in key])
            else:
                new_key = key.lower()

            new_value = convert_keys_to_lowercase(value)
            out_dict[new_key] = new_value
        return out_dict

    # Strings (must be checked before list/tuple, as strings have __iter__)
    if isinstance(obj, (str, bytes, bytearray)):
        return obj

    # Lists, Tuples and -like objects
    # NOTE: tuples come out as tuples, everything else as a list.
    if hasattr(obj, '__iter__'):
        new_list = [convert_keys_to_lowercase(x) for x in obj]

        if isinstance(obj, (tuple,)):
            return tuple(new_list)
        else:
            return new_list

    # Everything else
    return obj

def dump_json(data, pretty_print=True):
    """Call json.dumps() with optional pretty_print arguments.

    :param data: Data to convert to JSON.
    :param pretty_print: True|False should we pretty print the JSON.
    :returns: JSON version of data.
    """
    args = dict(default=None)
    if pretty_print:
        args.update(sort_keys=True, indent=4, separators=(',', ': '))
    return json.dumps(data, **args)

######################################################################################
# HTTP Response related
######################################################################################
def make_response_object(body, headers=copy.copy({'Content-Type': CONTENT_TYPE_JSON}), response_code=200):
    """Format response according to accept header.
    Build a Response() object from body/response code. Set any headers appropriately.

    :param headers: Dictionary of HTTP headers to return.
    :param response_code: HTTP Status code to return.
    :param body: Response body, in it's proper format (CSV, PDF, JSON etc.)
    :returns: Flask Response Object
    """
    response = flask.Response(body)
    response.status_code = response_code
    for header, value in headers.items():
        response.headers.add(header, value)
    return response

def return_201_created_resource(resource_url):
    """Return an HTTP 201 for a newly created resource.

    :param resource_url: URL to newly created resource to include in Location header
    :returns: HTTP 201 response
    """
    headers = {'Content-Type': CONTENT_TYPE_JSON,
               'Location': resource_url,
              }

    body = {'code': 201,
            'message': 'Successfully created resource',
            'description': 'Successfully created resource',
           }

    return make_response_object(headers=headers,
                                response_code=body['code'],
                                body=dump_json(data=body, pretty_print=app_config.PRETTY_PRINT_JSON))

def return_4xx(code, message, description):
    """Return an HTTP 4xx error.

    :param code: HTTP error code.
    :param message: short text message to include.
    :param description: More complex information to include (can be structured data or text).
    :returns: HTTP 4xx response
    """
    headers = {'Content-Type': CONTENT_TYPE_JSON}
    body = {'code': code,
            'message': message,
            'description': description,
           }

    return make_response_object(headers=headers,
                                response_code=body['code'],
                                body=dump_json(data=body, pretty_print=app_config.PRETTY_PRINT_JSON))

def return_400_validation_errors(message, errors):
    """Return an HTTP 400 for validation errors.

    :param message: short text message to include.
    :param errors: Structured Python data to return about errors.
    :returns: HTTP 400 response
    """
    return return_4xx(code=400, message=message, description=errors)

def return_403_forbidden(message, description):
    """Return an HTTP 403 FORBIDDEN - trying to perform action not allowed against a resource.

    :param message: short text message to include.
    :param description: More complex information to include (can be structured data or text).
    :returns: HTTP 403 response
    """
    return return_4xx(code=403, message=message, description=description)

def return_404_not_found(message, description):
    """Return an HTTP 404 for resource not found.

    :param message: short text message to include.
    :param description: More complex information to include (can be structured data or text).
    :returns: HTTP 404 response
    """
    return return_4xx(code=404, message=message, description=description)

def return_500_internal_error(message, description):
    """Return an HTTP 500 for internal server errors.

    :param message: short text message to include.
    :param description: More complex information to include (can be structured data or text).
    :returns: HTTP 500 response
    """
    return return_4xx(code=500, message=message, description=description)

def requires_auth(func):
    """Decorator to require auth from a Resource.
    This can be used either at the class level - all methods would require it.
    Or it can be used at the method level to require it of a single method.
    At the class level create a class variable 'method_decorators' like so:
        method_decorators = [ helpers.requires_auth ]
    At the method level, use decorator syntax like so:
        @helpers.requires_auth
        def get(self, ...)

    :param func: function to be wrapped by decorator.
    :returns: internal 'decorated' function that does auth check.
    """
    def check_auth(username, password):
        """This function is called to check if a username / password combination is valid for an API client.
        :param username: the API client logging in.
        :param password: the password of the API client logging in.
        :returns: True | False if user/pass is correct
        """
        valid = app_config.API_USERS
        if username not in valid:
            return False

        return valid[username] == password

    @functools.wraps(func)
    def decorated(*args, **kwargs):
        """Internal function to check API client username/password from HTTP Basic Auth."""
        auth = flask.request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return make_response_object(headers={'WWW-Authenticate': 'Basic realm="Login Required"'},
                                        response_code=401,
                                        body='Invalid API login credentials\n')

        return func(*args, **kwargs)

    return decorated