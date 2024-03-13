# Importation des bibliothèques nécessaires
import tkinter
from tkinter import filedialog  # Pour les boîtes de dialogue de sélection de fichiers
import cv2  # OpenCV pour le traitement d'images
import numpy as np  # Pour les opérations mathématiques
import svgwrite  # Pour créer des fichiers SVG
import wave  # Pour la manipulation de fichiers audio WAV
import struct  # Pour manipuler des données binaires
import sounddevice as sd  # Pour jouer du son

# Variables globales pour la fenêtre et le canvas
window = 0
canvas = 0

# Dimensions du canvas et de la fenêtre
CANVA_WIDTH = 600
CANVA_HEIGHT = 400
WINDOW_WIDTH = CANVA_WIDTH + 20
WINDOW_HEIGHT = CANVA_HEIGHT + 50

# Distance horizontale entre les boutons
X_DISTANCE_BETWEEN_BUTTON = 10

# Booléen pour le dessin
drawing = True

# Couleur du trait de dessin
color = 'black'

# Listes des coordonnées x et y du dessin
xList = []
yList = []

# Chemin du fichier audio de sortie
audio_name = "./audio/WaveStereo.wav"

# Fréquence d'échantillonnage du son en Hz
framerate = 11025.0  # framerate en tant que float

# Taille des données audio
data_size = 240000

# Amplitude du signal audio
amplitude = 2 ** 15 - 1  # multiplicateur pour l'amplitude

# Fréquence de l'ordinateur
COMPUTER_SOUND_RATE = 48000

# Durée de l'enregistrement en secondes
RECORD_DURATION = 5

# Formes par seconde pour la conversion en signal audio
FORMS_PER_SECONDE = 30

# Taux personnalisé pour la fréquence
personlized_rate = 0

# Fonction appelée lors d'un clic de souris
def onClick(event):
    global xList, yList, drawing

    if drawing is not False:
        xList.append(event.x)
        yList.append(event.y)

# Fonction appelée lors d'un mouvement de souris
def onMove(event):
    global xList, yList, drawing

    if drawing is not False:
        canvas.create_line(xList[-1], yList[-1], event.x, event.y, fill=color, width=3)
        xList.append(event.x)
        yList.append(event.y)

# Fonction appelée lors du relâchement du clic de souris
def onClickRelease(event):
    global drawing
    drawing = False

# Fonction pour effacer le canvas
def clear_canvas(canva):
    global drawing
    canva.delete('all')
    drawing = True

# Fonction pour vérifier et ajuster les valeurs incorrectes dans un tableau
def clear_wrong_values(tab):
    for i in range(len(tab)):
        if tab[i] < -1:
            tab[i] = -1
        elif tab[i] > 1:
            tab[i] = 1

    return tab

# Fonction pour convertir le dessin en signal audio
def convert_form_to_signal():
    global xList, yList, framerate, audio_name, amplitude

    # Normalisation des coordonnées du dessin entre -1 et 1
    x_normalized = ((np.array(xList) - (CANVA_WIDTH / 2)) / (CANVA_WIDTH / 2))
    y_normalized = ((np.array(yList) - (CANVA_HEIGHT / 2)) / (CANVA_HEIGHT / 2))

    x_normalized = clear_wrong_values(x_normalized)
    y_normalized = clear_wrong_values(y_normalized)

    # Fréquence du signal audio
    frequency = 30
    # Durée du fichier audio en secondes
    wavFileDuration = 5
    # Nombre de répétitions du dessin
    drawRepetition = frequency * wavFileDuration

    # Nom du fichier de sortie
    OutputFilename = './audio/Free.wav'

    # Calcul du nombre total de points dans le dessin
    total_points = len(x_normalized)
    # Calcul du nombre de points maximum autorisés
    max_points = 48000

    #Condition qui détermine la taille du pas
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

    # Création du fichier audio WAV
    wv = wave.open(OutputFilename, 'w')
    wv.setparams((2, 2, int(framerate), 0, 'NONE', 'not compressed'))
    maxVol = 2 ** 15 - 1.0

    wvData = b""
    for i in range(len(data_x)):
        wvData += struct.pack('h', int(maxVol * data_x[i]))  # Gauche
        wvData += struct.pack('h', int(maxVol * data_y[i]))  # Droite

    wv.writeframes(wvData)
    wv.close()

    # Effacer le canvas après la conversion
    canvas.delete("all")
    canvas.create_text(CANVA_WIDTH / 2, CANVA_HEIGHT / 2, text="Form converted to signal", font=("Arial", 16))

    print("Le fichier WAV est prêt.")

# Initialisation de la fenêtre et des éléments graphiques
def initWindow():
    global window, canvas
    window = tkinter.Tk()
    window.title('Dessiner ou Charger une Image')

    # Bouton pour dessiner
    button_draw = tkinter.Button(window, text="Dessiner", command=lambda: {
        canvas.bind('<Button-1>', onClick),
        canvas.bind('<B1-Motion>', onMove),
        canvas.bind('<ButtonRelease-1>', onClickRelease)
    })
    button_draw.place(x=X_DISTANCE_BETWEEN_BUTTON, y=get_next_y_button_position())

    # Bouton pour effacer le canvas
    button_clear_canva = tkinter.Button(window, text="Effacer le canvas", command=lambda: clear_canvas(canvas))
    button_clear_canva.place(x=get_next_x_button_position(button_draw), y=get_next_y_button_position())

    # Bouton pour convertir en signal audio
    bouton_convertir_audio = tkinter.Button(window, text="Convertir en signal audio", command=convert_form_to_signal)
    bouton_convertir_audio.place(x=get_next_x_button_position(button_clear_canva), y=get_next_y_button_position())

    # Canvas pour dessiner
    canvas = tkinter.Canvas(window, width=CANVA_WIDTH, height=CANVA_HEIGHT, bg='white')
    canvas.place(x=10, y=40)

    # Taille de la fenêtre
    window_size_str = "{0}x{1}".format(WINDOW_WIDTH, WINDOW_HEIGHT)
    window.geometry(window_size_str)

    # Boucle principale pour afficher la fenêtre
    window.mainloop()

# Fonction pour obtenir la prochaine position horizontale d'un bouton
def get_next_x_button_position(previous_button):
    global window
    window.update()  # Met à jour les coordonnées des widgets dans la fenêtre
    return previous_button.winfo_width() + previous_button.winfo_x() + X_DISTANCE_BETWEEN_BUTTON

# Fonction pour obtenir la prochaine position verticale d'un bouton
def get_next_y_button_position():
    return 5

# Démarrage de l'interface graphique
initWindow()
