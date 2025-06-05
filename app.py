from flask import Flask, render_template, request
import gspread
from google.oauth2.service_account import Credentials

app = Flask(__name__)
PASSWORD_BASIC = "admin"
PASSWORD_FULL  = "admin1"

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file("client_secret.json", scopes=scope)
client = gspread.authorize(creds)

sheet = client.open("Gestão de Stocks").sheet1

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

            alerta = ""
            if show_all:
                if validade:
                    if validade < today:
                        alerta = "fora_validade"
                    elif validade <= today + timedelta(days=5):
                        alerta = "proximo_validade"
                if stock <= 10 and not alerta:
                    alerta = "stock_baixo"
                if stock < 5:
                    alerta = "stock_vermelho"
                elif stock < 20:
                    alerta = "stock_amarelo"
            row["Alerta"] = alerta

            row["Latitude"] = float(row.get("Latitude", 0))    if show_all else None
            row["Longitude"] = float(row.get("Longitude", 0))  if show_all else None
            row["Quantidade em Stock"] = stock                if show_all else None

            filtered_rows.append(row)
        except:
            continue

    if not show_all:
        for row in filtered_rows:
            row.pop("Data de Entrada",    None)
            row.pop("Localização",        None)
            row.pop("Quantidade em Stock", None)
            row.pop("Latitude",            None)
            row.pop("Longitude",           None)

    return filtered_rows

@app.route('/', methods=['GET', 'POST'])
def index():
    admin_basic = False
    admin_full  = False
    senha_incorreta = False

    if request.method == "POST":
        senha = request.form.get("senha")
        if senha == PASSWORD_FULL:
            admin_full  = True
            admin_basic = True
        elif senha == PASSWORD_BASIC:
            admin_basic = True
        else:
            senha_incorreta = True

    items = get_data(show_all=(admin_basic or admin_full))

    return render_template(
        "index.html",
        items=items,
        senha_incorreta=senha_incorreta,
        admin_basic=admin_basic,
        admin_full=admin_full
    )

if __name__ == "__main__":
    app.run(debug=True)