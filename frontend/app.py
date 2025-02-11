from flask import Flask, request, jsonify, render_template, session
from flask_session import Session
import time
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from generate_response import generate_response
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_secure_secret_key')  

app.config['SESSION_TYPE'] = 'filesystem'  
app.config['SESSION_FILE_DIR'] = os.path.join(app.root_path, 'flask_session') 
app.config['SESSION_PERMANENT'] = False  
app.config['SESSION_USE_SIGNER'] = True  

Session(app)

if not os.path.exists(app.config['SESSION_FILE_DIR']):
    os.makedirs(app.config['SESSION_FILE_DIR'])

import logging
logging.basicConfig(level=logging.WARNING)

AVAILABLE_TOOLS = [
    {"name": "FPPredictor", "description": "This tool performs first-principles (FP) calculations to predict molecular properties. Use it for detailed, physics-based property predictions."},
    {"name": "MLPredictor", "description": "This tool utilizes machine learning-driven potential energy surface (PES) models to predict molecular properties based on trained data. Ideal for high-efficiency predictions."},
    {"name": "PredictorSelect", "description": "This tool helps select the appropriate prediction model (FP or ML) based on the task. Use it to optimize the property prediction process."},
    {"name": "DatasetSearch", "description": "This tool searches databases to retrieve molecular property data. Use it when looking for existing data for a specific molecule or material."},
    {"name": "StructureGenerate", "description": "This tool generates molecular structures for specified compounds. Use it to create 3D models from molecular formulas or descriptions."},
    {"name": "LiteratureSearch", "description": "This tool searches scientific literature for relevant papers and articles. Use it to find research references or detailed studies on molecular properties."},
    {"name": "WebSearch", "description": "This tool performs a web search for relevant external information. Use it to retrieve general knowledge or details not found in specialized databases."},
    {"name": "HumanExpert", "description": "This tool connects you with human experts in the field for complex, nuanced queries. Use it for insights or answers beyond the capabilities of automated tools."},
    {"name": "Python_REPL", "description": "A Python shell for executing Python commands. Use it to run code, conduct calculations, or test functions. To see results, print values using `print(...)`."}
]

def init_session():
    if 'mode' not in session:
        session['mode'] = None  
        session['config'] = None  
    if 'messages' not in session:
        session['messages'] = []

@app.route('/')
def index():
    init_session()
    return render_template('index.html')

@app.route('/set_mode', methods=['POST'])
def set_mode():
    data = request.get_json()
    mode = data.get('mode') 
    config = data.get('config') 

    if mode not in ['Ollama', 'ChatGPT']:
        return jsonify({'error': 'Invalid mode selected.'}), 400

    session['mode'] = mode
    session['config'] = config
    session.modified = True

    return jsonify({'status': 'success'})

@app.route('/get_available_tools', methods=['GET'])
def get_available_tools():
    return jsonify({'tools': AVAILABLE_TOOLS})

@app.route('/get_messages', methods=['GET'])
def get_messages():
    init_session()
    return jsonify({'messages': session.get('messages', [])})

@app.route('/chat', methods=['POST'])
def chat():
    init_session()
    data = request.get_json()
    user_message = data.get('message', '').strip()

    if not user_message:
        return jsonify({'error': 'Empty message'}), 400

    mode = session.get('mode')
    config = session.get('config')

    if not mode or not config:
        return jsonify({'error': 'Mode or config not set. Please select a mode first.'}), 400

    session['messages'].append({'sender': 'user', 'text': user_message})

    response = generate_response(user_message)

    session['messages'].append({'sender': 'bot', 'text': response})

    session.modified = True

    return jsonify({'response': response})

def call_app():
    app.run(debug=False)

if __name__ == '__main__':
    app.run(debug=False) 
