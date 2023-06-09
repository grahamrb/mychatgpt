from threading import Lock
from flask import Flask, render_template, session, request, \
    copy_current_request_context
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
import openai
import os
openai.api_type = "azure"
openai.api_base = os.getenv("OPENAI_API_BASE")
openai.api_version = "2023-03-15-preview"
openai.api_key = os.getenv("OPENAI_API_KEY")
deployment_name = os.getenv("OPENAI_DEPLOYMENT_NAME")

vars_set = True

if 'OPENAI_API_BASE' not in os.environ or 'OPENAI_API_KEY' not in os.environ or 'OPENAI_DEPLOYMENT_NAME' not in os.environ:
    vars_set = False

base_prompt = {"role": "system", "content": "You are a helpful assistant, your name is Logan."}

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24).hex()
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()

def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        socketio.sleep(10)
        count += 1
        # socketio.emit('my_response',
        #               {'data': 'Server generated event', 'isControl': True, 'count': count})


@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)

@socketio.event
def disconnect_request():
    @copy_current_request_context
    def can_disconnect():
        disconnect()

    session['receive_count'] = session.get('receive_count', 0) + 1
    # for this emit we use a callback function
    # when the callback function is invoked we know that the message has been
    # received and it is safe to disconnect
    emit('my_response',
         {'data': 'Disconnected!', 'isControl': True, 'count': session['receive_count']},
         callback=can_disconnect)


@socketio.event
def my_ping():
    emit('my_pong')


@socketio.event
def connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
    emit('my_response', {'data': 'Connected', 'isControl': True, 'count': 0})


@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected', request.sid)


@socketio.event
def chat(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    if 'messages' not in session:
        session['messages'] = []
        session['messages'].append(base_prompt)
    #print(message)
    session['messages'].append({"role": "user", "content": message['data']})
    #print(session['messages'])
    response = openai.ChatCompletion.create(
        # engine="gpt-35-turbo",
        engine=deployment_name,
        messages=session['messages']
    )

    #print(response)
    #print(response['choices'][0]['message']['content'])
    session['messages'].append({"role": "assistant", "content": response['choices'][0]['message']['content']})

    emit('my_response',
         {'data': response['choices'][0]['message']['content'], 'isControl': False,
          'count': session['receive_count']})


if __name__ == '__main__':
    socketio.run(app, port=5000)
