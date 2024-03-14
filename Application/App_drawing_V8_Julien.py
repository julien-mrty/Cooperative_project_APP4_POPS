import tkinter
from tkinter import filedialog

import cv2
import numpy as np
import svgwrite
import wave
import struct
import sounddevice as sd
import matplotlib.pyplot as plt


# Canva and window
window = 0
canvas = 0

CANVA_WIDTH = 600
CANVA_HEIGHT = 600
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

frequency = 30
wavFileDuration = 5  # Seconds, must be an integer
drawRepetition = frequency * wavFileDuration  # Nombre de répétitions du dessin.
OutputFilename = './audio/Draw.wav'


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


def onClickRelease(event):
    global drawing
    drawing = False


def clear_canvas(canva):
    global drawing, xList, yList
    canva.delete('all')
    xList.clear()
    yList.clear()
    drawing = True


def get_default_output_device_sample_rate():
    # Obtenir l'ID du dispositif de sortie audio par défaut
    default_output_device = sd.default.device[1]
    # Obtenir les informations du dispositif
    device_info = sd.query_devices(default_output_device, 'output')
    # Retourner la fréquence d'échantillonnage par défaut
    return device_info['default_samplerate']

sample_rate = get_default_output_device_sample_rate()
print(f"Default Output Device Sample Rate: {sample_rate} Hz")

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

    rate = len(xList) * frequency
    if rate > get_default_output_device_sample_rate():
        print("RATE : ", rate)
        raise ValueError("Samplerate of over ", get_default_output_device_sample_rate, " can be incompatible with the computer audio board.")

    x_interpolation = np.linspace(-1, 1, int (get_default_output_device_sample_rate() / frequency))
    initial_indices = np.arange(0, len(x_normalized), 1)
    new_indices = np.arange(0, len(x_normalized), len(x_normalized) / int (get_default_output_device_sample_rate() / frequency))

    print("Nombre de points  par image souhaîté : ", int (get_default_output_device_sample_rate() / frequency))
    print("LEN NEW  : ", len(new_indices))

    x_interpolated = np.interp(new_indices, initial_indices, x_normalized)
    y_interpolated = np.interp(new_indices, initial_indices, y_normalized)

    figure, axis = plt.subplots(2, 1)

    axis[0].plot(x_interpolation)
    axis[1].plot(x_interpolated)
    plt.show()

    data_x = []
    data_y = []

    for i in range(drawRepetition):
        for j in range(len(x_interpolated)):
            data_x.append(x_interpolated[j])
            data_y.append(y_interpolated[j])

    wv = wave.open(OutputFilename, 'w')
    wv.setparams((2, 2, rate, 0, 'NONE', 'not compressed'))
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


def charger_et_traiter_image():
    # Ouvrir une boîte de dialogue pour sélectionner un fichier image
    fichier_image = filedialog.askopenfilename()

    if fichier_image:
        # Lire l'image depuis le fichier sélectionné
        img = cv2.imread(fichier_image)

        # Conversion de l'image en niveaux de gris
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Définition du seuil de l'image en niveaux de gris
        _, threshold = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

        # Utilisation de la fonction findContours pour détecter les contours
        contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Création d'un objet SVG
        dwg = svgwrite.Drawing('contours.svg', profile='tiny', size=(img.shape[1], img.shape[0]))

        # Dessiner les contours dans le fichier SVG
        for contour in contours:
            # Approximation de la forme
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)

            # Création d'un chemin SVG à partir des contours
            path_data = ""
            for point in approx:
                x, y = point[0]
                if path_data == "":
                    path_data = f"M{x},{y}"
                else:
                    path_data += f" L{x},{y}"
            path_data += " Z"  # Fermer le chemin

            # Ajouter le chemin SVG à l'objet SVG
            path = svgwrite.path.Path(d=path_data, stroke=svgwrite.rgb(255, 0, 0, '%'), fill='none', stroke_width=2)
            dwg.add(path)

        # Enregistrez le fichier SVG
        dwg.save()

        # Affichez l'image avec les contours
        img_with_contours = img.copy()
        cv2.drawContours(img_with_contours, contours, -1, (0, 0, 255), 2)
        cv2.imshow('Image avec contours', img_with_contours)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


def convertir_en_svg():
    # Création d'un objet SVG
    dwg = svgwrite.Drawing('../drawing/draw.svg', profile='tiny', size=(CANVA_WIDTH, CANVA_HEIGHT))

    # Dessiner les lignes du dessin en SVG
    for i in range(len(xList) - 1):
        x1, y1, x2, y2 = xList[i], yList[i], xList[i + 1], yList[i + 1]
        dwg.add(svgwrite.shapes.Line(start=(x1, y1), end=(x2, y2), stroke=color, stroke_width=3))

    # Save the svg image
    dwg.save()
    # image_folder = filedialog.asksaveasfile(defaultextension='.svg',
    #                                         filetypes=[
    #                                             ("SVG file", ".svg")
    #                                         ])

    # Clear the canva
    canvas.delete("all")  # Efface le dessin sur le canevas
    canvas.create_text(CANVA_WIDTH / 2, CANVA_HEIGHT / 2, text="Dessin converti en SVG", font=("Helvetica", 16))


def initWindow():
    global window, canvas
    window = tkinter.Tk()
    window.title('Draw or Load Image')

    # Crée un bouton pour dessiner
    button_draw = tkinter.Button(window, text="Draw", command=lambda: {canvas.bind('<Button-1>', onClick),
                                                                       canvas.bind('<B1-Motion>', onMove),
                                                                       canvas.bind('<ButtonRelease-1>', onClickRelease)
                                                                       })
    button_draw.place(x =X_DISTANCE_BETWEEN_BUTTON,
                      y = get_next_y_button_position())

    # Clear the canva to draw a new form
    button_clear_canva = tkinter.Button(window, text="Clear canva", command=lambda: clear_canvas(canvas))
    button_clear_canva.place(x = get_next_x_button_position(button_draw),
                             y = get_next_y_button_position())

    # Crée un bouton pour convertir en SVG
    bouton_convertir_svg = tkinter.Button(window, text="Convert in SVG", command=convertir_en_svg)
    bouton_convertir_svg.place(x = get_next_x_button_position(button_clear_canva),
                               y = get_next_y_button_position())

    # Crée un bouton pour sélectionner une image
    bouton_charger_image = tkinter.Button(window, text="Select an image", command=charger_et_traiter_image)
    bouton_charger_image.place(x = get_next_x_button_position(bouton_convertir_svg),
                               y = get_next_y_button_position())

    # Button to convert the form to audio signal
    bouton_convertir_svg = tkinter.Button(window, text="Convert to audio signal", command=convert_form_to_signal)
    bouton_convertir_svg.place(x = get_next_x_button_position(bouton_charger_image),
                               y = get_next_y_button_position())

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
