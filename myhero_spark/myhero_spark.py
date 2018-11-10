#! /usr/bin/python
'''
    Spark Bot for Simple Superhero Voting Application

    This Bot will use a provided Spark Account (identified by the Developer Token)
    and create a webhook to receive all messages sent to the account.   Users can
    check current standings, list the available options, and place a vote.

    This is the an example Service for a basic microservice demo application.
    The application was designed to provide a simple demo for Cisco Mantl

    There are several pieces of information needed to run this application.  It is
    suggested to set them as OS Environment Variables.  Here is an example on how to
    set them:

    # Address and key for app server
    export myhero_app_server=http://myhero-app.mantl.domain.com
    export myhero_app_key=DemoAppKey

    # Details on the Cisco Spark Account to Use
    export myhero_spark_bot_email=myhero.demo@domain.com
    export spark_token=adfiafdadfadfaij12321kaf

    # Address and key for the Spark Bot itself
    export myhero_spark_bot_url=http://myhero-spark.mantl.domain.com
    export myhero_spark_bot_secret=DemoBotKey
'''


__author__ = 'hapresto'


from flask import Flask, request, Response
import requests, json, re

app = Flask(__name__)

spark_host = "https://api.ciscospark.com/"
spark_headers = {}
spark_headers["Content-type"] = "application/json"
app_headers = {}
app_headers["Content-type"] = "application/json"

commands = {
    "/vote": "Place a vote for a superhero. Format: `/vote OPTION` ",
    "/options": "Return the possible options",
    "/results": "Return current results.",
    "/help": "Get help."
}

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization,Key')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,PUT,POST,DELETE,OPTIONS')
    return response


@app.route('/', methods=["POST"])
def process_webhook():
    post_data = request.get_json(force=True)
    # pprint(post_data)
    process_incoming_message(post_data)
    return ""

@app.route("/hello/<email>", methods=["GET"])
def message_email(email):
    '''
    Kickoff a 1 on 1 chat with a given email
    :param email:
    :return:
    '''
    send_message_to_email(email, "Hello, would you like to vote?")
    return "Message sent to " + email

@app.route("/health", methods=["GET"])
def health_check():
    return "Service up."

# Function to take action on incoming message
def process_incoming_message(post_data):
    # pprint(post_data)

    webhook_id = post_data["id"]
    room_id = post_data["data"]["roomId"]

    message_id = post_data["data"]["id"]
    message = get_message(message_id)
    # pprint(message)

    # First make sure not processing a message from the bot
    if message["personEmail"] == bot_email:
        return ""

    command = ""
    for c in commands.items():
        if message["text"].find(c[0]) == 0:
            command = c[0]
            sys.stderr.write("Found command: " + command + "\n")
            # debug_msg(post_data, "Found command: " + command)
            break

    # Take action based on command
    # If no command found, send help
    if command in ["","/help"]:
        reply = send_help(post_data)
    elif command in ["/options"]:
        reply = send_options(post_data)
    elif command in ["/vote"]:
        reply = process_vote(post_data)
    elif command in ["/results"]:
        reply = send_results(post_data)

    send_message_to_room(room_id, reply)

def send_results(post_data):
    results = get_results()
    message = "The current standings are: \n"
    for i, result in enumerate(results):
        if i == 0:
            message += "* **" +result[0] + "** is in the lead with " + str(round(result[2])) + "% of the votes!\n"
        else:
            message += "* " + result[0] + " has " + str(round(result[2])) + "% of the votes.\n"
    return message

def send_help(post_data):
    message = "Thanks for your interest in voting for your favorite SuperHero.  \n"
    message = message + "I understand the following commands:  \n"
    for c in commands.items():
        message = message + "* **%s**: %s \n" % (c[0], c[1])
    return message

def send_options(post_data):
    options = get_options()
    message = "The options are... \n"
    for option in options:
        message += "* %s \n" % (option)
    return message

def debug_msg(post_data, message):
    send_message_to_room(get_message(post_data["data"]["id"])["roomId"], message)

def process_vote(post_data):
    message_id = post_data["data"]["id"]
    message = get_message(message_id)

    # 1.  Get Possible Options
    options = get_options()
    chosen_hero = ""
    # 2.  See if the message contains one of the options
    for option in options:
        if message["text"].lower().find(option.lower()) > -1:
            sys.stderr.write("Found a vote for: " + option + "\n")
            chosen_hero = option
            break

    # 3.  Cast vote for option
    if chosen_hero != "":
        vote = place_vote(chosen_hero)
        # 4.  Thank the user for their vote
        reply = "Thanks for your vote for **%s**.  Every vote is important.  You can check current results by typing _/results_." % (chosen_hero)
    else:
        reply = "I didn't understand your vote, please type the name of your chosen hero **exactly** as listed on the ballot.  "
    return reply

