#!/usr/bin/env python

# Source material for getting Amazon Alexa working with Python + Flask in Heroku
#   * https://developer.amazon.com/docs/alexa-skills-kit-sdk-for-python/host-web-service.html
#   * https://github.com/alexa/alexa-skills-kit-sdk-for-python/issues/53
#   * https://github.com/alexa/skill-sample-python-helloworld-classes/blob/master/lambda/py/hello_world.py
#   * https://github.com/alexa/skill-sample-python-fact/blob/master/lambda/py/lambda_function.py

import urllib
import json
import os

from flask import Flask
from flask import request
from flask import make_response

from ask_sdk_core.skill_builder import SkillBuilder
import ask_sdk_core.utils as ask_utils
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler

from ask_sdk_model import Response
from ask_sdk_model import RequestEnvelope

nr_of_queries = 0
last_query_google = ""
last_query_alexa = ""
last_query_alexa_tmp = ""

# Flask app should start in global layout
app = Flask(__name__)


# -----------------------------------------------------------
#                AMAZON ALEXA REQUEST HANDLERS
#------------------------------------------------------------


#
# Handler for launch requests
#
class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Welcome to TeMoto Commander."
        print(speak_output)

        return (handler_input.response_builder.speak(speak_output).ask(speak_output).response)


#
# Handler for MoveRobot intent
#
class MoveRobotIntentHandler(AbstractRequestHandler):
    """Handler for MoveRobot intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        
        return ask_utils.is_intent_name("TaMoveRobot")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        global last_query_alexa
        global last_query_alexa_tmp
        global nr_of_queries

        last_query_alexa = last_query_alexa_tmp
        nr_of_queries += 1    

        speak_output = "Ok."
        print(speak_output)

        return (handler_input.response_builder.speak(speak_output).ask(speak_output).response)


#
# Handler for fallback intent
#
class FallbackIntentHandler(AbstractRequestHandler):
    """Handler for Fallback Intent.
    AMAZON.FallbackIntent is only available in en-US locale.
    This handler will not be triggered except in that locale,
    so it is safe to deploy on any locale.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        print("In FallbackIntentHandler")

        handler_input.response_builder.speak(FALLBACK_MESSAGE).ask(
            FALLBACK_REPROMPT)
        return handler_input.response_builder.response


#
# Handler for ending the session
#
class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        print("In SessionEndedRequestHandler")

        return handler_input.response_builder.response


#
# Handler for problems
#
class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


#
# Create a skill builder and register the handles
#
print("Creating a skill builder ...")
skill_builder = SkillBuilder()
skill_builder.add_request_handler(LaunchRequestHandler())
skill_builder.add_request_handler(MoveRobotIntentHandler())
skill_builder.add_request_handler(FallbackIntentHandler())
skill_builder.add_request_handler(SessionEndedRequestHandler())
skill_builder.add_exception_handler(CatchAllExceptionHandler())

skill_obj = skill_builder.create()


#
# Define the routes for Flask
#
@app.route("/alexa-webhook", methods=['POST'])
def post():
    """
    Process the request as following :
    - Get the input request JSON
    - Deserialize it to Request Envelope
    - Verify the request was sent by Alexa
    - Invoke the skill
    - Return the serialized response
    """
    global last_query_alexa_tmp

    content = request.json
    request_envelope = skill_obj.serializer.deserialize(
        payload=json.dumps(content), obj_type=RequestEnvelope)

    print("Received a skill request:")
    req = request.get_json(silent=True, force=True)
    print(json.dumps(req, indent=4))
    last_query_alexa_tmp = json.dumps(req, indent=4)

    # For eg, check if Skill ID matches
    if (request_envelope.context.system.application.application_id != "amzn1.ask.skill.aa7904b4-f578-4eb8-9178-cfc49928ccc3"):
        print("Skill called with incorrect skill ID")
        return {}

    response_envelope = skill_obj.invoke(request_envelope=request_envelope, context=None)
    return json.dumps(skill_obj.serializer.serialize(response_envelope))


#
# Flask route that returns last alexa query JSON
#
@app.route('/alexa-queries')
def alexaQueries():
    global nr_of_queries
    global last_query_alexa
    return (last_query_alexa)


# -----------------------------------------------------------
#             GOOGLE ASSISTANT REQUEST HANDLERS
#------------------------------------------------------------


@app.route('/google-webhook', methods=['POST'])
def googleWebhook():
    global nr_of_queries
    global last_query_google

    nr_of_queries += 1

    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))
    last_query_google = json.dumps(req, indent=4)

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


@app.route('/google-queries')
def googleQueries():
    global nr_of_queries
    global last_query_google
    return (last_query_google)


#@app.route('/inc')
#def inc():
#    global nr_of_queries
#    return ("The number of received queries: " + str(nr_of_queries))


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print ("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')
