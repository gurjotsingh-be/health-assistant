from flask import Flask, request, jsonify, render_template, session
from crew import HealthAssistantCrew
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')

consultation_history = {}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        symptoms = data.get('symptoms', '')
        age = data.get('age', '')
        medical_history = data.get('medical_history', '')
        
        if not symptoms or not age:
            return jsonify({
                'success': False,
                'error': 'Symptoms and age are required'
            }), 400
        
        try:
            age_int = int(age)
            if age_int < 0 or age_int > 150:
                return jsonify({
                    'success': False,
                    'error': 'Please enter a valid age between 0 and 150'
                }), 400
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Age must be a valid number'
            }), 400
        
        crew = HealthAssistantCrew()
        result = crew.run(symptoms, age, medical_history)
        
        consultation_data = {
            'timestamp': datetime.now().isoformat(),
            'symptoms': symptoms,
            'age': age,
            'medical_history': medical_history,
            'result': result
        }
        
        if 'session_id' not in session:
            session['session_id'] = os.urandom(16).hex()
        
        session_id = session['session_id']
        if session_id not in consultation_history:
            consultation_history[session_id] = []
        
        consultation_history[session_id].append(consultation_data)
        
        return jsonify({
            'success': True,
            'result': result,
            'consultation_id': len(consultation_history[session_id]) - 1
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/history', methods=['GET'])
def get_history():
    try:
        if 'session_id' not in session:
            return jsonify({
                'success': True,
                'history': []
            })
        
        session_id = session['session_id']
        history = consultation_history.get(session_id, [])
        
        simplified_history = [{
            'id': idx,
            'timestamp': item['timestamp'],
            'symptoms': item['symptoms'][:100] + '...' if len(item['symptoms']) > 100 else item['symptoms'],
            'age': item['age']
        } for idx, item in enumerate(history)]
        
        return jsonify({
            'success': True,
            'history': simplified_history
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/history/<int:consultation_id>', methods=['GET'])
def get_consultation(consultation_id):
    try:
        if 'session_id' not in session:
            return jsonify({
                'success': False,
                'error': 'No consultation history found'
            }), 404
        
        session_id = session['session_id']
        history = consultation_history.get(session_id, [])
        
        if consultation_id < 0 or consultation_id >= len(history):
            return jsonify({
                'success': False,
                'error': 'Consultation not found'
            }), 404
        
        return jsonify({
            'success': True,
            'consultation': history[consultation_id]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/export/<int:consultation_id>', methods=['GET'])
def export_consultation(consultation_id):
    try:
        if 'session_id' not in session:
            return "No consultation history found", 404
        
        session_id = session['session_id']
        history = consultation_history.get(session_id, [])
        
        if consultation_id < 0 or consultation_id >= len(history):
            return "Consultation not found", 404
        
        consultation = history[consultation_id]
        
        export_text = f"""
HEALTH CONSULTATION REPORT
Generated: {consultation['timestamp']}

PATIENT INFORMATION
Age: {consultation['age']}
Medical History: {consultation['medical_history'] or 'None provided'}

SYMPTOMS
{consultation['symptoms']}

ASSESSMENT
{consultation['result']}
"""
        
        return export_text, 200, {
            'Content-Type': 'text/plain; charset=utf-8',
            'Content-Disposition': f'attachment; filename=consultation_{consultation_id}.txt'
        }
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
