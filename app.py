import pandas as pd
import numpy as np
import plotly.express as px
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc

################ DATASET ########################
df_acq = pd.read_csv("acquisitions_update_2021.csv").replace("-", np.nan)
df_acq['Acquisition Year'] = pd.to_numeric(df_acq['Acquisition Year'], errors='coerce')
df_acq['Acquisition Price'] = pd.to_numeric(df_acq['Acquisition Price'], errors='coerce')
df_acq.rename({'Acquisition Price': 'Acquisition Price(Billions)'}, axis=1, inplace=True)

################ KPIS ##################################
total_parent_companies = df_acq['Parent Company'].nunique()
total_acquired_companies = df_acq['Acquired Company'].nunique()
total_countries = df_acq['Country'].nunique()

################## GRAFICOS #####################
def create_bar_chart(data, title, x, y, color, hide_y_labels=False):
    fig = px.bar(data, title=title, x=x, y=y, color=color, color_discrete_sequence=px.colors.sequential.Viridis)
    fig.update_layout(title_x=0.5)
    if hide_y_labels:
        fig.update_yaxes(showticklabels=False)  # Oculta las etiquetas del eje Y
    return fig

def create_histogram(data, title, x, nbins):
    fig = px.histogram(data, x=x, title=title, nbins=nbins, color_discrete_sequence=px.colors.sequential.Viridis)
    fig.update_layout(title_x=0.5)
    fig.update_yaxes(title="Companies Acquired")  # Renombrar el eje Y
    return fig

fig1 = create_histogram(df_acq, "Distribution of Acquisitions by Year", "Acquisition Year", 45)

fig2 = create_bar_chart(
    df_acq['Parent Company'].value_counts().reset_index().rename({'count': 'Acquisitions'}, axis=1),
    "Companies with Most Acquisitions", "Parent Company", "Acquisitions", "Parent Company")

fig3 = create_bar_chart(
    df_acq['Business'].value_counts().reset_index().head(25).rename({'count': 'Number of Companies'}, axis=1),
    "Businesses Acquired", "Number of Companies", "Business", "Business", hide_y_labels=True)

fig4 = create_bar_chart(
    df_acq['Derived Products'].value_counts().reset_index().head(25).rename({'count': 'Number of Companies'}, axis=1),
    "Products Derived from Acquisitions", "Number of Companies", "Derived Products", "Derived Products", hide_y_labels=True)

fig5 = create_bar_chart(
    df_acq['Country'].value_counts().reset_index().head(25).rename({'count': 'Number of Companies'}, axis=1),
    "Acquisitions by Country", "Number of Companies", "Country", "Country", hide_y_labels=True)

fig6 = create_bar_chart(
    df_acq.sort_values("Acquisition Price(Billions)", ascending=False).head(10),
    "Most Expensive Acquisitions", "Acquired Company", "Acquisition Price(Billions)", "Acquired Company")

##################### APP ###############################
app = Dash(
    __name__,
    title="Acquisitions Insights",
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined&family=Roboto:wght@400;700&display=swap",
    ],
)

##################### CALLBACKS ##################################
@app.callback(
    [Output("fig1_filtered", "figure"),
     Output("fig5_filtered", "figure"),
     Output("fig6_filtered", "figure")],
    [Input("pc_acq", "value")]
)
def update_figures(selected_company):
    filtered_df = df_acq[df_acq['Parent Company'] == selected_company]
    
    # Verificar si el DataFrame está vacío o si no hay datos en el gráfico de países
    if filtered_df.empty or filtered_df['Country'].isna().all():
        fig5_filtered = {
            "layout": {
                "xaxis": {"visible": False},
                "yaxis": {"visible": False},
                "annotations": [
                    {
                        "text": "Please, note that countries of acquisitions were not disclosed by this Parent Company",
                        "xref": "paper",
                        "yref": "paper",
                        "showarrow": False,
                        "font": {"size": 16}
                    }
                ]
            }
        }
    else:
        fig5_filtered = create_bar_chart(
            filtered_df['Country'].value_counts().reset_index().rename(
                {'count': 'Number of Companies'}, axis=1
            ),
            f"Acquisitions by Country for {selected_company}",
            "Number of Companies", "Country", "Country", hide_y_labels=True 
        )
    
    return (
        create_histogram(
            filtered_df,
            f"Acquisitions by Year for {selected_company}",
            "Acquisition Year",
            45
        ),
        fig5_filtered,
        create_bar_chart(
            filtered_df.sort_values("Acquisition Price(Billions)", ascending=False).head(10),
            f"Most Expensive Acquisitions by {selected_company}",
            "Acquired Company", "Acquisition Price(Billions)", "Acquired Company"
        )
    )
##################### LAYOUT #####################################
app.layout = html.Div(
    style={"background-color": "#f8f9fa"},
    children=[
        dbc.NavbarSimple(
            brand="Top Companies Acquisitions Analysis",
            brand_href="/",
            color="dark",
            dark=True,
        ),
        dcc.Tabs([
            dcc.Tab(label='Acquisitions Insights', children=[
                dbc.Container([
                    dbc.Row([
                        dbc.Col(html.Div([html.H2(total_parent_companies, className="text-center"), html.H4("Parent Companies", className="text-center")], className="p-3 bg-light rounded-3 shadow-sm"), md=4),
                        dbc.Col(html.Div([html.H2(total_acquired_companies, className="text-center"), html.H4("Acquired Companies", className="text-center")], className="p-3 bg-light rounded-3 shadow-sm"), md=4),
                        dbc.Col(html.Div([html.H2(total_countries, className="text-center"), html.H4("Countries of Acquisitions", className="text-center")], className="p-3 bg-light rounded-3 shadow-sm"), md=4),
                    ], className="mb-4"),
                    dbc.Row([dbc.Col(dcc.Graph(figure=fig1), md=6), dbc.Col(dcc.Graph(figure=fig2), md=6)], className="mb-4"),
                    dbc.Row([dbc.Col(dcc.Graph(figure=fig3), md=6), dbc.Col(dcc.Graph(figure=fig4), md=6)], className="mb-4"),
                    dbc.Row([dbc.Col(dcc.Graph(figure=fig5), md=6), dbc.Col(dcc.Graph(figure=fig6), md=6)], className="mb-4"),
                ], fluid=True, className="py-4"),
            ]),
            dcc.Tab(label='Analysis per Company', children=[
                dbc.Container([
                    html.Div([html.H3("Filter by Parent Company"), dcc.Dropdown(id="pc_acq", options=[{"label": c, "value": c} for c in df_acq['Parent Company'].dropna().unique()], value=df_acq['Parent Company'].dropna().unique()[0], clearable=False)], className="mb-4"),
                    dbc.Row([dbc.Col(dcc.Graph(id="fig1_filtered"), md=12)], className="mb-4"),
                    dbc.Row([dbc.Col(dcc.Graph(id="fig5_filtered"), md=6), dbc.Col(dcc.Graph(id="fig6_filtered"), md=6)]),
                ], fluid=True, className="py-4"),
            ]),
        ])
    ]
)

##################### RUN APP ####################################
if __name__ == '__main__':
    app.run_server(debug=True)
