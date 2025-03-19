let selectedDeviceIp = null;
let selectedDeviceName = null;

function showPopup(message) {
    $('#popup-message').text(message);
    $('#popup').fadeIn();
    setTimeout(() => {
        $('#popup').fadeOut();
    }, 2000);
}

function loadDevices() {
    $.get('/devices/', function(data) {
        $('#device-list').empty();
        Object.entries(data.devices).forEach(([ip, name]) => {
            $('#device-list').append(
                `<button onclick="selectDevice('${ip}', '${name}')">${name} (${ip})</button>`
            );
        });
    }).fail(function() {
        showPopup('Errore nel caricamento dei dispositivi');
    });
}

function selectDevice(ip, name) {
    selectedDeviceIp = ip;
    selectedDeviceName = name;
    $('#content h2').text(`Audio disponibili per ${selectedDeviceName}`);
    loadAudioFiles();
}

function loadAudioFiles() {
    $.get(`/proxy/${selectedDeviceIp}/audio/`, function(data) {
        $('#audio-list').empty();
        data.audios.forEach(audio => {
            $('#audio-list').append(
                `<button class="audio-btn" onclick="playAudio('${audio}')">${audio}</button>`
            );
        });
    }).fail(function() {
        showPopup('Errore nel caricamento degli audio');
    });
}

function playAudio(audio) {
    if (!selectedDeviceIp) {
        showPopup('Seleziona prima un dispositivo');
        return;
    }
    $.post(`/proxy/${selectedDeviceIp}/audio/${audio}/`, function(response) {
        showPopup(`Riproduzione terminata su ${selectedDeviceName}`);
    }).fail(function() {
        showPopup('Errore durante la riproduzione dell audio');
    });
}

$(document).ready(function() {
    loadDevices();
});