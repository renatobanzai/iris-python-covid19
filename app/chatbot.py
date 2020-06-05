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

obj_irisdomestic = irisdomestic(config["iris"])

def get_model(language):
    global_data_training = "^chatbot.training.data." + language
    corpus_model = "chatterbot.corpus." + language
    chatbot_name = "Banzaibot " + language
    db_language = "sqlite:///db." + language

    training_iterator = obj_irisdomestic.iterator(global_data_training, "question")
    training_data = []
    for question, answer in training_iterator:
        training_data.append(question)
        training_data.append(answer)

    bot = ChatBot(chatbot_name, storage_adapter="chatterbot.storage.SQLStorageAdapter", database_uri=db_language)
    trainer = ChatterBotCorpusTrainer(bot)
    trainer.train(corpus_model)

    if len(training_data) > 0:
        trainer_list = ListTrainer(bot)
        trainer_list.train(training_data)

    obj_irisdomestic.set("1", global_data_training, "isupdated")
    return bot

english_bot = get_model("english")
russian_bot = get_model("russian")
brazilian_bot = get_model("portuguese")
spanish_bot = get_model("spanish")


app = Flask(__name__)
languages = ["english", "russian", "spanish", "portuguese"]



@app.route("/")
def home():
    for language in languages:
        global_data_training = "^chatbot.training.data." + language
        if obj_irisdomestic.isDefined(global_data_training, "isupdated") == 0:
            is_updated = "0"
        else:
            is_updated = obj_irisdomestic.get(global_data_training, "isupdated")

        if is_updated == "0":
            if language=="english":
                english_bot = get_model(language)
            elif language=="russian":
                russian_bot = get_model(language)
            elif language=="spanish":
                spanish_bot = get_model(language)
            elif language=="portuguese":
                brazilian_bot_bot = get_model(language)
            obj_irisdomestic.set("1", "^chatbot.training.isupdated")

    return render_template("index.html")

@app.route("/get")
def get_bot_response():
    if request.remote_addr:
        remote_addr = request.remote_addr
    else:
        remote_addr = "unknown"

    chatuser = request.args.get('login')
    userText = request.args.get('msg')
    language = request.args.get('language')
    conversation_global = "^chatbot.conversation." + language

    if language == "english":
        bot = english_bot
    elif language == "russian":
        bot = russian_bot
    elif language == "spanish":
        bot = spanish_bot
    elif language == "portuguese":
        bot = brazilian_bot


    result = str(bot.get_response(userText))
    obj_irisdomestic.set(remote_addr, conversation_global, chatuser, userText, result)
    return result


if __name__ == "__main__":
    app.run(host='0.0.0.0')
