import json

def load_responses(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def get_response(question, responses):
    if question in responses:
        return responses[question]
    else:
        return "I'm sorry, I don't have an answer for that."

def main():
    file_path = 'chat.json'
    responses = load_responses(file_path)

    while True:
        question = input("User: ")
        response = get_response(question, responses)
        print("Chatbot:", response)

if __name__ == '__main__':
    main()
