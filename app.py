import pandas as pd
import numpy as np
import plotly.express as px
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc

################ DATASET ########################
df_acq = pd.read_csv("acquisitions_update_2021.csv")
df_acq = df_acq.replace("-", np.nan)
df_acq['Acquisition Year'] = pd.to_numeric(df_acq['Acquisition Year'], errors='coerce')
df_acq['Acquisition Price'] = pd.to_numeric(df_acq['Acquisition Price'], errors='coerce')
df_acq = df_acq.rename({'Acquisition Price': 'Acquisition Price(Billions)'}, axis=1)

################ KPIS ##################################
total_parent_companies = df_acq['Parent Company'].nunique()
total_acquired_companies = df_acq['Acquired Company'].nunique()

################## GRAFICOS #####################
fig1 = px.histogram(
    df_acq,
    x="Acquisition Year",
    title="Distribution of Acquisitions by Year",
    labels={"Acquisition Year": "Year of Acquisition"},
    nbins=45,
    color_discrete_sequence=["#7b86ed"], 
)
fig1.update_layout(title_x=0.5)

companies = df_acq['Parent Company'].value_counts()
companies_df = companies.to_frame().reset_index()
companies_df = companies_df.rename({'count': 'Acquisitions'}, axis=1)
fig2 = px.bar(
    companies_df, 
    title="Companies with Most Acquisitions", 
    x='Parent Company', 
    y='Acquisitions', 
    color='Parent Company', 
    color_discrete_sequence=px.colors.sequential.Viridis,  # Usar una paleta bonita
)
fig2.update_layout(title_x=0.5)

business_types = df_acq["Business"].value_counts().reset_index()
business_types = business_types.rename({"count": "Number of Companies"}, axis=1)
business_types = business_types.head(25)
fig3 = px.bar(
    business_types, 
    title="Businesses Acquired", 
    x='Number of Companies', 
    y='Business', 
    color='Business',
    color_discrete_sequence=px.colors.sequential.Viridis,  # Colores secuenciales agradables
)
fig3.update_layout(title_x=0.5)

new_products = df_acq["Derived Products"].value_counts().reset_index()
new_products = new_products.rename({"count": "Number of Companies"}, axis=1)
new_products = new_products.head(25)
fig4 = px.bar(
    new_products, 
    title="Products Derived from Acquisitions", 
    x='Number of Companies', 
    y='Derived Products', 
    color='Derived Products', 
    color_discrete_sequence=px.colors.sequential.Viridis,
)
fig4.update_layout(title_x=0.5)

countries = df_acq["Country"].value_counts().reset_index()
countries = countries.rename({"count": "Number of Companies"}, axis=1)
countries = countries.head(25)
fig5 = px.bar(
    countries, 
    title="Acquisitions by Country", 
    x='Number of Companies', 
    y='Country', 
    color='Country', 
    color_discrete_sequence=px.colors.qualitative.Set2, 
)
fig5.update_layout(title_x=0.5)

most_valuable = df_acq.sort_values("Acquisition Price(Billions)", ascending=False).head(10)
fig6 = px.bar(
    most_valuable, 
    title="Most Expensive Acquisitions", 
    x='Acquired Company', 
    y='Acquisition Price(Billions)', 
    color='Acquired Company', 
    hover_data=['Parent Company'],
    color_discrete_sequence=px.colors.sequential.Cividis,
)
fig6.update_layout(title_x=0.5)

##################### INICIAR APP ###############################
app = Dash(
    __name__,
    title="Acquisitions Insights",
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200",  # Icons
        "https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,100;0,300;0,400;0,500;0,700;0,900;1,100;1,300;1,400;1,500;1,700;1,900&display=swap",  # Font
    ],
)

##################### WIDGETS ####################################
parent_company = df_acq['Parent Company'].dropna().unique()
pc_acq = dcc.Dropdown(
    id="pc_acq",
    options=[{"label": company, "value": company} for company in parent_company],
    value=parent_company[0],
    clearable=False
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

    # Figura 1 (Distribución por año)
    fig1_filtered = px.histogram(
        filtered_df,
        x="Acquisition Year",
        title=f"Acquisitions by Year for {selected_company}",
        labels={"Acquisition Year": "Year of Acquisition"},
        nbins=45,
        color_discrete_sequence=["#007bff"],
    )
    fig1_filtered.update_layout(title_x=0.5)

    # Figura 5 (Adquisiciones por país)
    countries = filtered_df["Country"].value_counts().reset_index()
    countries = countries.rename({"count": "Number of Companies"}, axis=1)
    fig5_filtered = px.bar(
        countries,
        title=f"Acquisitions by Country for {selected_company}",
        x='Number of Companies',
        y='Country',
        color='Country',
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig5_filtered.update_layout(title_x=0.5)

    # Figura 6 (Adquisiciones más caras)
    most_valuable = filtered_df.sort_values("Acquisition Price(Billions)", ascending=False).head(10)
    fig6_filtered = px.bar(
        most_valuable,
        title=f"Most Expensive Acquisitions by {selected_company}",
        x='Acquired Company',
        y='Acquisition Price(Billions)',
        color='Acquired Company',
        color_discrete_sequence=px.colors.sequential.Cividis,
    )
    fig6_filtered.update_layout(title_x=0.5)

    return fig1_filtered, fig5_filtered, fig6_filtered

##################### LAYOUT #####################################
app.layout = html.Div([
    html.H1("Acquisitions Insights", className="text-center fw-bold m-2", style={"text-align": "center", "color": "#000", "padding-bottom": "30px"}),

    dcc.Tabs([dcc.Tab(label='Acquisitions Insights', children=[html.Div([
        # KPIs
        html.Div([
            html.Div([
                html.H4("Total Parent Companies"),
                html.H2(total_parent_companies, id="total-parent-kpi", style={"color": "#007bff"})
            ], className="metric-box"),

            html.Div([
                html.H4("Total Acquired Companies"),
                html.H2(total_acquired_companies, id="total-acquired-kpi", style={"color": "#28a745"})
            ], className="metric-box"),
        ], className="kpi-container", style={"display": "flex", "justify-content": "space-around", "padding": "20px"}),

        # Gráficos
        html.Div([dcc.Graph(figure=fig) for fig in [fig1, fig2, fig3, fig4, fig5, fig6]], style={"padding": "20px"}),
    ]),
]),

        dcc.Tab(label='Analysis per Company', children=[
            html.Div([
                html.H3("Filter by Parent Company"),
                pc_acq,  # Dropdown para seleccionar la compañía
            ], style={"padding": "20px"}),

            html.Div([dcc.Graph(id="fig1_filtered")], style={"padding": "20px"}),
            html.Div([dcc.Graph(id="fig5_filtered")], style={"padding": "20px"}),
            html.Div([dcc.Graph(id="fig6_filtered")], style={"padding": "20px"}),
        ])
    ])
])

if __name__ == '__main__':
    app.run_server(debug=True)