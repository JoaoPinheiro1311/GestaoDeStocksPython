from flask import Flask, render_template, request
import gspread
from google.oauth2.service_account import Credentials

app = Flask(__name__)
PASSWORD = "admin"

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file("client_secret.json", scopes=scope)
client = gspread.authorize(creds)

sheet = client.open("Gestão de Stocks").sheet1

from datetime import datetime, timedelta

def get_data(show_all=False):
    rows = sheet.get_all_records()
    filtered_rows = []

    for row in rows:
        try:
            stock = int(row.get("Quantidade em Stock", 0))
            alerta = ""

            # Nova lógica de cores:
            if stock < 5:
                alerta = "stock_vermelho"
            elif stock < 20:
                alerta = "stock_amarelo"

            row["Alerta"] = alerta
            row["Latitude"] = float(row.get("Latitude", 0))
            row["Longitude"] = float(row.get("Longitude", 0))
            filtered_rows.append(row)
        except:
            continue

    if not show_all:
        for row in filtered_rows:
            row.pop("Data de Entrada", None)
            row.pop("Localização", None)
            row.pop("Quantidade em Stock", None)
            row.pop("Latitude", None)
            row.pop("Longitude", None)

    return filtered_rows

@app.route('/')
def index():
    items = get_data(show_all=False)
    return render_template("index.html", items=items, senha_incorreta=False, admin=False)

@app.route('/admin', methods=['POST'])
def admin():
    senha = request.form.get("senha")
    if senha == PASSWORD:
        items = get_data(show_all=True)
        return render_template("index.html", items=items, senha_incorreta=False, admin=True)
    else:
        items = get_data(show_all=False)
        return render_template("index.html", items=items, senha_incorreta=True, admin=False)

if __name__ == "__main__":
    app.run(debug=True)
