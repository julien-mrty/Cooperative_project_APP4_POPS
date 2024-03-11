import tkinter
from tkinter import filedialog

import cv2
import numpy as np
import svgwrite
import wave
import struct
import sounddevice as sd


# Canva and window
window = 0
canvas = 0

CANVA_WIDTH = 600
CANVA_HEIGHT = 400
WINDOW_WIDTH = CANVA_WIDTH + 20
WINDOW_HEIGHT = CANVA_HEIGHT + 50

X_DISTANCE_BETWEEN_BUTTON = 10

drawing = True
color = 'black'


# Form coordonates
xList = []
yList = []


# Audio
audio_name = "./audio/WaveStereo.wav"
# Initial : 44100.0
# Test : 11025.0
# Échantillonnage à x kHz
framerate = 11025.0 # framerate as a float
data_size = 240000
amplitude = 2 ** 15 - 1 # multiplier for amplitude

COMPUTER_SOUND_RATE = 48000
RECORD_DURATION = 5
FORMS_PER_SECONDE = 30
personlized_rate = 0


def onClick(event):
    global xList, yList, drawing

    if drawing is not False:
        xList.append(event.x)
        yList.append(event.y)


def onMove(event):
    global xList, yList, drawing

    if drawing is not False:
        canvas.create_line(xList[-1], yList[-1], event.x, event.y, fill=color, width=3)
        xList.append(event.x)
        yList.append(event.y)
        # print("LEN : ", len(xList))


def onClickRelease(event):
    global drawing
    drawing = False


def clear_canvas(canva):
    global drawing
    canva.delete('all')
    drawing = True

def clear_wrong_values(tab):
    for i in range(len(tab)):
        if tab[i] < -1:
            tab[i] = -1
        elif tab[i] > 1:
            tab[i] = 1

    return tab

def convert_form_to_signal():
    global xList, yList, framerate, audio_name, amplitude

    # Normalisez les coordonnées du dessin entre -1 et 1
    x_normalized = ((np.array(xList) - (CANVA_WIDTH / 2)) / (CANVA_WIDTH / 2))
    y_normalized = ((np.array(yList) - (CANVA_HEIGHT / 2)) / (CANVA_HEIGHT / 2))

    x_normalized = clear_wrong_values(x_normalized)
    y_normalized = clear_wrong_values(y_normalized)

    frequency = 30
    wavFileDuration = 5  # Seconds, must be an integer.
    drawRepetition = frequency * wavFileDuration  # Nombre de répétitions du dessin.
    OutputFilename = './audio/Free.wav'

    # Calcul du nombre total de points dans le dessin
    total_points = len(x_normalized)
    # Calcul du nombre de points maximum autorisés
    max_points = 48000

    if total_points <= max_points:
        step_size = 1
    else:
        step_size = total_points // max_points

    data_x = []
    data_y = []
    for i in range(drawRepetition):
        for n in range(0, total_points, step_size):
            print("index : ", n)
            print("_____ X value : ", x_normalized[n])
            print("_____ Y value : ", y_normalized[n])
            data_x.append(x_normalized[n])
            data_y.append(y_normalized[n])

    wv = wave.open(OutputFilename, 'w')
    wv.setparams((2, 2, int(framerate), 0, 'NONE', 'not compressed'))
    maxVol = 2 ** 15 - 1.0  # maximum amplitude (32767)
    wvData = b""

    for i in range(len(data_x)):
        print("LEFT : ", maxVol * data_x[i])
        print("RIGHT : ", maxVol * data_y[i])
        wvData += struct.pack('h', int(maxVol * data_x[i]))  # Left
        wvData += struct.pack('h', int(maxVol * data_y[i]))  # Right

    wv.writeframes(wvData)
    wv.close()

    canvas.delete("all")
    canvas.create_text(CANVA_WIDTH / 2, CANVA_HEIGHT / 2, text="Form converted to signal", font=("Arial", 16))

    print("WAV file is ready.")


def initWindow():
    global window, canvas
    window = tkinter.Tk()
    window.title('Draw or Load Image')

    # Crée un bouton pour dessiner
    button_draw = tkinter.Button(window, text="Draw", command=lambda: {canvas.bind('<Button-1>', onClick),
                                                                       canvas.bind('<B1-Motion>', onMove),
                                                                       canvas.bind('<ButtonRelease-1>', onClickRelease)
                                                                       })
    button_draw.place(x=X_DISTANCE_BETWEEN_BUTTON, y=get_next_y_button_position())

    # Clear the canva to draw a new form
    button_clear_canva = tkinter.Button(window, text="Clear canva", command=lambda: clear_canvas(canvas))
    button_clear_canva.place(x=get_next_x_button_position(button_draw), y=get_next_y_button_position())

    # Button to convert the form to audio signal
    bouton_convertir_audio = tkinter.Button(window, text="Convert to audio signal", command=convert_form_to_signal)
    bouton_convertir_audio.place(x=get_next_x_button_position(button_clear_canva), y=get_next_y_button_position())

    canvas = tkinter.Canvas(window, width=CANVA_WIDTH, height=CANVA_HEIGHT, bg='white')
    canvas.place(x=10, y=40)
    window_size_str = "{0}x{1}".format(WINDOW_WIDTH, WINDOW_HEIGHT)
    window.geometry(window_size_str)

    window.mainloop()



def get_next_x_button_position(previous_button):
    global window
    window.update() # Update the coordonates of the widgets in the window

    return previous_button.winfo_width() + previous_button.winfo_x() + X_DISTANCE_BETWEEN_BUTTON

def get_next_y_button_position():
    return 5


initWindow()
