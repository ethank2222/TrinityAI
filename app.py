from anthropic import Anthropic
from openai import OpenAI
import google.generativeai as genai
from flask import Flask, render_template, jsonify, request
import os
import logging
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
            api_key = os.environ.get('GEMINI_KEY')
            if not api_key:
                logger.error("GEMINI_KEY not found in environment variables")
                return "Error: Gemini API key not configured"
            
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-2.5-flash")
                logger.info(f"Generating content with Gemini for question: {question[:50]}...")
                response = model.generate_content(question)
                
                # Check if response is blocked or has issues
                if not response.text:
                    if response.candidates and response.candidates[0].finish_reason:
                        finish_reason = response.candidates[0].finish_reason
                        logger.warning(f"Gemini response blocked. Finish reason: {finish_reason}")
                        if finish_reason == genai.types.FinishReason.SAFETY:
                            return "Response blocked due to safety concerns. Please try a different question."
                        elif finish_reason == genai.types.FinishReason.RECITATION:
                            return "Response blocked due to recitation concerns. Please try a different question."
                        else:
                            return f"Response blocked. Reason: {finish_reason}"
                    else:
                        logger.warning("Gemini returned empty response with no finish reason")
                        return "No response generated. Please try again."
                
                logger.info("Gemini response generated successfully")
                return response.text
                
            except Exception as gemini_error:
                logger.error(f"Gemini API error: {str(gemini_error)}")
                return f"Gemini API error: {str(gemini_error)}"
        
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