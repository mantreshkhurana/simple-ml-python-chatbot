import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline

def load_responses(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)
    return data

def train_model(data):
    questions = list(data.keys())
    responses = list(data.values())
    model = make_pipeline(TfidfVectorizer(), MultinomialNB())
    model.fit(questions, responses)
    return model

def save_model(model, model_file="chat.joblib"):
    from joblib import dump
    dump(model, model_file)
    print(f"Model saved to {model_file}")

if __name__ == "__main__":
    responses_data = load_responses("chat.json")
    model = train_model(responses_data)
    save_model(model)
