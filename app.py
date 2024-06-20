import io
import socket
from flask import Flask, Response, Blueprint, request, jsonify, render_template
from flask_cors import CORS

try:
    from werkzeug.wsgi import FileWrapper
except ImportError:
    from werkzeug import FileWrapper

global STATE
STATE = {}

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

''' Admin '''

@admin_bp.route('/sessions')
def admin_sessions():
    connected_sessions = []
    for key, session in STATE.items():
        connected_sessions.append({
            'key': key,
            'filename': session['filename'],
            'events_count': len(session['events']),
            'computer_name': session['computer_name']
        })
    
    return render_template('session.html', sessions=connected_sessions)

app.register_blueprint(admin_bp)

''' Client '''

@app.route('/')
def root():
    return render_template('/index.html')

@app.route('/rd', methods=['POST'])
def rd():
    req = request.get_json()
    key = req['_key']

    if req['filename'] == STATE[key]['filename']:
        attachment = io.BytesIO(b'')
    else:
        attachment = io.BytesIO(STATE[key]['im'])

    w = FileWrapper(attachment)
    resp = Response(w, mimetype='text/plain', direct_passthrough=True)
    resp.headers['filename'] = STATE[key]['filename']
  
    return resp

@app.route('/event_post', methods=['POST'])
def event_post():
    global STATE

    req = request.get_json()
    key = req['_key']

    STATE[key]['events'].append(request.get_json())
    return jsonify({'ok': True})

''' Remote '''

@app.route('/new_session', methods=['POST'])
def new_session():
    global STATE

    req = request.get_json()
    key = req['_key']
    computer_name = req.get('computer_name', 'unknown')  # Get the computer name from the request

    STATE[key] = {
        'im': b'',
        'filename': 'none.png',
        'events': [],
        'computer_name': computer_name
    }

    return jsonify({'ok': True})

@app.route('/capture_post', methods=['POST'])
def capture_post():
    global STATE
  
    with io.BytesIO() as image_data:
        filename = list(request.files.keys())[0]
        key = filename.split('_')[1]
        request.files[filename].save(image_data)
        STATE[key]['im'] = image_data.getvalue()
        STATE[key]['filename'] = filename

    return jsonify({'ok': True})

@app.route('/events_get', methods=['POST'])
def events_get():
    req = request.get_json()
    key = req['_key']
    events_to_execute = STATE[key]['events'].copy()
    STATE[key]['events'] = []
    return jsonify({'events': events_to_execute})

@app.route('/get_keys', methods=['GET'])
def key_events_get():
    events_to_execute = []  # Convert dict_items to a list
    for key, session in STATE.items():
        events_to_execute.append({
            'key': key,
            'filename': session['filename'],
            'events_count': len(session['events']),
            'computer_name': session['computer_name']
        })
    return jsonify({'keys': events_to_execute})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    # app.run()
