from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({
        "service": "Microservice Catalogue - PME Artisanale",
        "statut": "En ligne",
        "message": "Bienvenue sur l'API Cloud de produits artisanaux !"
    })

@app.route("/produits")
def get_produits():
    produits = [
        {"id": 1, "nom": "Poterie traditionnelle de Sejnane", "prix_tnd": 45},
        {"id": 2, "nom": "Tapis berbère tissé main", "prix_tnd": 320},
        {"id": 3, "nom": "Coffret huile d'olive & bois d'olivier", "prix_tnd": 60}
    ]
    return jsonify(produits)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

    