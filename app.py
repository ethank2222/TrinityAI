from anthropic import Anthropic
from openai import OpenAI
import google.generativeai as genai
from flask import Flask, render_template, jsonify, request
import os
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()

def get_response(ai_type, question):
    """Get response from AI service"""
    try:
        if ai_type == "openai":
            client = OpenAI(api_key=os.environ.get('OPENAI_KEY'))
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": question}],
                stream=True
            )
            return ''.join(chunk.choices[0].delta.content for chunk in response if chunk.choices[0].delta.content)
        
        elif ai_type == "gemini":
            genai.configure(api_key=os.environ.get('GEMINI_KEY'))
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(question)
            return response.text
        
        elif ai_type == "claude":
            client = Anthropic(api_key=os.environ.get('CLAUDE_KEY'))
            response = client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=1000,
                messages=[{"role": "user", "content": question}]
            )
            return response.content[0].text
        
        return "Invalid AI service"
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/health')
def health():
    return "OK", 200

@app.route('/openai', methods=['POST'])
def openai():
    data = request.get_json()
    response = get_response("openai", data['question'])
    return jsonify({"message": response})

@app.route('/gemini', methods=['POST'])
def gemini():
    data = request.get_json()
    response = get_response("gemini", data['question'])
    return jsonify({"message": response})

@app.route('/claude', methods=['POST'])
def claude():
    data = request.get_json()
    response = get_response("claude", data['question'])
    return jsonify({"message": response})

if __name__ == '__main__':
    app.run(debug=True)