# Importation des bibliothèques nécessaires
import tkinter
from tkinter import filedialog, messagebox  # Pour les boîtes de dialogue de sélection de fichiers
import cv2  # OpenCV pour le traitement d'images
import numpy as np  # Pour les opérations mathématiques
import svgwrite  # Pour créer des fichiers SVG
import wave  # Pour la manipulation de fichiers audio WAV
import struct  # Pour manipuler des données binaires
import sounddevice as sd  # Pour jouer du son
import os  # Pour manipuler le systeme

# Variables globales pour l'audio
playing_audio = False
current_audio_file = None
audio_data = None
saved_drawings = []

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

# Coordonnés de la forme
drawing_segments = []

# Fonction appelée lors d'un clic de souris
def onClick(event):
    global drawing_segments
    # Commence un nouveau segment de dessin
    drawing_segments.append([event.x, event.y])

# Fonction appelée lors d'un mouvement de souris
def onMove(event):
    global drawing_segments
    # Ajoute les coordonnées au segment en cours
    if drawing_segments:
        drawing_segments[-1].extend([event.x, event.y])
        canvas.create_line(drawing_segments[-1], fill=color, width=3)

# Fonction appelée lors du relâchement du clic de souris
def onClickRelease(event):
    # Fin du segment de dessin en cours
    pass

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

# Fonction pour interpoler les points, lisser les transitions entre les points du dessin
def interpolate_points(x_points, y_points, interpolation_factor):
    """
    Interpolates points in the drawing to smooth out the signal.

    Parameters:
        x_points (list): List of x coordinates.
        y_points (list): List of y coordinates.
        interpolation_factor (int): Factor for interpolation (1 = no interpolation).

    Returns:
        Tuple of interpolated x and y points.
    """
    interpolated_x = []
    interpolated_y = []

    for i in range(len(x_points) - 1):
        x0, y0 = x_points[i], y_points[i]
        x1, y1 = x_points[i + 1], y_points[i + 1]

        # Add the original point
        interpolated_x.append(x0)
        interpolated_y.append(y0)

        # Interpolate between the original points
        for j in range(1, interpolation_factor):
            t = j / interpolation_factor
            interpolated_x.append(x0 + t * (x1 - x0))
            interpolated_y.append(y0 + t * (y1 - y0))

    # Add the last point
    interpolated_x.append(x_points[-1])
    interpolated_y.append(y_points[-1])

    return interpolated_x, interpolated_y

# Fonction pour convertir le dessin en signal audio
def convert_form_to_signal():
    global xList, yList, framerate, audio_name, amplitude

    # Interpoler les points du dessin
    interpolated_x, interpolated_y = interpolate_points(xList, yList, interpolation_factor=5)

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
    canvas.create_text(CANVA_WIDTH / 2, CANVA_HEIGHT / 2, text="La forme est convertie avec succès. Le fichier WAV est prêt !", font=("Arial", 16))

    print("Le fichier WAV est prêt.")



# Fonction pour ouvrir la fenêtre de liste des fichiers audio
def open_audio_files_window():
    global playing_audio
    audio_files_window = tkinter.Toplevel(window)
    audio_files_window.title("Liste des fichiers audio convertis en dessin")

    # Trouver tous les fichiers audio dans le dossier "audio"
    audio_files = [f for f in os.listdir("../audio") if f.endswith(".wav")]

    # Fonction pour lire ou arrêter un fichier audio sélectionné
    def toggle_audio(audio_file):
        global playing_audio, current_audio_file, audio_data

        if playing_audio and current_audio_file == audio_file:
            sd.stop()
            playing_audio = False
        else:
            try:
                wf = wave.open(f"./audio/{audio_file}", 'rb')
                frames = wf.readframes(wf.getnframes())
                audio_data = np.frombuffer(frames, dtype=np.int16)
                sd.play(audio_data, wf.getframerate())
                current_audio_file = audio_file
                playing_audio = True
                wf.close()
            except Exception as e:
                print(f"Erreur lors de la lecture du fichier audio : {e}")

    # Fonction pour créer les boutons de lecture pour chaque fichier audio
    def create_play_buttons():
        for audio_file in audio_files:
            play_button = tkinter.Button(audio_files_window, text=audio_file, command=lambda af=audio_file: toggle_audio(af))
            play_button.pack()

    # Création des boutons pour chaque fichier audio
    create_play_buttons()

    # Fonction pour arrêter l'audio lorsque la fenêtre est fermée
    def on_close():
        global playing_audio
        if playing_audio:
            sd.stop()
            playing_audio = False
        audio_files_window.destroy()

    audio_files_window.protocol("WM_DELETE_WINDOW", on_close)

# Fonction pour ouvrir la fenêtre de sauvegarde de dessin
def open_save_drawing_window():
    save_window = tkinter.Toplevel(window)
    save_window.title("Sauvegarder le dessin")

    def save_drawing():
        global xList, yList, saved_drawings
        drawing_name = entry_drawing_name.get()
        if drawing_name:
            saved_drawings.append((drawing_name, xList.copy(), yList.copy()))
            messagebox.showinfo("Sauvegarde réussie", "Le dessin a été sauvegardé avec succès.")
            save_window.destroy()
        else:
            messagebox.showerror("Erreur de sauvegarde", "Veuillez entrer un nom pour le dessin.")

    label_drawing_name = tkinter.Label(save_window, text="Nom du dessin:")
    label_drawing_name.pack()

    entry_drawing_name = tkinter.Entry(save_window, width=30)
    entry_drawing_name.pack()

    button_save_drawing = tkinter.Button(save_window, text="Sauvegarder", command=save_drawing)
    button_save_drawing.pack()


# Fonction pour ouvrir la fenêtre de visualisation des dessins sauvegardés
def open_view_drawings_window():
    view_window = tkinter.Toplevel(window)
    view_window.title("Dessins sauvegardés")

    def view_drawing(drawing):
        nonlocal view_window
        canvas_view = tkinter.Canvas(view_window, width=CANVA_WIDTH, height=CANVA_HEIGHT, bg='white')
        canvas_view.pack()

        x_points, y_points = drawing[1], drawing[2]
        for i in range(len(x_points) - 1):
            canvas_view.create_line(x_points[i], y_points[i], x_points[i + 1], y_points[i + 1], fill='black', width=3)

    for drawing in saved_drawings:
        button_view_drawing = tkinter.Button(view_window, text=drawing[0], command=lambda d=drawing: view_drawing(d))
        button_view_drawing.pack()


# Fonction pour initialiser la fenêtre principale
def initWindow():
    global window, canvas
    window = tkinter.Tk()
    window.title('DrawMe')

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

    # Bouton pour ouvrir la liste des fichiers audio convertis
    bouton_audio_files = tkinter.Button(window, text="Parcourir les fichiers audio", command=open_audio_files_window)
    bouton_audio_files.place(x=get_next_x_button_position(bouton_convertir_audio), y=get_next_y_button_position())

    # Bouton pour sauvegarder le dessin
    bouton_sauvegarder_dessin = tkinter.Button(window, text="Sauvegarder le dessin", command=open_save_drawing_window)
    bouton_sauvegarder_dessin.place(x=get_next_x_button_position(bouton_convertir_audio),
                                    y=get_next_y_button_position())

    # Bouton pour visualiser les dessins sauvegardés
    bouton_visualiser_dessins = tkinter.Button(window, text="Visualiser les dessins", command=open_view_drawings_window)
    bouton_visualiser_dessins.place(x=get_next_x_button_position(bouton_sauvegarder_dessin),
                                    y=get_next_y_button_position())

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
