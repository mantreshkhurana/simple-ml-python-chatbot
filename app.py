from datetime import datetime
from urllib.request import urlopen
from flask import Flask, request, render_template, jsonify
import json
from joblib import load
from youtube_search import YoutubeSearch
import re
import requests
import wikipedia
import webbrowser
from bs4 import BeautifulSoup
import os
import argparse

# From local files
import train
import modules.toxicity as toxicity

parser = argparse.ArgumentParser()

parser.add_argument(
    "-p",
    "--port",
    type=int,
    default=5000,
    help="specify the port number, default is 5000.",
)

parser.add_argument(
    "-s",
    "--server",
    type=int,
    default=1,
    help="server mode, default is True.",
)

args = parser.parse_args()

port = args.port
server = args.server

if os.path.exists("chat.joblib"):
    pass
else:
    url = "http://mantreshkhurana.com/projects/simple-ml-python-chatbot/chat.json"
    download_responses_data = train.download_responses(url)

    with open("chat.json", "w") as file:
        json.dump(download_responses_data, file, indent=4)

    responses_data = train.load_responses("chat.json")
    model = train.train_model(responses_data)
    train.save_model(model)

app = Flask(__name__)


def load_responses(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)
    return data


def load_model(model_file="chat.joblib"):
    return load(model_file)


def get_response(question, model):
    question = question.lower()

    if "time" in question or "current time" in question:
        current_time = datetime.now().strftime("%I:%M %p")
        return f"The current time is {current_time}"

    elif "date" in question or "today's date" in question:
        current_date = datetime.now().strftime("%m/%d/%Y")
        return f"Today's date is {current_date}"

    elif "day" in question or "today's day" in question:
        current_day = datetime.now().strftime("%A")
        return f"Today's day is {current_day}"

    elif "month" in question or "current month" in question:
        current_month = datetime.now().strftime("%B")
        return f"The current month is {current_month}"

    elif "year" in question or "current year" in question:
        current_year = datetime.now().strftime("%Y")
        return f"The current year is {current_year}"

    elif "play" in question:
        seperated_result = re.search("play (.+)", question)
        if seperated_result:
            result = seperated_result.group(1)
            results = YoutubeSearch(result, max_results=1).to_dict()
            for v in results:
                webbrowser.open("https://www.youtube.com" + v["url_suffix"])
                return "Playing " + v["title"]

    elif "google" in question or "search" in question:
        if "google" in question:
            reg_ex = re.search("google (.+)", question)

        elif "search" in question:
            reg_ex = re.search("search (.+)", question)

        if reg_ex:
            domain = reg_ex.group(1)
            url = "https://www.google.com/search?q=" + domain
            webbrowser.open(url)
            return "Showing some results of " + domain + " on Google."

    elif "cricket news" in question or "news cricket" in question:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36"
        }
        r = requests.get("https://www.cricbuzz.com/", headers=headers)
        soup = BeautifulSoup(r.text, "lxml")
        result = soup.find_all("a", class_="cb-nws-hdln-ancr text-hvr-underline")
        for result in result[:3]:
            return result.text

    elif "calculate" in question:
        try:
            if "calculate" in question:
                reg_ex = re.search("calculate (.+)", question)

            if reg_ex:
                domain = reg_ex.group(1)
                return "Answer: " + str(eval(domain))
        except Exception as e:
            return "Sorry, I couldn't calculate that, I am still learning."

    elif (
        "search youtube" in question
        or "youtube" in question
        or "how to" in question
        or "recipe for" in question
    ):
        if "youtube" in question:
            reg_ex = re.search("youtube (.+)", question)

        elif "search youtube" in question:
            reg_ex = re.search("search youtube (.+)", question)

        elif "how to" in question:
            reg_ex = re.search("how to (.+)", question)

        elif "recipe for" in question:
            reg_ex = re.search("recipe for (.+)", question)

        if reg_ex:
            domain = reg_ex.group(1)
            url = "https://www.youtube.com/results?search_query=" + domain

            results = YoutubeSearch(domain, max_results=1).to_dict()
            for v in results:
                webbrowser.open(url)
                return (
                    "Showing some results of "
                    + domain
                    + " on Youtube: <br><b>"
                    + v["title"]
                    + "</b> "
                    + "https://www.youtube.com"
                    + v["url_suffix"].split("&")[0]
                )

    elif "who is" in question:
        who_is = re.search("who is (.+)", question)
        domain = who_is.group(1)
        results = wikipedia.summary(question, sentences=1)
        return results

    elif "where is" in question or "locate" in question:
        if "where is" in question:
            location = re.search("where is (.+)", question)

        elif "locate" in question:
            location = re.search("locate (.+)", question)

        locate = location.group(1)
        locate = "https://www.google.com/maps/place/" + str(locate) + "/&amp;"
        webbrowser.open(locate)
        return "Showing <b>" + str(locate) + "</b> on Map."

    elif "news" == question:
        news_url = "https://news.google.com/news/rss"
        Client = urlopen(news_url)
        xml_page = Client.read()
        Client.close()
        soup_page = BeautifulSoup(xml_page, "xml")
        news_list = soup_page.findAll("item")
        for news in news_list[:3]:
            news_string = str(news.title.text.encode("utf-8"))
            news_converted_string = re.sub("[b]", "", news_string)
            return news_converted_string

    return model.predict([question])[0]


@app.route("/")
def index():
    if server == 1:
        return jsonify({"status": "Server is running"})
    elif server == 0:
        return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    question = request.form["question"]

    toxic = toxicity.is_toxic(question)

    if toxic:
        return jsonify(
            {"response": "It's an inappropriate question, I can't answer that."}
        )
    else:
        model = load_model()
        response = get_response(question, model)
        return jsonify({"response": response})


@app.route("/api/chat", methods=["POST"])
def api_chat():
    if request.method == "POST":
        if "question" not in request.json:
            return jsonify({"error": "Question parameter missing"}), 400
        question = request.json["question"]
        model = load_model()
        response = get_response(question, model)
        return jsonify({"response": response}), 200


@app.errorhandler(404)
def page_not_found(error):
    return jsonify({"error": "Page not found"}), 404


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=port)
