import requests
import pandas as pd
import dash
from dash import dcc, html, dash_table, Input, Output
from flask import Flask

server = Flask(__name__)  # Khởi tạo Flask server
app = dash.Dash(__name__, server=server)  # Dùng Flask làm backend

def fetch_data(url):

    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en,en-US;q=0.9,vi;q=0.8,en-GB;q=0.7",
        "cookie": "_ga=GA1.1.1069808236.1728375592; wnt.live.sid=s%3AxuichCpjboG_3CMLRCPgcAM-Tp22iIMF.p3Nae2KYcIfOfYEeUI9yobF2eS25fWPMLBnfo6X5kmw; _ga_8F96GDL1ZW=GS1.1.1741751588.8.1.1741751604.0.0.0",
        "priority": "u=1, i",
        "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Microsoft Edge";v="134"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0",
        "x-requested-with": "XMLHttpRequest"
    }

    response = requests.get(url, headers=headers)

    data = response.json()

    table = []

    for match in data["matches"]:  
        row = [
            match.get("uniqueId"),
            match.get("status")+1,
            match.get("dateScheduled"),
            match.get("dateStart"),
            match.get("roundNumber"),
            match.get("tableName"),
            match.get("length"),
            match.get("scores")[0],  
            match.get("scores")[1],
            f'{match.get("players")[0].get("name")} {match.get("players")[0].get("surname")}' if match.get("players")[0] != None else None,
            f'{match.get("players")[1].get("name")} {match.get("players")[1].get("surname")}' if match.get("players")[1] != None else None,
            match.get("players")[0].get("country").get("name") if match.get("players")[0] != None else None,
            match.get("players")[1].get("country").get("name") if match.get("players")[1] != None else None,
        ]

        table.append(row)

    return pd.DataFrame(table, columns=['uniqueId', 'status', 'dateScheduled', 'dateStart', 'roundNumber', 'tableName', 'length', 'score1', 'score2', 'player1', 'player2', 'country1', 'country2'])


def get_data():
    df = pd.concat([fetch_data("https://www.wntlivescores.com/events/european-open-pool-championship-2025/group-matches/1/1/1741640127"),
                    fetch_data("https://www.wntlivescores.com/events/european-open-pool-championship-2025/group-matches/2/1/1741640127")],
                    ignore_index=True)

    return df

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("European Pool Championship 2025"),

    dcc.Dropdown(
        id='status-filter',
        placeholder="Chọn trạng thái...",
        multi=False
    ),


    dcc.Dropdown(
        id='country-filter',
        placeholder="Chọn quốc gia...",
        multi=False
    ),


    dash_table.DataTable(
        id='table',
        columns=[],  
        data=[],
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'center'},
        style_header={'backgroundColor': 'lightgrey', 'fontWeight': 'bold'}
    )
])

@app.callback(
    [Output('table', 'data'),
     Output('table', 'columns'),
     Output('status-filter', 'options'),
     Output('country-filter', 'options')],
    [Input('status-filter', 'value'),
     Input('country-filter', 'value')]
)

def update_table(selected_status, selected_country):
    df = get_data()

    # Chọn các cột hiển thị
    selected_columns = ['dateScheduled', 'dateStart', 'status', 'roundNumber', 'tableName', 'length', 'player1', 'score1', 'score2', 'player2']

    df_filtered = df[selected_columns]

    # Lọc theo status nếu có chọn
    if selected_status:
        df_filtered = df_filtered[df_filtered["status"] == selected_status]

    # Lọc theo country nếu có chọn
    if selected_country:
        df_filtered = df_filtered[(df_filtered["country1"] == selected_country) | (df_filtered["country2"] == selected_country)]

    # Tạo options cho dropdown
    status_options = [{"label": s, "value": s} for s in df["status"].dropna().unique()]
    country_options = [{"label": c, "value": c} for c in pd.unique(df[["country1", "country2"]].dropna().values.ravel())]

    return df_filtered.to_dict('records'), [{"name": col, "id": col} for col in selected_columns], status_options, country_options

if __name__ == '__main__':
    app.run_server(debug=True)