# Utilities to interact with the MyHero-App Server
# ToDo - Update for v2 results
def get_results():
    u = app_server + "/v2/results"
    page = requests.get(u, headers = app_headers)
    tally = page.json()
    return tally

def get_options():
    u = app_server + "/options"
    page = requests.get(u, headers=app_headers)
    options = page.json()["options"]
    return options

def place_vote(vote):
    u = app_server + "/vote/" + vote
    page = requests.post(u, headers=app_headers)
    return page.json()

# Spark Utility Functions
#### Message Utilities
def send_message_to_email(email, message):
    spark_u = spark_host + "v1/messages"
    message_body = {
        "toPersonEmail" : email,
        "markdown" : message
    }
    page = requests.post(spark_u, headers = spark_headers, json=message_body)
    message = page.json()
    return message

def send_message_to_room(room_id, message):
    spark_u = spark_host + "v1/messages"
    message_body = {
        "roomId" : room_id,
        "markdown" : message
    }
    page = requests.post(spark_u, headers = spark_headers, json=message_body)
    message = page.json()
    return message

def get_message(message_id):
    spark_u = spark_host + "v1/messages/" + message_id
    page = requests.get(spark_u, headers = spark_headers)
    message = page.json()
    return message

#### Webhook Utilities
def current_webhooks():
    spark_u = spark_host + "v1/webhooks"
    page = requests.get(spark_u, headers = spark_headers)
    webhooks = page.json()
    return webhooks["items"]

def create_webhook(roomId, target, webhook_name = "New Webhook"):
    spark_u = spark_host + "v1/webhooks"
    spark_body = {
        "name" : webhook_name,
        "targetUrl" : target,
        "resource" : "messages",
        "event" : "created"
    }

    if (roomId != ""):
        {
            spark_body["filter"]: "roomId=" + roomId
        }

    page = requests.post(spark_u, headers = spark_headers, json=spark_body)
    webhook = page.json()
    return webhook

def update_webhook(webhook_id, target, name):
    spark_u = spark_host + "v1/webhooks/" + webhook_id
    spark_body = {
        "name" : name,
        "targetUrl" : target
    }
    page = requests.put(spark_u, headers = spark_headers, json=spark_body)
    webhook = page.json()
    return webhook

def delete_webhook(webhook_id):
    spark_u = spark_host + "v1/webhooks/" + webhook_id
    page = requests.delete(spark_u, headers = spark_headers)

def setup_webhook(room_id, target, name):
    webhooks = current_webhooks()
    webhook_id = ""
    # pprint(webhooks)

    # Legacy test for room based demo
    if (room_id != ""):
        # Look for a Web Hook for the Room
        for webhook in webhooks:
            if webhook["filter"] == "roomId=" + room_id:
                # print("Found Webhook")
                webhook_id = webhook["id"]
                break
    # For Global Webhook
    else:
        for webhook in webhooks:
            if webhook["name"] == name:
                # print("Found Webhook")
                webhook_id = webhook["id"]
                break

    # If Web Hook not found, create it
    if webhook_id == "":
        webhook = create_webhook(room_id, target, name)
        webhook_id = webhook["id"]
    # If found, update url
    else:
        webhook = update_webhook(webhook_id, target, name)

    # pprint(webhook)
    return webhook_id

#### Room Utilities
def current_rooms():
    spark_u = spark_host + "v1/rooms"
    page = requests.get(spark_u, headers = spark_headers)
    rooms = page.json()
    return rooms["items"]

def leave_room(room_id):
    # Get Membership ID for Room
    membership_id = get_membership_for_room(room_id)
    spark_u = spark_host + "v1/memberships/" + membership_id
    page = requests.delete(spark_u, headers = spark_headers)

def get_membership_for_room(room_id):
    spark_u = spark_host + "v1/memberships?roomId=%s" % (room_id)
    page = requests.get(spark_u, headers = spark_headers)
    memberships = page.json()["items"]

    return memberships

