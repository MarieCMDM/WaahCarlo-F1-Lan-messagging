import os
import asyncio
import httpx
from functools import wraps
from typing import Callable
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from playsound import playsound
from dotenv import load_dotenv

from .lan_devices import DeviceDiscoverer

load_dotenv()

NAME = os.getenv('VISIBLE_NAME')
SUBNET = os.getenv('SUBNET')
SECRET_KEY = os.getenv('GROUP_SECRET')

app = Flask(__name__)
CORS(app)


PORT = 9000
REQUEST_TIMEOUT = 2
AUDIO_FOLDER = './audios'
CHECK_ENDPOINT = 'waahCavlo'
audio_files = os.listdir(AUDIO_FOLDER)
audio_names = [file.split('.')[0] for file in audio_files]


discoverer = DeviceDiscoverer(PORT, REQUEST_TIMEOUT, CHECK_ENDPOINT, SUBNET)
httpx_client = httpx.Client()

def is_localhost_request(f: Callable):
    @wraps(f)
    def wrap(*args, **kwargs):
        if request.remote_addr == "127.0.0.1" or request.remote_addr == "::1" or request.remote_addr == 'localhost':
            return f(*args, **kwargs)
        else:
            return jsonify(error="Unautorized"), 403

    return wrap

def sercet_required(f: Callable):
    @wraps(f)
    def wrap(*args, **kwargs):
        if request.args.get('secret') == SECRET_KEY:
            return f(*args, **kwargs)
        else:
            return jsonify(error="Unautorized"), 403

    return wrap

@app.get('/')
@is_localhost_request
def index():
    return render_template('index.html')

@app.get('/devices/')
@is_localhost_request
def get_devices():
    devices = {}
    try:
        discovered_devices = asyncio.run(discoverer.scan_network(SECRET_KEY))
        for device_ip, device_name in discovered_devices:
            devices[device_ip] = device_name
        return jsonify(devices=devices), 200
    except Exception as e:
        print(e)
        return jsonify(message='Failed to get local devices'), 500

# @app.post('/dev/audio/files/reload/')
# @is_localhost_request
# def relaod_audio_files():
#     try:
#         audio_files = os.listdir(AUDIO_FOLDER)
#         audio_names = [file.split('.')[0] for file in audio_files]
#         return jsonify(audios=audio_names), 200
#     except Exception as e:
#         return jsonify(message='Failed to reload audio files', error=e), 500

# @app.post('/dev/audio/files/')
# @is_localhost_request
# def add_audio_file():
#     try:
#         #TODO
#         return jsonify(audios=audio_names), 200
#     except Exception as e:
#         return jsonify(message='Failed to add audio files', error=e), 500

@app.get('/proxy/<device>/audio/')
@is_localhost_request
def get_audios_on_remote(device: str):
    try:
        params = {'secret': SECRET_KEY}
        url = f'http://{device}:{PORT}/audio/'
        response = httpx_client.get(url, params=params)
        return response.json()
    except Exception as e:
        return jsonify(message='Failed to play audio files on remote'), 500
    
@app.post('/proxy/<device>/audio/<name>/')
@is_localhost_request
def play_on_remote(device: str, name: str):
    try:
        params = {'secret': SECRET_KEY}
        url = f'http://{device}:{PORT}/audio/{name}/'
        response = httpx_client.post(url, params=params)
        return response.json()
    except Exception as e:
        return jsonify(message='Failed to play audio files on remote',), 500

@app.get(f'/{CHECK_ENDPOINT}')
@sercet_required
def waah_cavlo():
    return jsonify(name=NAME)

@app.get('/audio/')
@sercet_required
def get_audio():
    return jsonify(audios=audio_names), 200

@app.post('/audio/<name>/')
@sercet_required
def play_audio(name):
    for file in audio_files:
        if name in file:
            try:
                playsound(os.path.join(AUDIO_FOLDER, file))
                return jsonify(message='played'), 200
            except Exception as e:
                return jsonify(message='Failed to play audio files'), 500
    return jsonify(message=f'No audio file found for {name}'), 500