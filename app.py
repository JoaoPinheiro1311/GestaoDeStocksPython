from flask import Flask, render_template, request
import gspread
from google.oauth2.service_account import Credentials

app = Flask(__name__)
PASSWORD = "admin"

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file("client_secret.json", scopes=scope)
client = gspread.authorize(creds)

sheet = client.open("Gestão de Stocks").sheet1

def parse_coordinates(coord_str):
    try:
        lat, lng = coord_str.replace("°", "").split(",")
        return float(lat.strip()), float(lng.strip())
    except:
        return None, None

from datetime import datetime, timedelta

def get_data(show_all=False):
    rows = sheet.get_all_records()
    filtered_rows = []
    today = datetime.today()

    for row in rows:
        try:
            validade_str = row.get("Data de Validade", "")
            validade = datetime.strptime(validade_str, "%d/%m/%Y") if validade_str else None
            stock = int(row.get("Quantidade em Stock", 0))

            if show_all or stock > 10:
                alerta = ""
                if validade:
                    if validade < today:
                        alerta = "fora_validade"
                    elif validade <= today + timedelta(days=5):
                        alerta = "proximo_validade"
                if stock <= 10 and not alerta:
                    alerta = "stock_baixo"

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