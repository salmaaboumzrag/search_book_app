# Importation des bibliothèques nécessaires pour effectuer des requêtes HTTP et analyser des données XML.
import requests
import xml.etree.ElementTree as ET

# Fonction pour obtenir le PPN (Pica Production Number) d'un livre à partir de son ISBN
def obtenir_ppn_depuis_isbn(isbn):
    # Construction de l'URL de l'API Sudoc pour obtenir le PPN à partir de l'ISBN
    url = f"https://www.sudoc.fr/services/isbn2ppn/{isbn}"
    # Envoi de la requête HTTP à l'API
    response = requests.get(url)
    # Vérification si la requête a réussi (code HTTP 200)
    if response.status_code != 200:
        return None

    # Analyse du contenu XML de la réponse
    tree = ET.fromstring(response.content)
    # Recherche du PPN dans le contenu XML
    ppn = tree.find('.//result/ppn')
    # Retourne le texte du PPN s'il est trouvé, sinon retourne None
    return ppn.text if ppn is not None else None

# Fonction pour obtenir les métadonnées d'un livre à partir de son PPN
def obtenir_metadonnees_depuis_ppn(ppn):
    # Construction de l'URL de l'API Sudoc pour obtenir les métadonnées RDF à partir du PPN
    url = f"http://www.sudoc.fr/{ppn}.rdf"
    try:
        # Envoi de la requête HTTP à l'API avec un délai d'attente
        response = requests.get(url, timeout=30)
        # Vérification si la requête a réussi (code HTTP 200)
        if response.status_code != 200:
            return None

        # Analyse du contenu RDF/XML de la réponse
        tree = ET.fromstring(response.content)
        # Extraction des informations (titre, auteur, éditeur, date) du contenu RDF/XML
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

        # Retourne le dictionnaire des informations
        return infos
    except requests.exceptions.Timeout:
        # Gestion de l'exception en cas de dépassement du délai d'attente de la requête
        print("La requête a dépassé le délai d'attente.")
        return None
    except Exception as e:
        # Gestion des autres exceptions qui pourraient survenir
        print(f"Une erreur est survenue : {e}")
        return None

# Script principal
# Demande à l'utilisateur d'entrer un numéro ISBN
isbn = input("Entrez un numéro ISBN: ")
# Obtention du PPN à partir de l'ISBN
ppn = obtenir_ppn_depuis_isbn(isbn)
# Vérification et affichage des résultats
if ppn:
    print(f"PPN trouvé : {ppn}")
    infos = obtenir_metadonnees_depuis_ppn(ppn)
    if infos:
        print(f"Titre du livre : {infos['titre']}")
        print(f"Auteur : {infos['auteur']}")
        print(f"Éditeur : {infos['editeur']}")
        print(f"Date : {infos['date']}")
    else:
        print("Aucune métadonnée trouvée pour ce PPN.")
else:
    print("Aucun PPN trouvé pour cet ISBN.")
