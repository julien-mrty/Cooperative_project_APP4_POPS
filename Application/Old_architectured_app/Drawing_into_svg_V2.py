import cv2
import svgwrite
import tkinter
from tkinter import filedialog
import soundfile as sf
import numpy as np
import sounddevice as sd

height = 600
width = 800

drawing = True

window = 0
canvas = 0

xList = []
yList = []

color = 'black'

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

def clear_canvas(canvas):
    global drawing
    canvas.delete('all')
    drawing = True

def moduler_signal_audio():
    global xList, yList

    # Normalisez les coordonnées du dessin entre 0 et 1
    x_normalized = (np.array(xList) - min(xList)) / (max(xList) - min(xList))
    y_normalized = (np.array(yList) - min(yList)) / (max(yList) - min(yList))

    # Créez un signal audio en fonction des coordonnées normalisées
    signal_audio = x_normalized + 1j * y_normalized

    # Modulation du signal audio
    modulation_frequency = 440  # Fréquence de modulation en Hz
    t = np.arange(len(signal_audio)) / 44100.0  # Échantillonnage à 44.1 kHz
    carrier_wave = np.sin(2 * np.pi * modulation_frequency * t)
    modulated_signal = np.real(signal_audio * carrier_wave)

    # Enregistrez le signal audio dans un fichier WAV dans le répertoire spécifié
    output_directory = "./"  # chemin du répertoire
    output_filename = "signal_audio.wav"
    output_path = f"{output_directory}/{output_filename}"

    sf.write(output_path, modulated_signal, 44100)

    # Jouez le signal modulé
    sd.play(modulated_signal, samplerate=44100)
    sd.wait()

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
    dwg = svgwrite.Drawing('dessin.svg', profile='tiny', size=(800, 600))

    # Dessiner les lignes du dessin en SVG
    for i in range(len(xList) - 1):
        x1, y1, x2, y2 = xList[i], yList[i], xList[i + 1], yList[i + 1]
        dwg.add(svgwrite.shapes.Line(start=(x1, y1), end=(x2, y2), stroke=color, stroke_width=3))

    # Moduler le signal audio
    moduler_signal_audio()

    # Save the file
    dwg.save()
    # image_folder = filedialog.asksaveasfile(defaultextension='.svg',
    #                                         filetypes=[
    #                                             ("SVG file", ".svg")
    #                                         ])

    # Affichez le fichier SVG
    canvas.delete("all")  # Efface le dessin sur le canevas
    canvas.create_text(400, 300, text="Dessin converti en SVG", font=("Helvetica", 16))


def initWindow():
    global window, canvas
    window = tkinter.Tk()
    window.title('Draw or Load Image')

    # Crée un bouton pour dessiner
    button_draw = tkinter.Button(window, text="Draw", command=lambda: {canvas.bind('<Button-1>', onClick),
                                                                       canvas.bind('<B1-Motion>', onMove),
                                                                       canvas.bind('<ButtonRelease-1>', onClickRelease)
                                                                       })
    button_draw.place(x=20, y=5)

    # Clear the canva to draw a new form
    button_clear_canva = tkinter.Button(window, text="Clear canva", command=lambda: clear_canvas(canvas))
    button_clear_canva.place(x=80, y=5)

    # Crée un bouton pour convertir en SVG
    bouton_convertir_svg = tkinter.Button(window, text="Convert in SVG", command=convertir_en_svg)
    bouton_convertir_svg.place(x=180, y=5)

    # Crée un bouton pour sélectionner une image
    bouton_charger_image = tkinter.Button(window, text="Select an image", command=charger_et_traiter_image)
    bouton_charger_image.place(x=300, y=5)

    canvas = tkinter.Canvas(window, width=800, height=600, bg='white')
    canvas.place(x=10, y=40)
    window.geometry("820x650")

    window.mainloop()

initWindow()