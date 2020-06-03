from flask import Flask, render_template, request
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer, ListTrainer
from iris_python_suite import irisglobal, irisdomestic, irisglobalchart
import yaml

try:
    with open("../data/config.yaml", "r") as file:
        config = yaml.safe_load(file)
except Exception as e:
    print('Error reading the config file')

app = Flask(__name__)

english_bot = ChatBot("Chatterbot", storage_adapter="chatterbot.storage.SQLStorageAdapter")
trainer = ChatterBotCorpusTrainer(english_bot)
trainer.train("chatterbot.corpus.english")
training_data = [
    "Who will win the contest?",
    "I am hoping Banzai",
    "Banzai has chances to win the contest?",
    "Do you like me?",
    "Star Wars or Star Trek?",
    "Sorry, I dont discuss religion.",
    "Whats the answer for the life universe and eveything?",
    "The answer is 42."
]
trainer_list = ListTrainer(english_bot)
trainer_list.train(training_data)


obj_irisdomestic = irisdomestic(config["iris"])

@app.route("/")
def home():
    if obj_irisdomestic.isDefined("^chatbot.training.isupdated") == 0:
        is_updated = "0"
    else:
        is_updated = obj_irisdomestic.get("^chatbot.training.isupdated")

    if is_updated == "0":
        english_bot = ChatBot("Chatterbot", storage_adapter="chatterbot.storage.SQLStorageAdapter")
        trainer = ChatterBotCorpusTrainer(english_bot)
        trainer.train("chatterbot.corpus.english")
        training_data = [
            "Who will win the contest?",
            "I am hoping Banzai",
            "Banzai has chances to win the contest?",
            "Do you like me?",
            "Star Wars or Star Trek?",
            "Sorry, I dont discuss religion.",
            "Whats the answer for the life universe and eveything?",
            "The answer is 42."
        ]
        trainer_list = ListTrainer(english_bot)
        training_data = [
            "Who will win the contest?",
            "I am hoping Banzai",
            "Banzai has chances to win the contest?",
            "Do you like me?",
            "Star Wars or Star Trek?",
            "Sorry, I dont discuss religion.",
            "Whats the answer for the life universe and eveything?",
            "The answer is 42."
        ]
        training_iterator = obj_irisdomestic.iterator("^chatbot.training.data")
        for question, answer in training_iterator:
            training_data.append(question)
            training_data.append(answer)

        trainer_list.train(training_data)
        obj_irisdomestic.set("1","^chatbot.training.isupdated")
    return render_template("index.html")

@app.route("/get")
def get_bot_response():
    if request.remote_addr:
        chatuser = request.remote_addr
    else:
        chatuser = "unknown"

    userText = request.args.get('msg')
    result = str(english_bot.get_response(userText))
    obj_irisdomestic.set(result, "^chatbot.conversation", chatuser, userText)
    return result


if __name__ == "__main__":
    app.run(host='0.0.0.0')
