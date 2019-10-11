"""
Simplistic Python Project to Provide a Web GUI Controlled Timer for a Pi Zero with a Rely HAT

Notes: Currently missing the Rely Hat Code as the PI zero is on order


"""

# import for annotation support
import json
import time
from threading import Timer, Lock
from typing import Dict, Union, Callable, Any

# import for the web
import flask
# create our flask app
from flask import request
from werkzeug.datastructures import ImmutableMultiDict


# add a Timer wrapper to allow time feedback
# could put this into a class on its own...
class FeedbackTimer(Timer):
    """
        Simplistic timer engine to allow remote feedback
    """

    def __init__(self, interval: Union[float, int], function: Callable, args: Any = None, kwargs: Any = None) -> None:
        """ Timer constructor

        :param interval: in seconds
        :param function: the callback function
        :param args: args
        :param kwargs: kwargs
        """
        #  call class constructor
        Timer.__init__(self, interval, function, args, kwargs)
        #  init the start time
        self.start_time = None

    def start(self) -> None:
        """ Start the timer

        :return:
        """
        # Set the time
        self.start_time = time.time()
        # kick off the time event
        super().start()

    def elapsed(self) -> Union[float, None]:
        """ get the time that has elapsed between the start time and the current time

        :return:
        """
        if self.is_alive():
            return time.time() - self.start_time
        else:
            return None

    def remaining(self) -> Union[float, None]:
        """ get the time that "should be" left on the Timer, this will be off by some cycles but its good for our needs

        :return:
        """
        if self.is_alive():
            # noinspection PyUnresolvedReferences
            return self.interval - self.elapsed()
        else:
            return None


def pi_after_timer_event() -> None:
    """ function that gets called after the timeout event occurs

    :return:
    """
    print("Job Done")


def pi_before_timer_event() -> None:
    """ function that gets called before the timer starts

    :return:
    """
    print("Start Job")


def pi_timer_event_abort() -> None:
    """ function that gets called when the timer event is aborted

    :return:
    """
    print("Abort Job")


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


app = flask.Flask("Simplistic Web Timer")

# Because I am a pug fan, bind pug to our template engine (no raw html for me!)
app.jinja_env.add_extension('pypugjs.ext.jinja.PyPugJSExtension')

# Allow changes to be propagated to the client
# app.jinja_env.auto_reload = True

# Add some dictionaries to the app to manage ajax get/post request easier
app.handler_post = {}
app.handler_get = {}

_app_lock = Lock()
_app_time = None


# noinspection PyPep8Naming
def GET(func: Callable) -> Callable:
    """ decorators to add items to the handler_get via the @GET Syntax

    :param func: the ajax git function to call
    """
    app.handler_get[func.__name__] = func

    return func


# noinspection PyPep8Naming
def POST(func: Callable) -> Callable:
    """ decorators to add items to the handler_get via the @POST Syntax

    :param func: the ajax post function to call
    """

    app.handler_post[func.__name__] = func

    return func


# Create a generic ajax handler
@app.route('/ajax/', methods=['GET', 'POST'])
@app.route('/ajax/<user_request>', methods=['GET', 'POST'])
@app.route('/ajax/<user_request>/<value>', methods=['GET', 'POST'])
def handle_request(user_request: Union[str, None] = None, value: Union[str, None] = None) -> str:
    """ function to handle ajax request for get and post events via our decorators system


    :param user_request: user get request
    :param value: use get value
    :return: json result
    """
    if "GET" in request.method:
        if user_request in app.handler_get:
            return app.handler_get[user_request](user_request, value)
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

        if event in app.handler_post:
            return app.handler_post[event](posted_data, user_request, value)
        else:
            return json_error()
    else:
        return json_error()


@app.route('/')
def index() -> str:
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


@POST
def ajax_get_status(
        posted_data: Union[ImmutableMultiDict, None],
        user_request: Union[str, None],
        value: Union[str, None]) -> str:
    """ get the time status

    :param posted_data: data sent via html post
    :param user_request: the url of the request if get
    :param value: the value of the request if get
    :return: JSON string
    """
    global _app_time
    time_state = False
    time_left = 0
    with _app_lock:
        if _app_time is not None:
            if _app_time.is_alive():
                time_state = True
                time_left = _app_time.remaining()
            else:
                _app_time = None

    return json.dumps(
        {
            "Error": False,
            "Message": "",
            "Status": time_state,
            "Left": time_left
        }
    )


@POST
def ajax_stop_event(
        posted_data: Union[ImmutableMultiDict, None],
        user_request: Union[str, None],
        value: Union[str, None]) -> str:
    """ stop the time event

    :param posted_data: data sent via html post
    :param user_request: the url of the request if get
    :param value: the value of the request if get
    :return: JSON string
    """
    global _app_time
    with _app_lock:
        if _app_time is not None:
            if _app_time.is_alive():
                _app_time.cancel()
                _app_time = None
                pi_timer_event_abort()
            else:
                _app_time = None

    return json_ok("Ok")


@POST
def ajax_start_event(
        posted_data: Union[ImmutableMultiDict, None],
        user_request: Union[str, None],
        value: Union[str, None]) -> str:
    """ start the time event

    :param posted_data: data sent via html post
    :param user_request: the url of the request if get
    :param value: the value of the request if get
    :return: JSON string
    """
    global _app_time

    hours = posted_data.get("hours", 0)
    minutes = posted_data.get("minutes", 0)
    seconds = posted_data.get("seconds", 0)

    if hours == "":
        hours = 0

    if minutes == "":
        minutes = 0

    if seconds == "":
        seconds = 0

    try:
        hours = float(hours)
        minutes = float(minutes)
        seconds = float(seconds)
    except ValueError:
        return json_error("Non numeric value of time provided...")

    run_time = 0
    run_time += hours * 60.0 * 60.0
    run_time += minutes * 60.0
    run_time += seconds

    if run_time <= 0:
        return json_error("Time provided below threshold...")

    with _app_lock:
        if _app_time is not None:
            if _app_time.is_alive():
                return json_error("Timer Already Running...")
            else:
                _app_time = None

        pi_before_timer_event()
        _app_time = FeedbackTimer(interval=run_time, function=pi_after_timer_event)
        _app_time.start()

    return json_ok("Ok")


if __name__ == '__main__':
    app.run(debug=True, port=5000)  # run app in debug mode on port 5000
