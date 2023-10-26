import cv2
import svgwrite

# Lisez l'image depuis n'importe quel fichier image
s_img = 'images/POPS-logo.png'
img = cv2.imread(s_img)

# Conversion de l'image en niveaux de gris
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Définition du seuil de l'image en niveaux de gris
_, threshold = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

# Utilisation de la fonction findContours pour détecter les contours
contours, _ = cv2.findContours(
    threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

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
