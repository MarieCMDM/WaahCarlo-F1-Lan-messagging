import os

from flask import Flask, jsonify
from flask_cors import CORS
from playsound import playsound

from lan_devices import DeviceDiscover

app = Flask(__name__)
CORS(app)

AUDIO_FOLDER = './audios'
audio_files = os.listdir(AUDIO_FOLDER)
audio_names = [file.split('.')[0] for file in audio_files]

discoverer = DeviceDiscover('Mattia-aorus')

@app.get('/devices/')
def get_devices():
    try:
        devices = discoverer.discoverLanDevices()
        print(devices)
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
    app.run(host='0.0.0.0', port=9000, debug=True)