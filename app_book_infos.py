# Importation des bibliothèques nécessaires
import tkinter as tk
from tkinter import messagebox, font
import requests
import xml.etree.ElementTree as ET

# Fonction pour obtenir le PPN (Pica Production Number) depuis un ISBN
def obtenir_ppn_depuis_isbn(isbn):
    # Construction de l'URL pour la requête à l'API Sudoc
    url = f"https://www.sudoc.fr/services/isbn2ppn/{isbn}"
    # Envoi de la requête HTTP
    response = requests.get(url)
    # Vérification du code de réponse HTTP
    if response.status_code != 200:
        return None

    # Analyse du contenu XML de la réponse
    tree = ET.fromstring(response.content)
    # Recherche de l'élément PPN dans le document XML
    ppn = tree.find('.//result/ppn')
    # Retourne le texte du PPN s'il est trouvé, sinon None
    return ppn.text if ppn is not None else None

# Fonction pour obtenir les métadonnées depuis un PPN
def obtenir_metadonnees_depuis_ppn(ppn):
    # Construction de l'URL pour la requête à l'API Sudoc
    url = f"http://www.sudoc.fr/{ppn}.rdf"
    try:
        # Envoi de la requête HTTP avec un délai d'attente
        response = requests.get(url, timeout=30)
        # Vérification du code de réponse HTTP
        if response.status_code != 200:
            return None

        # Analyse du contenu RDF/XML de la réponse
        tree = ET.fromstring(response.content)
        # Extraction des différents éléments du RDF (titre, auteur, éditeur, date)
        titre_element = tree.find('.//{http://purl.org/dc/elements/1.1/}title')
        titre = titre_element.text.split('/')[0].strip() if titre_element is not None and titre_element.text is not None else "Inconnu"
        auteur = tree.find('.//{http://xmlns.com/foaf/0.1/}name')
        editeur = tree.find('.//{http://purl.org/dc/elements/1.1/}publisher')
        date = tree.find('.//{http://purl.org/dc/elements/1.1/}date')

        # Création d'un dictionnaire contenant les informations extraites
        infos = {
            "titre": titre,
            "auteur": auteur.text if auteur is not None else "Inconnu",
            "editeur": editeur.text if editeur is not None else "Inconnu",
            "date": date.text if date is not None else "Inconnue"
        }

        return infos
    except requests.exceptions.Timeout:
        # Gestion de l'exception pour un délai d'attente dépassé
        print("La requête a dépassé le délai d'attente.")
        return None
    except Exception as e:
        # Gestion des autres exceptions
        print(f"Une erreur est survenue : {e}")
        return None

# Initialisation de l'interface graphique Tkinter
root = tk.Tk()
root.title("Application de Métadonnées de Livre")

# Définir une icône pour la fenêtre (remplacez 'icone-livre.ico' par le chemin de votre icône)
root.iconbitmap('icone-livre.ico')

# Définir une police plus grande
police_grande = font.Font(family='Helvetica', size=12, weight='bold')

# Créer et ajouter une étiquette avec une police plus grande
label = tk.Label(root, text="Entrez un numéro ISBN:", font=police_grande)
label.pack(pady=10)  # Ajouter un peu d'espace vertical

# Créer et ajouter un champ de saisie avec une police plus grande et une largeur augmentée
isbn_entry = tk.Entry(root, font=police_grande, width=30)  # Largeur ajustée à 30 caractères
isbn_entry.pack(pady=5)  # Ajouter un peu d'espace vertical


# Fonction appelée lors du clic sur le bouton de recherche
def on_search():
    # Obtention de l'ISBN saisi
    isbn = isbn_entry.get()
    # Recherche du PPN à partir de l'ISBN
    ppn = obtenir_ppn_depuis_isbn(isbn)
    if ppn:
        # Recherche des métadonnées à partir du PPN
        infos = obtenir_metadonnees_depuis_ppn(ppn)
        if infos:
            # Formatage du texte des résultats
            result_text = f"Titre: {infos['titre']}\nAuteur: {infos['auteur']}\nÉditeur: {infos['editeur']}\nDate: {infos['date']}"
        else:
            result_text = "Aucune métadonnée trouvée pour ce PPN."
    else:
        result_text = "Aucun PPN trouvé pour cet ISBN."
    # Affichage des résultats dans une messagebox
    messagebox.showinfo("Résultats", result_text)

# Créer et ajouter un bouton de recherche avec une police plus grande
search_button = tk.Button(root, text="Rechercher", command=on_search, font=police_grande)
search_button.pack(pady=10)  # Ajouter un peu d'espace vertical

# Démarrage de la boucle principale de l'interface graphique
root.mainloop()
