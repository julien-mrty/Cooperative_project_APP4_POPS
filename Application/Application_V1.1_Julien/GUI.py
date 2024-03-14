import tkinter
from tkinter import messagebox  # Pour les boîtes de dialogue de sélection de fichiers
import numpy as np  # Pour les opérations mathématiques
import wave  # Pour la manipulation de fichiers audio WAV
import sounddevice as sd  # Pour jouer du son
import os  # Pour manipuler le systeme
import Form_conversion

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
xList = []
yList = []

# Chemin du fichier audio de sortie
audio_name = "./audio/David.wav"
OutputFilename = './audio/Julien.wav'
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
    global drawing, xList, yList
    canva.delete('all')
    xList.clear()
    yList.clear()
    drawing = True


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


def initWindow():
    global window, canvas
    window = tkinter.Tk()
    window.title('Draw Me')

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

    # Button to convert the form to audio signal
    bouton_convertir_svg = tkinter.Button(window, text="Convert to audio signal", command=lambda: Form_conversion.convert_form_to_signal(xList, yList, canvas))
    bouton_convertir_svg.place(x = get_next_x_button_position(button_clear_canva),
                               y = get_next_y_button_position())

    # Bouton pour ouvrir la liste des fichiers audio convertis
    bouton_audio_files = tkinter.Button(window, text="Parcourir les fichiers audio", command=open_audio_files_window)
    bouton_audio_files.place(x = get_next_x_button_position(bouton_convertir_svg),
                             y = get_next_y_button_position())

    # Bouton pour sauvegarder le dessin
    bouton_sauvegarder_dessin = tkinter.Button(window, text="Sauvegarder le dessin", command=open_save_drawing_window)
    bouton_sauvegarder_dessin.place(x = get_next_x_button_position(bouton_audio_files),
                                    y = get_next_y_button_position())

    # Bouton pour visualiser les dessins sauvegardés
    bouton_visualiser_dessins = tkinter.Button(window, text="Visualiser les dessins", command=open_view_drawings_window)
    bouton_visualiser_dessins.place(x = get_next_x_button_position(bouton_sauvegarder_dessin),
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
