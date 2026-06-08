from flask import Flask, render_template, request, redirect
from datetime import datetime
import json
import os

app = Flask(__name__)
app.secret_key = "change_this_secret_key"

DATA_FILE = "data.json"


# -------------------------
# LOAD / SAVE SAFE
# -------------------------
def load_data():
    if not os.path.exists(DATA_FILE):
        return {"actuel": 0, "history": {}}

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        data = {"actuel": 0, "history": {}}

    if "history" not in data:
        data["history"] = {}

    return data


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


# -------------------------
# DATE HELPERS
# -------------------------
def month_key():
    return datetime.now().strftime("%Y-%m")


def month_label():
    return datetime.now().strftime("%B %Y")


# -------------------------
# HOME
# -------------------------
@app.route("/")
def home():
    data = load_data()
    m = month_key()

    if m not in data["history"]:
        data["history"][m] = {"revenus": {}, "depenses": {}}
        save_data(data)

    revenus = data["history"][m].get("revenus", {})
    depenses = data["history"][m].get("depenses", {})

    revenus_total = sum(revenus.values()) if isinstance(revenus, dict) else 0
    depenses_total = sum(depenses.values()) if isinstance(depenses, dict) else 0

    actuel = float(data.get("actuel", 0))

    total = actuel + revenus_total - depenses_total

    return render_template(
        "index.html",
        actuel=actuel,
        revenus_total=revenus_total,
        depenses_total=depenses_total,
        total=total,
        month=month_label()
    )


# -------------------------
# UPDATE ACTUEL
# -------------------------
@app.route("/update_actuel", methods=["POST"])
def update_actuel():
    data = load_data()

    try:
        data["actuel"] = float(request.form["actuel"])
    except:
        data["actuel"] = 0

    save_data(data)
    return redirect("/")


# -------------------------
# REVENUS
# -------------------------
@app.route("/revenus")
def revenus():
    data = load_data()
    m = month_key()

    data["history"].setdefault(m, {"revenus": {}, "depenses": {}})

    revenus = data["history"][m].get("revenus", {})

    return render_template("revenus.html", revenus=revenus)


# -------------------------
# DEPENSES
# -------------------------
@app.route("/depenses")
def depenses():
    data = load_data()
    m = month_key()

    data["history"].setdefault(m, {"revenus": {}, "depenses": {}})

    depenses = data["history"][m].get("depenses", {})

    return render_template("depenses.html", depenses=depenses)


# -------------------------
# ADD REVENUE
# -------------------------
@app.route("/add_revenu", methods=["POST"])
def add_revenu():
    data = load_data()
    m = month_key()

    data["history"].setdefault(m, {"revenus": {}, "depenses": {}})

    cat = request.form.get("categorie", "Autre")
    amount = float(request.form.get("montant", 0))

    data["history"][m]["revenus"][cat] = \
        data["history"][m]["revenus"].get(cat, 0) + amount

    save_data(data)
    return redirect("/revenus")


# -------------------------
# ADD DEPENSE
# -------------------------
@app.route("/add_depense", methods=["POST"])
def add_depense():
    data = load_data()
    m = month_key()

    data["history"].setdefault(m, {"revenus": {}, "depenses": {}})

    cat = request.form.get("categorie", "Autre")
    amount = float(request.form.get("montant", 0))

    data["history"][m]["depenses"][cat] = \
        data["history"][m]["depenses"].get(cat, 0) + amount

    save_data(data)
    return redirect("/depenses")
    
    
# -------------------------
# DELETE DEPENSE
# -------------------------
@app.route("/delete_categorie/<type>/<cat>", methods=["POST"])
def delete_categorie(type, cat):
    data = load_data()
    month = month_key()

    data["history"].setdefault(month, {"revenus": {}, "depenses": {}})

    if type == "revenus":
        data["history"][month]["revenus"].pop(cat, None)

    if type == "depenses":
        data["history"][month]["depenses"].pop(cat, None)

    save_data(data)
    return redirect(request.referrer)
    
# -------------------------
# HISTORIQUE LISTE
# -------------------------
@app.route("/historique")
def historique():
    data = load_data()

    history = []

    for k in sorted(data["history"].keys(), reverse=True):
        history.append({
            "key": k,
            "label": k
        })

    return render_template("historique.html", history=history)


# -------------------------
# DETAIL MOIS (FIXED SAFE)
# -------------------------
@app.route("/historique/<month>")
def historique_detail(month):
    data = load_data()

    mois_data = data["history"].get(month)

    # si mois inexistant → création safe
    if not mois_data:
        mois_data = {"revenus": {}, "depenses": {}}

    revenus = mois_data.get("revenus", {})
    depenses = mois_data.get("depenses", {})

    revenus_total = sum(revenus.values()) if isinstance(revenus, dict) else 0
    depenses_total = sum(depenses.values()) if isinstance(depenses, dict) else 0

    total = float(data.get("actuel", 0)) + revenus_total - depenses_total

    return render_template(
        "detail.html",
        label=month,
        revenus=revenus,
        depenses=depenses,
        total=total
    )


# -------------------------
# RUN
# -------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)