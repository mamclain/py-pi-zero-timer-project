"""
wrap flask into a class that is a bit easier to work with for our particular use case
"""

import json
from typing import Dict, Union, Callable, Any

import flask
from flask import request


def json_error(message: str = "") -> str:
    """ A function to return a basic ajax json error

    :return:
    """
    return json.dumps(
        {
            "Error": True,
            "Message": message
        }
    )


def json_ok(message: str = "") -> str:
    """ A function to return a basic ajax json ok

    :return:
    """
    return json.dumps(
        {
            "Error": False,
            "Message": message
        }
    )


def render_custom_template(
        layout_template: str,
        template_title: str,
        page_name: str,
        page_template: str,
        page_parameters: Dict,
        layout_parameters: Union[Dict, None] = None
) -> str:
    """ Render a custom flask template stack

    Notes: There are likely better ways this could have been implemented, but I like segmenting my
    monolithic/WSGI header templates from the body application  and I find this approach simplistic to follow.

    :param layout_parameters: the layout template parameters
    :param page_name: the name of the page
    :param layout_template: the layout template name
    :param template_title: the html title of the page shown
    :param page_template: the app page template name
    :param page_parameters: the app page template parameters
    :return:
    """

    if layout_parameters is None:
        layout_parameters = {}

    app_params = {
        "template_title": template_title,
        "page_name": page_name,
    }
    page_parameters.update(app_params)

    local_layout_parameters = {
        "template_title": template_title,
        "page_name": page_name,
        "page_html": flask.render_template(page_template, **page_parameters)
    }

    if layout_parameters is not None:
        local_layout_parameters.update(layout_parameters)

    return flask.render_template(
        layout_template,
        **local_layout_parameters
    )


def render_index() -> str:
    """ Return the Homepage, Nothing supper fancy here

    :return:
    """
    return render_custom_template(
        "standalone_template.pug",
        "Simplistic Web Timer",
        "A Simplistic Web Timer",
        "app_template.pug",
        {}
    )


# noinspection PyPep8Naming
def GET(func: Callable) -> Callable:
    """ decorators to add items to the handler_get via the @GET Syntax

    :param func: the ajax git function to call
    """

    func._dec_type = "GET"
    func._dec_name = func.__name__
    return func


# noinspection PyPep8Naming
def POST(func: Callable) -> Callable:
    """ decorators to add items to the handler_get via the @POST Syntax

    :param func: the ajax post function to call
    """

    func._dec_type = "POST"
    func._dec_name = func.__name__
    return func


class EasyFlask(object):
    """
    Wrap flask into a class that is a bit easier to work with for our particular use case
    """

    def __init__(self, app_name: str) -> None:
        self.app = flask.Flask(app_name)

        # Because I am a pug fan, bind pug to our template engine (no raw html for me!)
        self.app.jinja_env.add_extension('pypugjs.ext.jinja.PyPugJSExtension')

        # Allow changes to be propagated to the client
        self.app.jinja_env.auto_reload = True

        # Add some dictionaries to the app to manage ajax get/post request easier
        self.handler_post = self._class_decorator_finder(self.__class__, "POST")
        self.handler_get = self._class_decorator_finder(self.__class__, "GET")

        # the root index should call the index function
        self.app.add_url_rule('/', "index", render_index)

        # allow our plugin to support get/post ajax
        self.app.add_url_rule(
            '/ajax/',
            'basic_ajax',
            self.handle_request,
            methods=['GET', 'POST']
        )
        self.app.add_url_rule(
            '/ajax/<user_request>',
            'basic_ajax_request',
            self.handle_request,
            methods=['GET', 'POST']
        )
        self.app.add_url_rule(
            '/ajax/<user_request>/<value>',
            'complex_ajax_request',
            self.handle_request,
            methods=['GET', 'POST']
        )

    @staticmethod
    def _class_decorator_finder(cls: Any, decorator: str) -> Dict:
        """ used to find a post decorator

        :param cls: the input class
        :param decorator: the post decorator type
        :return: the post decorator list
        """
        post_decorator_list = {}
        if cls is not None:
            class_items = list(cls.__dict__.values())
            for maybeDecorated in list(cls.__dict__.values()):
                if hasattr(maybeDecorated, '_dec_type'):
                    # noinspection PyProtectedMember
                    if maybeDecorated._dec_type == decorator:
                        # noinspection PyProtectedMember
                        dec_name = maybeDecorated._dec_name
                        post_decorator_list[dec_name] = maybeDecorated
            for base in cls.__bases__:
                post_decorator_list.update(cls._class_decorator_finder(base, decorator))
        return post_decorator_list

    def handle_request(self, user_request: Union[str, None] = None, value: Union[str, None] = None) -> str:
        """ function to handle ajax request for get and post events via our decorators system


        :param user_request: user get request
        :param value: use get value
        :return: json result
        """
        if "GET" in request.method:
            if user_request in self.handler_get:
                return self.handler_get[user_request](self, user_request, value)
            else:
                return json_error()

        elif "POST" in request.method:
            # Allow Query String First
            posted_data = request.form
            # Otherwise attempt JSON Decode
            if not any(posted_data):
                posted_data = request.json
            event = posted_data.get("request")
            if event is None:
                return json_error()

            if event in self.handler_post:
                return self.handler_post[event](self, posted_data, user_request, value)
            else:
                return json_error()
        else:
            return json_error()
