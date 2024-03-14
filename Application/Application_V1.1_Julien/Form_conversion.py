import numpy as np  # Pour les opérations mathématiques
import wave  # Pour la manipulation de fichiers audio WAV
import struct  # Pour manipuler des données binaires
import sounddevice as sd  # Pour jouer du son
import matplotlib.pyplot as plt


# Variables globales pour l'audio
playing_audio = False
current_audio_file = None
audio_data = None
saved_drawings = []

# Canva and window
window = 0
canvas = 0

CANVA_WIDTH = 680
CANVA_HEIGHT = 680
WINDOW_WIDTH = CANVA_WIDTH + 20
WINDOW_HEIGHT = CANVA_HEIGHT + 50

# Distance horizontale entre les boutons
X_DISTANCE_BETWEEN_BUTTON = 10

drawing = True

# Couleur du trait de dessin
color = 'black'

# Listes des coordonnées x et y du dessin
#xList = GUI.xList
#yList = GUI.yList

# Chemin du fichier audio de sortie
OutputFilename = './audio/'
data_size = 240000

# Amplitude du signal audio
amplitude = 2 ** 15 - 1  # multiplicateur pour l'amplitude

RECORD_DURATION = 5
FORMS_PER_SECONDE = 30
personlized_rate = 0

# Fréquence du signal audio
frequency = 30
wavFileDuration = 5  # Seconds, must be an integer

# Nombre de répétitions du dessin
drawRepetition = frequency * wavFileDuration


def get_default_output_device_sample_rate():
    # Obtenir l'ID du dispositif de sortie audio par défaut
    default_output_device = sd.default.device[1]
    # Obtenir les informations du dispositif
    device_info = sd.query_devices(default_output_device, 'output')
    # Retourner la fréquence d'échantillonnage par défaut
    return device_info['default_samplerate']


def clear_wrong_values(tab):
    for i in range(len(tab)):
        if tab[i] < -1:
            tab[i] = -1
        elif tab[i] > 1:
            tab[i] = 1

    return tab


# Fonction pour convertir le dessin en signal audio
def convert_form_to_signal(xList, yList, canvas, audio_name):
    global amplitude, OutputFilename

    # On récupère le nom choisi par l'utilisateur
    OutputFilename += audio_name + ".wav"

    # Normalisez les coordonnées du dessin entre -1 et 1
    x_normalized = ((np.array(xList) - (CANVA_WIDTH / 2)) / (CANVA_WIDTH / 2))
    y_normalized = ((np.array(yList) - (CANVA_HEIGHT / 2)) / (CANVA_HEIGHT / 2))

    # Recadrage des valeurs hors interval (lorsque la souris sort de la fenêtre pendant le dessin)
    x_normalized = clear_wrong_values(x_normalized)
    y_normalized = clear_wrong_values(y_normalized)

    print("Nombre de points : ", len(x_normalized))

    rate = len(xList) * frequency
    if rate > get_default_output_device_sample_rate():
        print("Rate 1 : ", rate)
        # Calcul du nombre total de points dans le dessin
        total_points = len(x_normalized)
        # Calcul du nombre de points maximum autorisés
        max_points = get_default_output_device_sample_rate()

        # Condition qui détermine la taille du pas
        if total_points <= max_points:
            step_size = 1
        else:
            step_size = total_points // max_points

        data_x = []
        data_y = []
        for i in range(drawRepetition):
            for n in range(0, total_points, step_size):
                data_x.append(x_normalized[n])
                data_y.append(y_normalized[n])

    else:
        print("Rate 2 : ", rate)
        print("get_default_output_device_sample_rate : ", get_default_output_device_sample_rate())
        print("frequency : ", frequency)
        initial_indices = np.arange(0, len(x_normalized), 1)
        new_indices = np.arange(0, len(x_normalized), len(x_normalized) / int (get_default_output_device_sample_rate() / frequency))

        x_interpolated = np.interp(new_indices, initial_indices, x_normalized)
        y_interpolated = np.interp(new_indices, initial_indices, y_normalized)

        #figure, axis = plt.subplots(2, 1)

        #axis[0].plot(x_interpolated)
        #axis[1].plot(x_interpolated, y_interpolated)
        #plt.show()

        data_x = []
        data_y = []

        for i in range(drawRepetition):
            for j in range(len(x_interpolated)):
                data_x.append(x_interpolated[j])
                data_y.append(y_interpolated[j])

    wv = wave.open(OutputFilename, 'w')
    wv.setparams((2, 2, get_default_output_device_sample_rate(), 0, 'NONE', 'not compressed'))
    # CHANGER AVEC AMPLITUDE
    maxVol = 2 ** 15 - 1.0  # maximum amplitude (32767)
    wvData = b""

    for i in range(len(data_x)):
        wvData += struct.pack('h', int(maxVol * data_x[i]))  # Left
        wvData += struct.pack('h', int(maxVol * data_y[i]))  # Right

    wv.writeframes(wvData)
    wv.close()
    print("WAV file is ready.")

    # Clear the canva
    canvas.delete("all")  # Efface le dessin sur le canevas
    canvas.create_text(CANVA_WIDTH / 2, CANVA_HEIGHT / 2, text="Form converted to signal", font=("Arial", 16))