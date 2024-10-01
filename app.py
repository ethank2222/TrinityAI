from anthropic import Anthropic
from openai import OpenAI
import google.generativeai as genai
from flask import Flask, render_template, jsonify, request
import os
import marko

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
            system="Please respond with the best answer.",
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



@app.route('/ask_question', methods=['POST'])
def ask_question():
    data = request.get_json()
    question = data['question']
    
    openai_response = getResponse("openai", question)
    gemini_response = getResponse("gemini", question)
    claude_response = getResponse("claude", question)
    vote1 = 0
    vote2 = 0
    vote3 = 0
    tool = 1

    #while vote1 != "1" and vote1 != "2" and vote1 != "3":
    vote1 = getResponse("openai", "Here was the question that was given: " + question + "Given the following three responses, return only the number of the best response." + "1. " + openai_response + " 2. " + gemini_response + " 3. " + claude_response + " Remember, only return the number '1', '2', or '3' as a standalone number.")
    #while vote2 != "1" and vote2 != "2" and vote2 != "3":
    vote2 = getResponse("gemini", "Here was the question that was given: " + question + "Given the following three responses, return only the number of the best response." + "1. " + openai_response + " 2. " + gemini_response + " 3. " + claude_response + " Remember, only return the number '1', '2', or '3' as a standalone number.")
    #while vote3 != "1" and vote3 != "2" and vote3 != "3":
    vote3 = getResponse("claude", "Here was the question that was given: " + question + "Given the following three responses, return only the number of the best response." + "1. " + openai_response + " 2. " + gemini_response + " 3. " + claude_response + " Remember, only return the number '1', '2', or '3' as a standalone number.")
    
    vote1 = int(vote1)
    vote2 = int(vote2)
    vote3 = int(vote3)

    votesfor1 = 0
    votesfor2 = 0
    votesfor3 = 0

    if vote1 == 1:
        votesfor1 += 1
    elif vote1 == 2:
        votesfor2 += 1
    elif vote1 == 3:
        votesfor3 += 1
    if vote2 == 1:
        votesfor1 += 1
    elif vote2 == 2:
        votesfor2 += 1
    elif vote2 == 3:
        votesfor3 += 1
    if vote3 == 1:
        votesfor1 += 1
    elif vote3 == 2:
        votesfor2 += 1
    elif vote3 == 3:
        votesfor3 += 1
    
    if votesfor1 > votesfor2 and votesfor1 > votesfor3:
        tool = 1
    if votesfor2 > votesfor1 and votesfor2 > votesfor3:
        tool = 2
    if votesfor3 > votesfor1 and votesfor3 > votesfor2:
        tool = 3
    
    if tool == 1:
        best_response = openai_response
    elif tool == 2:
        best_response = gemini_response
    else:
        best_response = claude_response
    
    print(tool)
    print(best_response)
    result = {'message': marko.convert(best_response), 'tool': tool}
    return jsonify(result)


if __name__ == '__main__':
   app.run()

