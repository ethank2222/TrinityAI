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

load_dotenv()

myWeights = []
mongo_client = MongoClient(os.environ.get('MONGODB_URI'), serverSelectionTimeoutMS=5000)
db = mongo_client.get_database('trinityai_dev')
db_interactions = db.interactions
    

def getResponse(type, question):
    if type == "openai":
        #OpenAI
        api_key = os.environ.get('OPENAI_KEY')
        if not api_key:
            return "Error: OpenAI API key not configured"
        
        try:
            client = OpenAI(api_key=api_key)
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
            
        except Exception as openai_error:
            error_message = str(openai_error)
            if "insufficient_quota" in error_message or "billing" in error_message.lower() or "quota" in error_message.lower():
                return "Error: OpenAI API quota insufficient. Please check your billing."
            elif "invalid_api_key" in error_message or "authentication" in error_message.lower():
                return "Error: Invalid OpenAI API key. Please check your API key."
            elif "rate_limit" in error_message.lower() or "rate limit" in error_message.lower():
                return "Error: OpenAI API rate limit exceeded. Please try again later."
            elif "model" in error_message.lower() and "not found" in error_message.lower():
                return "Error: OpenAI model not available. Please try a different model."
            elif "timeout" in error_message.lower():
                return "Error: OpenAI API request timed out. Please try again."
            elif "connection" in error_message.lower():
                return "Error: Unable to connect to OpenAI API. Please check your internet connection."
            else:
                return f"OpenAI API error: {error_message}"
    elif type == "gemini":
        #Gemini
        api_key = os.environ.get('GEMINI_KEY')
        if not api_key:
            return "Error: Gemini API key not configured"
        
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(question)
            
            # Check if response is blocked or has issues
            if not response.text:
                if response.candidates and response.candidates[0].finish_reason:
                    finish_reason = response.candidates[0].finish_reason
                    if finish_reason == genai.types.FinishReason.SAFETY:
                        return "Response blocked due to safety concerns. Please try a different question."
                    elif finish_reason == genai.types.FinishReason.RECITATION:
                        return "Response blocked due to recitation concerns. Please try a different question."
                    else:
                        return f"Response blocked. Reason: {finish_reason}"
                else:
                    return "No response generated. Please try again."
            
            return response.text
            
        except Exception as gemini_error:
            error_message = str(gemini_error)
            if "api_key" in error_message.lower() or "authentication" in error_message.lower():
                return "Error: Invalid Gemini API key. Please check your API key."
            elif "quota" in error_message.lower() or "billing" in error_message.lower():
                return "Error: Gemini API quota insufficient. Please check your billing."
            elif "rate_limit" in error_message.lower() or "rate limit" in error_message.lower():
                return "Error: Gemini API rate limit exceeded. Please try again later."
            elif "model" in error_message.lower() and "not found" in error_message.lower():
                return "Error: Gemini model not available. Please try a different model."
            elif "timeout" in error_message.lower():
                return "Error: Gemini API request timed out. Please try again."
            elif "connection" in error_message.lower():
                return "Error: Unable to connect to Gemini API. Please check your internet connection."
            else:
                return f"Gemini API error: {error_message}"
    elif type == "claude":
        #claude
        api_key = os.environ.get('CLAUDE_KEY')
        if not api_key:
            return "Error: Claude API key not configured"
        
        try:
            client2 = Anthropic(api_key=api_key)
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
            
        except Exception as claude_error:
            error_message = str(claude_error)
            if "credit balance is too low" in error_message or "insufficient credits" in error_message or "billing" in error_message.lower():
                return "Error: Claude API credits insufficient. Please check your billing."
            elif "invalid_request_error" in error_message or "authentication" in error_message.lower():
                return "Error: Invalid Claude API request. Please check your API key and permissions."
            elif "rate_limit" in error_message.lower() or "rate limit" in error_message.lower():
                return "Error: Claude API rate limit exceeded. Please try again later."
            elif "model" in error_message.lower() and "not found" in error_message.lower():
                return "Error: Claude model not available. Please try a different model."
            elif "timeout" in error_message.lower():
                return "Error: Claude API request timed out. Please try again."
            elif "connection" in error_message.lower():
                return "Error: Unable to connect to Claude API. Please check your internet connection."
            else:
                return f"Claude API error: {error_message}"
    else:
        return "N/A"

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
    try:

        db_interactions.insert_one(datapoint)

        datapoints = list(db_interactions.find())
        for each in datapoints:
            print(each)

        return jsonify({"message": "Thank you for your input!"})
    except Exception as e:
        # Handle any errors and return an error response
        return jsonify({"message": "Unable to process the request at this time."})

def getWeights(question):
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
    return


if __name__ == '__main__':
    app.run(debug=True)