from anthropic import Anthropic
from openai import OpenAI
import requests
from flask import Flask, render_template, jsonify, request
import os
from pymongo import MongoClient
from dotenv import load_dotenv
import weights
import database
import time
import threading
import uuid

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
    elif type == "grok":
        # Grok (xAI) official SDK usage
        try:
            from xai_sdk import Client
            from xai_sdk.chat import user, system
        except ImportError:
            return "[Grok xai_sdk not installed]"
        xai_api_key = os.environ.get('GROK_KEY')
        if not xai_api_key:
            return "[Grok API key not set]"
        try:
            client = Client(api_key=xai_api_key)
            chat = client.chat.create(model="grok-4")
            chat.append(system("You are Grok, a highly intelligent, helpful AI assistant."))
            chat.append(user(question))
            response = chat.sample()
            return response.content
        except Exception as e:
            return f"[Grok exception: {str(e)}]"
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

#openai first response
@app.route('/openaiFirstResponse', methods=['POST'])
def openaiFirstResponse():
    data = request.get_json()
    question = "Please respond with the best answer to the following question:" + data['question']
    response = getResponse("openai", question)
    return jsonify({"message": response})
#grok first response
@app.route('/grokFirstResponse', methods=['POST'])
def grokFirstResponse():
    data = request.get_json()
    question = "Please respond with the best answer to the following question:" + data['question']
    response = getResponse("grok", question)
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
#grok modifying response
@app.route('/grokModifyingResponse', methods=['POST'])
def grokModifyingResponse():
    question = request.get_json()['question']
    response = getResponse("grok", question)
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
#grok voting
@app.route('/grokVoting', methods=['POST'])
def grokVoting():
    question = request.get_json()['question']
    response = getResponse("grok", question)
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

# In-memory store for Socratic sessions
socratic_sessions = {}

