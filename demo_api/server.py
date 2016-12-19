# coding: utf-8
import logging
import logging.config

import flask
import flask_restful

import demo_shared.helpers

import app_config

import resources.items
import resources.session

# Create a "Flask-Restful" Application
APP = flask.Flask(__name__)
API = flask_restful.Api(app=APP)

# Read in configuration settings
APP.config.from_pyfile('app_config.py')

@APP.before_request
def before_request():
    """Before each request, connect to the database.
    """

#pylint: disable=unused-argument
@APP.teardown_request
def teardown_request(exception):
    """After teardown request handler. Logs clean shutdown and exception info.
    """

    if exception:
        logging.exception('after exception')
    else:
        logging.info('clean shutdown')

#pylint: disable=unused-argument
@APP.errorhandler(404)
def resource_not_found(error):
    """Do not let Flask handle generic 404 errors natively.
    It will return HTML even though the client accept header will specify JSON.
    :param error: The exception
    :returns: JSON 404 response
    """
    return hss_shared.helpers.return_404_not_found(
        message='Resource Not Found',
        description='The requested URL was not found on the server. \
If you entered the URL manually please check your spelling and try again.')

@APP.errorhandler(Exception)
def all_exception_handler(error):
    """For ANY uncaught exception log it.
    :param error: The exception
    :returns: Nothing
    :raises: Re-raises the exception
    """
    # Log the exception before letting Flask deal with it natively.
    logging.exception('Uncaught Exception')
    raise Exception

def build_logging():
    """Create the config dictionary and configure python logging for the running application.

    :returns: nothing
    """
    config_dict = {
        'version': 1,
        'handlers': {
            'console': {  # log to stderr using JSON formatter
                'class': 'logging.StreamHandler'
            }
        },
        'root': { # Default logger channel, level comes from project config, use console (stderr) handler
            'level': app_config.DEBUG_LEVEL,
            'handlers': ['console']
        }
    }

    logging.config.dictConfig(config_dict)

# Define resource Routing table
#  add_resource args are: Class, *urls, **kwargs
#    so (Foo, '/foo', '/foo/<int:foo_id>') maps
#       Class => Foo, *urls => [ /foo, /foo/<int:foo_id> ], **kwargs => {}
API.add_resource(resources.items.Items, '/api/items')
API.add_resource(resources.session.Session, '/api/session')
build_logging()
