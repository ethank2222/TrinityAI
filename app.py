from anthropic import Anthropic
from openai import OpenAI
import google.generativeai as genai
from flask import Flask, render_template, jsonify, request
import os
import marko
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
from bson import ObjectId
import datetime


load_dotenv()


mongo_client = MongoClient(os.environ.get('MONGODB_URI'))
try:
    mongo_client.server_info()  # This will raise an error if the connection fails
    print("Connected to MongoDB")
except Exception as e:
    print(f"MongoDB connection error: {e}")

db_name = 'trinityai_dev' if os.environ.get('FLASK_ENV') == 'development' else 'trinityai_prod'
db = mongo_client.get_database(db_name)
interactions_collection = db.interactions

def getResponse(type, question):
    if type == "openai":
        #OpenAI
        client = OpenAI(api_key=os.environ.get('OPENAI_KEY'))
        open_ai_stream = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": question}
            ],
            stream=True
        )
        open_ai_response = ''
        for chunk in open_ai_stream:
            if chunk.choices[0].delta.content is not None:
                open_ai_response += chunk.choices[0].delta.content
        return open_ai_response
    elif type == "gemini":
        #Gemini
        genai.configure(api_key=os.environ.get('GEMINI_KEY'))
        model = genai.GenerativeModel("gemini-1.5-flash")
        gemini_stream = model.generate_content(question)
        return gemini_stream.text
    elif type == "claude":
        #claude
        client2 = Anthropic(api_key=os.environ.get('CLAUDE_KEY'))
        claude_stream = client2.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1000,
            temperature=0,
            system="",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": question
                        }
                    ]
                }
            ]
        )
        claude_response = claude_stream.content[0].text
        return claude_response
    else:
        return "N/A"

app = Flask(__name__)
@app.route('/')
def home():
    return render_template('index.html')

#openai first response
@app.route('/openaiFirstResponse', methods=['POST'])
def openaiFirstResponse():
    data = request.get_json()
    question = "Please respond with the best answer to the following question:" + data['question']
    response = getResponse("openai", question)
    return jsonify({"message": response})
#gemini first response
@app.route('/geminiFirstResponse', methods=['POST'])
def geminiFirstResponse():
    data = request.get_json()
    question = "Please respond with the best answer to the following question:" + data['question']
    response = getResponse("gemini", question)
    return jsonify({"message": response})
#claude first response
@app.route('/claudeFirstResponse', methods=['POST'])
def claudeFirstResponse():
    data = request.get_json()
    question = "Please respond with the best answer to the following question:" + data['question']
    response = getResponse("claude", question)
    return jsonify({"message": response})

#openai modifying response
@app.route('/openaiModifyingResponse', methods=['POST'])
def openaiModifyingResponse():
    question = request.get_json()['question']
    response = getResponse("openai", question)
    return jsonify({"message": response})
#gemini modifying response
@app.route('/geminiModifyingResponse', methods=['POST'])
def geminiModifyingResponse():
    question = request.get_json()['question']
    response = getResponse("gemini", question)
    return jsonify({"message": response})
#claude modifying response
@app.route('/claudeModifyingResponse', methods=['POST'])
def claudeModifyingResponse():
    question = request.get_json()['question']
    response = getResponse("claude", question)
    return jsonify({"message": response})

#openai voting
@app.route('/openaiVoting', methods=['POST'])
def openaiVoting():
    question = request.get_json()['question']
    response = getResponse("openai", question)
    if "1" in response:
        return jsonify({"message": 1})
    if "2" in response:
        return jsonify({"message": 2})
    return jsonify({"message": 3})
#gemini voting
@app.route('/geminiVoting', methods=['POST'])
def geminiVoting():
    question = request.get_json()['question']
    response = getResponse("gemini", question)
    if "1" in response:
        return jsonify({"message": 1})
    if "2" in response:
        return jsonify({"message": 2})
    return jsonify({"message": 3})
#claude voting response
@app.route('/claudeVoting', methods=['POST'])
def claudeVoting():
    question = request.get_json()['question']
    response = getResponse("claude", question)
    if "1" in response:
        return jsonify({"message": 1})
    if "2" in response:
        return jsonify({"message": 2})
    return jsonify({"message": 3})

@app.route('/postDatapoint', methods=['POST'])
def postDatapoint():
    try:
        answer = request.get_json()['answer']
        tool = request.get_json()['tool']
        rating = int(request.get_json()['rating'])

        datapoint = {
            "answer": answer,
            "tool": tool,
            "rating": rating,
        }
        
        result = interactions_collection.insert_one(datapoint)

        datapoints = list(interactions_collection.find())
        for each in datapoints:
            each['_id'] = str(each['_id'])  # Convert ObjectId to string
            print(each)

        return jsonify({"message": "Thank you for your input!"})
    except Exception as e:
        # Handle any errors and return an error response
        return jsonify({"message": "Unable to process the request at this time."})

def getWeights():
    datapoints = list(interactions_collection.find())
    for each in datapoints:
        each['_id'] = str(each['_id'])  # Convert ObjectId to string
        print(each)
    openai = 0
    claude = 0
    gemini = 0

    #implement ML Algo Here





    return [openai, gemini, claude]




if __name__ == '__main__':
   app.run()

