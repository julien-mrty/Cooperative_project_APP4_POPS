import tkinter as tk

# Fonction appelée lorsque le bouton est cliqué
def afficher_message():
    label.config(text="Bonjour, Tkinter!")

# Crée une fenêtre principale
fenetre = tk.Tk()
fenetre.title("Exemple Tkinter")

# Crée un widget Label pour afficher du texte
label = tk.Label(fenetre, text="Cliquez sur le bouton")
label.pack()

# Crée un bouton
bouton = tk.Button(fenetre, text="Cliquez moi!", command=afficher_message)
bouton.pack()

# Lance la boucle principale de l'application
fenetre.mainloop()