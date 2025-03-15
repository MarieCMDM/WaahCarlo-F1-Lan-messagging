import os
import asyncio

from flask import Flask, jsonify 
from flask_cors import CORS
from playsound import playsound

from lan_devices import DeviceDiscoverer

PORT = 9000
SUBNET = '10.10.0.0/24'
NAME = 'Mattia'

app = Flask(__name__)
CORS(app)

AUDIO_FOLDER = './audios'
CHECK_ENDPOINT = 'waahCavlo'
audio_files = os.listdir(AUDIO_FOLDER)
audio_names = [file.split('.')[0] for file in audio_files]


discoverer = DeviceDiscoverer(PORT, 2, CHECK_ENDPOINT, SUBNET)
devices = asyncio.run(discoverer.scan_network())

@app.get(f'/{CHECK_ENDPOINT}')
def waah_cavlo():
    return jsonify(name=NAME)

@app.get('/devices/')
def get_devices():
    devices = {}
    try:
        discovered_devices = asyncio.run(discoverer.scan_network())
        print(discovered_devices)
        for device_ip, device_name in discovered_devices:
            print(device_ip, device_name)
            devices[device_ip] = device_name
        return jsonify(devices=devices), 200
    except Exception as e:
        return jsonify(message='Failed to get local devices', error=e), 500

@app.post('/dev/audio/files/reload/')
def relaod_audio_files():
    try:
        audio_files = os.listdir(AUDIO_FOLDER)
        audio_names = [file.split('.')[0] for file in audio_files]
        return jsonify(audios=audio_names), 200
    except Exception as e:
        return jsonify(message='Failed to reload audio files', error=e), 500

@app.get('/audio/')
def get_audio():
    return jsonify(audios=audio_names), 200

@app.post('/audio/<name>/')
def play_audio(name):
    for file in audio_files:
        if name in file:
            try:
                playsound(os.path.join(AUDIO_FOLDER, file))
                return jsonify(message='played'), 200
            except Exception as e:
                return jsonify(message='Failed to play audio files', error=e), 500
    return jsonify(message=f'No audio file found for {name}'), 500
            
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=True)