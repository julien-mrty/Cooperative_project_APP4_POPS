import cv2
import svgwrite
import tkinter as tk
from tkinter import filedialog

window = 0
canvas = 0

xList = []
yList = []

color = 'black'


def onClick(event):
    global xList, yList
    xList.append(event.x)
    yList.append(event.y)


def onMove(event):
    global xList, yList
    canvas.create_line(xList[-1], yList[-1], event.x, event.y, fill=color, width=3)
    xList.append(event.x)
    yList.append(event.y)


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

    # Enregistrez le fichier SVG
    dwg.save()

    # Affichez le fichier SVG
    canvas.delete("all")  # Efface le dessin sur le canevas
    canvas.create_text(400, 300, text="Dessin converti en SVG", font=("Helvetica", 16))


def initWindow():
    global window, canvas
    window = tk.Tk()
    window.title('Draw or Load Image')

    # Crée un bouton pour dessiner
    bouton_dessiner = tk.Button(window, text="Dessiner", command=lambda: canvas.bind('<B1-Motion>', onMove))
    bouton_dessiner.pack()

    # Crée un bouton pour convertir en SVG
    bouton_convertir_svg = tk.Button(window, text="Convertir en SVG", command=convertir_en_svg)
    bouton_convertir_svg.pack()

    # Crée un bouton pour sélectionner une image
    bouton_charger_image = tk.Button(window, text="Sélectionner une image", command=charger_et_traiter_image)
    bouton_charger_image.pack()

    canvas = tk.Canvas(window, width=800, height=600, bg='white')
    canvas.pack()
    canvas.bind('<Button-1>', onClick)

    window.mainloop()


initWindow()