# Standard Utility
def valid_request_check(request):
    try:
        if request.headers["key"] == secret_key:
            return (True, "")
        else:
            error = {"Error": "Invalid Key Provided."}
            sys.stderr.write(error + "\n")
            status = 401
            resp = Response(json.dumps(error), content_type='application/json', status=status)
            return (False, resp)
    except KeyError:
        error = {"Error": "Method requires authorization key."}
        sys.stderr.write(str(error) + "\n")
        status = 400
        resp = Response(json.dumps(error), content_type='application/json', status=status)
        return (False, resp)

if __name__ == '__main__':
    from argparse import ArgumentParser
    import os, sys
    from pprint import pprint

    # Setup and parse command line arguments
    parser = ArgumentParser("MyHero Spark Interaction Bot")
    parser.add_argument(
        "-t", "--token", help="Spark User Bearer Token", required=False
    )
    parser.add_argument(
        "-a", "--app", help="Address of app server", required=False
    )
    parser.add_argument(
        "-k", "--appkey", help="App Server Authentication Key Used in API Calls", required=False
    )
    parser.add_argument(
        "-u", "--boturl", help="Local Host Address for this Bot", required=False
    )
    parser.add_argument(
        "-b", "--botemail", help="Email address of the Bot", required=False
    )
    parser.add_argument(
        "--demoemail", help="Email Address to Add to Demo Room", required=False
    )
    parser.add_argument(
        "-s", "--secret", help="Key Expected in API Calls", required=False
    )

    args = parser.parse_args()

    # Set application run-time variables
    # Values can come from
    #  1. Command Line
    #  2. OS Environment Variables
    #  3. Raw User Input
    bot_url = args.boturl
    if (bot_url == None):
        bot_url = os.getenv("myhero_spark_bot_url")
        if (bot_url == None):
            bot_url = raw_input("What is the Application Address for this Bot? ")
    # print "Bot URL: " + bot_url
    sys.stderr.write("Bot URL: " + bot_url + "\n")

    bot_email = args.botemail
    if (bot_email == None):
        bot_email = os.getenv("myhero_spark_bot_email")
        if (bot_email == None):
            bot_email = raw_input("What is the Email Address for this Bot? ")
    # print "Bot Email: " + bot_email
    sys.stderr.write("Bot Email: " + bot_email + "\n")

    app_server = args.app
    # print "Arg App: " + str(app_server)
    if (app_server == None):
        app_server = os.getenv("myhero_app_server")
        # print "Env App: " + str(app_server)
        if (app_server == None):
            get_app_server = raw_input("What is the app server address? ")
            # print "Input App: " + str(get_app_server)
            app_server = get_app_server
    # print "App Server: " + app_server
    sys.stderr.write("App Server: " + app_server + "\n")

    app_key = args.appkey
    # print "Arg App Key: " + str(app_key)
    if (app_key == None):
        app_key = os.getenv("myhero_app_key")
        # print "Env App Key: " + str(app_key)
        if (app_key == None):
            get_app_key = raw_input("What is the app server authentication key? ")
            # print "Input App Key: " + str(get_app_key)
            app_key = get_app_key
    # print "App Server Key: " + app_key
    sys.stderr.write("App Server Key: " + app_key + "\n")

    spark_token = args.token
    # print "Spark Token: " + str(spark_token)
    if (spark_token == None):
        spark_token = os.getenv("spark_token")
        # print "Env Spark Token: " + str(spark_token)
        if (spark_token == None):
            get_spark_token = raw_input("What is the Cisco Spark Token? ")
            # print "Input Spark Token: " + str(get_spark_token)
            spark_token = get_spark_token
    # print "Spark Token: " + spark_token
    # sys.stderr.write("Spark Token: " + spark_token + "\n")
    sys.stderr.write("Spark Token: REDACTED\n")

    secret_key = args.secret
    if (secret_key == None):
        secret_key = os.getenv("myhero_spark_bot_secret")
        if (secret_key == None):
            get_secret_key = raw_input("What is the Authorization Key to Require? ")
            secret_key = get_secret_key
    sys.stderr.write("Secret Key: " + secret_key + "\n")


    # Set Authorization Details for external requests
    spark_headers["Authorization"] = "Bearer " + spark_token
    app_headers["key"] = app_key

    # Create Web Hook to recieve ALL messages
    global_webhook_id = setup_webhook("", bot_url, "Global MyHero Demo Webhook")
    sys.stderr.write("Global MyHero Web Hook ID: " + global_webhook_id + "\n")

    app.run(debug=True, host='0.0.0.0', port=int("5000"))

