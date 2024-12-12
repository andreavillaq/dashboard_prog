from dash import Dash, html, dcc

app = Dash(__name__)

#html.div es un elemento de maqutacion
app.layout = html.Div([
    html.H1("Mi aplicación Dash"), #titulo
    dcc.Graph(
        id='mi-grafico',
        figure={'data': [{
            'x': [1, 2, 3],
            'y': [4, 1, 2],
            'type': 'bar',
            'name': 'SF'
            }]
          }
        )
])

if __name__ == '__main__':
    app.run(debug=True)