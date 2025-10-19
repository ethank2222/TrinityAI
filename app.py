from anthropic import Anthropic
from openai import OpenAI
import google.generativeai as genai
from flask import Flask, render_template, jsonify, request
import os
from pymongo import MongoClient
from dotenv import load_dotenv
import weights
import database

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Health check endpoint for Railway"""
    return jsonify({"status": "healthy", "message": "TrinityAI is running"})

load_dotenv()

myWeights = []

# Initialize MongoDB connection with error handling
try:
    mongodb_uri = os.environ.get('MONGODB_URI')
    if not mongodb_uri:
        print("Warning: MONGODB_URI environment variable not set. Database functionality will be limited.")
        mongo_client = None
        db = None
        db_interactions = None
    else:
        mongo_client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
        db = mongo_client.get_database('trinityai_dev')
        db_interactions = db.interactions
        # Test connection
        mongo_client.admin.command('ping')
        print("MongoDB connection established successfully")
except Exception as e:
    print(f"MongoDB connection failed: {e}")
    mongo_client = None
    db = None
    db_interactions = None
    

def getResponse(type, question):
    try:
        if type == "openai":
            #OpenAI
            openai_key = os.environ.get('OPENAI_KEY')
            if not openai_key:
                return "OpenAI API key not configured"
            client = OpenAI(api_key=openai_key)
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
            gemini_key = os.environ.get('GEMINI_KEY')
            if not gemini_key:
                return "Gemini API key not configured"
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            gemini_stream = model.generate_content(question)
            return gemini_stream.text
        elif type == "claude":
            #claude
            claude_key = os.environ.get('CLAUDE_KEY')
            if not claude_key:
                return "Claude API key not configured"
            client2 = Anthropic(api_key=claude_key)
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
            return "Invalid AI service type"
    except Exception as e:
        print(f"Error in getResponse for {type}: {e}")
        return f"Error: {str(e)}"

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
    if db_interactions is not None:
        if len(list(db_interactions.find({"tool": 1}))) > 5 and len(list(db_interactions.find({"tool": 2}))) > 5 and len(list(db_interactions.find({"tool": 3}))) > 5:
            myWeights = getWeights(question)
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
        if db_interactions is None:
            return jsonify({"message": "Database not available. Thank you for your input!"})
            
        question = request.get_json()['question']
        tool = request.get_json()['tool']
        score = int(request.get_json()['score'])
        if tool == "openai":
            tool = 1
        elif tool == "gemini":
            tool = 2
        else:
            tool = 3

        datapoint = {
            "question": question,
            "tool": tool,
            "score": score,
        }

        db_interactions.insert_one(datapoint)

        datapoints = list(db_interactions.find())
        for each in datapoints:
            print(each)

        return jsonify({"message": "Thank you for your input!"})
    except Exception as e:
        print(f"Error in postDatapoint: {e}")
        return jsonify({"message": "Unable to process the request at this time."})

def getWeights(question):
    try:
        if db_interactions is None:
            print("Database not available for weighting")
            return [.333, .333, .333]
            
        datapoints = list(db_interactions.find())
        for each in datapoints:
            each['_id'] = str(each['_id'])  # Convert ObjectId to string
            print(each)

        if len(datapoints) <= 3:
            print("Not enough Data for Weighting Process")
            return [.333, .333, .333]

        #implement ML Algo Here
        myWeights = weights.computeWeights(datapoints, question)
        
        print(f"Successfully weighted with weights openai: {myWeights[0]}, gemini: {myWeights[1]}, and claude: {myWeights[2]}")
        return myWeights
    except Exception as e:
        print(f"Error in getWeights: {e}")
        return [.333, .333, .333]


if __name__ == '__main__':
    app.run(debug=True)