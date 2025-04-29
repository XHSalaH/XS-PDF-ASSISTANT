
🎯 Objectif :
Application Tkinter pour diviser et fusionner des pages PDF en plusieurs fichiers organisés, selon des "Groupes" et "Parties" définis.

🔥 Fonctions principales :
Choix Source/Destination : Sélection du PDF source et du dossier de sortie.

Gestion par Groupes :
Un Groupe = un fichier PDF de sortie.
Un Partie = un ensemble de pages (début/fin) à extraire.

Édition facile :
Double-clic pour renommer Groupes ou Parties.
Clic simple pour modifier les numéros de pages.

Organisation :
Ajouter, Dupliquer, Déplacer, Réordonner, Supprimer Groupes/Parties.
Réinitialiser la configuration.

Traitement :

Créer les nouveaux fichiers PDF selon ta structure définie.
Gestion de l'écrasement des fichiers existants avec confirmation.
Messages de succès ou erreurs à la fin.

Confort :

Bouton pour ouvrir directement le dossier de sortie.
Thèmes ttk supportés pour meilleur look (optionnel).
Icône personnalisée pour l’application.

⚙️ Prérequis :
Python 3.7+
pypdf
ttkthemes (optionnel)
🚀 Installation rapide :
bash
Copier
Modifier
git clone <repo-url>
cd <dossier>
python -m venv venv
.\venv\Scripts\activate # (Windows) ou source venv/bin/activate (Linux/macOS)
pip install pypdf ttkthemes
python "XS PDF ASSISTANT.py"
📋 Utilisation :
Sélectionner le PDF source et le dossier de sortie.

Créer des Groupes et y ajouter des Parties (pages à extraire).
Organiser (renommer, déplacer, dupliquer, supprimer si besoin).
Lancer le Traitement 🚀.

Ouvrir le dossier de sortie ↗️.