@app.route('/socraticAnalysis', methods=['POST'])
def socratic_analysis():
    data = request.get_json()
    question = data.get('question', '')
    session_id = str(uuid.uuid4())
    # Initialize session state
    socratic_sessions[session_id] = {
        'turns': [],
        'summary': '',
        'agreement': '',
        'arguments': '',
        'finished': False,
        'error': None,
        'question': question,
    }
    # Start debate in background
    def socratic_debate_thread(session_id, question):
        try:
            start_time = time.time()
            max_rounds = 5
            timeout = 180  # 3 minutes
            llms = [
                {'name': 'OpenAI', 'type': 'openai'},
                {'name': 'Grok', 'type': 'grok'},
                {'name': 'Anthropic', 'type': 'claude'},
            ]
            turns = []
            consensus = False
            def build_prompt(llm_name, question, turns, round_num):
                others = [t for t in turns[-len(llms):] if t['llm'] != llm_name]
                other_args = '\n'.join([
                    f"{t['llm']}: {t['overview']}\n{t['full']}" for t in others
                ])
                prompt = f"""
You are {llm_name}, an expert AI model. This is round {round_num+1} of a Socratic debate with two other advanced AIs.\n
The question is: {question}\n
Here are the most recent arguments from the other AIs:\n{other_args if other_args else '(no arguments yet)'}\n\nYour task:\n- Provide a concise overview of your position (1-2 sentences, start with 'Overview:').\n- Then provide your full, detailed reasoning (start with 'Full:').\n- If you agree with another model, say so and explain why.\n- If you disagree, critique their arguments and defend your own.\n- If you think consensus is reached, state it clearly.\n- If you do not agree, that is perfectly fine—honest, well-reasoned disagreement is valuable and not a failure.\n- Try to come to an agreement if possible, but do not force consensus.\n- Be clear and specific.\n"""
                return prompt
            for round_num in range(max_rounds):
                round_turns = []
                for llm in llms:
                    if time.time() - start_time > timeout:
                        break
                    prompt = build_prompt(llm['name'], question, turns + round_turns, round_num)
                    try:
                        response = getResponse(llm['type'], prompt)
                        overview = ''
                        full = ''
                        if 'Overview:' in response and 'Full:' in response:
                            parts = response.split('Overview:')[-1].split('Full:')
                            overview = parts[0].strip()
                            full = parts[1].strip() if len(parts) > 1 else ''
                        else:
                            s = response.split('.')
                            overview = s[0].strip() + '.' if s else response
                            full = response
                        round_turns.append({
                            'llm': llm['name'],
                            'overview': overview,
                            'full': full
                        })
                    except Exception as e:
                        round_turns.append({
                            'llm': llm['name'],
                            'overview': f'[Error: {str(e)}]',
                            'full': f'[Error: {str(e)}]'
                        })
                turns.extend(round_turns)
                socratic_sessions[session_id]['turns'] = turns.copy()
                # Check for consensus in this round
                overviews = [t['overview'].lower() for t in round_turns if t['overview']]
                if len(overviews) == len(llms):
                    # If all overviews contain 'consensus' or are identical, treat as consensus
                    if all('consensus' in ov or ov == overviews[0] for ov in overviews):
                        consensus = True
                        break
                if time.time() - start_time > timeout:
                    break
            summary = ''
            agreement = ''
            arguments = ''
            # Helper to get a concise summary from OpenAI
            def get_concise_summary(prompt):
                try:
                    return getResponse('openai', prompt)
                except Exception:
                    return ''
            if consensus:
                # Use the consensus round for summary/arguments
                last_overviews = [t['overview'] for t in turns[-len(llms):]]
                last_fulls = [t['full'] for t in turns[-len(llms):]]
                summary_prompt = (
                    "Given the following overviews and arguments from three AI models who have reached consensus, "
                    "write a single concise summary (1-2 sentences) of their agreed answer, omitting repetition and meta-commentary. "
                    "Overviews: " + ' | '.join(last_overviews) + ". Arguments: " + ' | '.join(last_fulls)
                )
                agreement_prompt = (
                    "Given the following overviews from three AI models who have reached consensus, "
                    "write a single short sentence stating what they agreed on. Overviews: " + ' | '.join(last_overviews)
                )
                summary = get_concise_summary(summary_prompt)
                agreement = get_concise_summary(agreement_prompt)
                arguments = ' '.join([t['llm'] + ': ' + t['full'] for t in turns[-len(llms):]])
            else:
                last_turns = turns[-len(llms):]
                last_overviews = [t['overview'] for t in last_turns]
                last_fulls = [t['full'] for t in last_turns]
                summary_prompt = (
                    "Given the following overviews and arguments from three AI models who did not reach consensus, "
                    "write a single concise summary (1-2 sentences) of the main points of agreement and disagreement, omitting repetition and meta-commentary. "
                    "Overviews: " + ' | '.join(last_overviews) + ". Arguments: " + ' | '.join(last_fulls)
                )
                agreement_prompt = (
                    "Given the following overviews from three AI models who did not reach consensus, "
                    "write a single short sentence summarizing the main areas of agreement or disagreement. Overviews: " + ' | '.join(last_overviews)
                )
                summary = get_concise_summary(summary_prompt)
                agreement = get_concise_summary(agreement_prompt)
                arguments = ' '.join([f"{t['llm']}: {t['full']}" for t in last_turns])
            socratic_sessions[session_id]['summary'] = summary
            socratic_sessions[session_id]['agreement'] = agreement
            socratic_sessions[session_id]['arguments'] = arguments
            socratic_sessions[session_id]['finished'] = True
        except Exception as e:
            socratic_sessions[session_id]['error'] = str(e)
            socratic_sessions[session_id]['finished'] = True
    # Launch background thread
    thread = threading.Thread(target=socratic_debate_thread, args=(session_id, question))
    thread.start()
    # Return session_id and initial state
    return jsonify({
        'session_id': session_id,
        'turns': [],
        'summary': '',
        'agreement': '',
        'arguments': '',
        'finished': False
    })

@app.route('/socraticAnalysisStream')
def socratic_analysis_stream():
    session_id = request.args.get('session_id')
    if not session_id or session_id not in socratic_sessions:
        return jsonify({'error': 'Invalid session_id'}), 400
    session = socratic_sessions[session_id]
    return jsonify({
        'turns': session['turns'],
        'summary': session['summary'],
        'agreement': session['agreement'],
        'arguments': session['arguments'],
        'finished': session['finished'],
        'error': session['error'],
    })

@app.route('/postDatapoint', methods=['POST'])
def postDatapoint():
    question = request.get_json()['question']
    tool = request.get_json()['tool']
    score = int(request.get_json()['score'])
    if tool == "openai":
        tool = 1
    elif tool == "grok":
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
    
    print(f"Successfully weighted with weights openai: {myWeights[0]}, grok: {myWeights[1]}, and claude: {myWeights[2]}")
    return


if __name__ == '__main__':
    app.run(debug=True)