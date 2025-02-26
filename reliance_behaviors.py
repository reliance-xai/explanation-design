import pandas as pd
import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.express as px

# Charger les données
file_path = "data_transformed.xlsx"
df = pd.read_excel(file_path, engine="openpyxl")

# Renommer la colonne "Ref." en "Ref" si elle est mal formatée
df.rename(columns={"Ref.": "Ref"}, inplace=True)

# Transformer les données
df_melted = df.melt(
    id_vars=[
        "Ref",  
        "Explanation Modality",
        "Explanation Format",
        "AI Model",
        "Application Domain",
        "XAI Type",
        "XAI Technique",
        "XAI Method",
        "Decision-Making Task",
        "Audience",
    ],
    value_vars=["Over-reliance", "Under-reliance", "Appropriate reliance"],
    var_name="Reliance Type",
    value_name="Reliance Effect",
)

# Supprimer les valeurs NaN
df_melted = df_melted.dropna(subset=["Reliance Effect"])

# Configurer l'application Dash
app = dash.Dash(__name__)

def create_dropdown_options(column_name):
    """Créer les options pour les menus déroulants à partir des valeurs uniques de la colonne."""
    unique_values = df_melted[column_name].dropna().unique()
    return [{'label': value, 'value': value} for value in unique_values] if len(unique_values) > 0 else []

# Interface utilisateur de l'application
app.layout = html.Div([
    html.H1("Impact of Explanation Design on User Reliance", style={'textAlign': 'center'}),

    # Filtres interactifs
    html.Div([
        html.Label("Select Explanation Modality:"),
        dcc.Dropdown(id='modality-dropdown', options=create_dropdown_options("Explanation Modality"), multi=True)
    ], style={'width': '32%', 'display': 'inline-block'}),
    
    html.Div([
        html.Label("Select Explanation Format:"),
        dcc.Dropdown(id='format-dropdown', options=create_dropdown_options("Explanation Format"), multi=True)
    ], style={'width': '32%', 'display': 'inline-block'}),

    html.Div([
        html.Label("Select Task:"),
        dcc.Dropdown(id='task-dropdown', options=create_dropdown_options("Decision-Making Task"), multi=True)
    ], style={'width': '32%', 'display': 'inline-block'}),

    html.Div([
        html.Label("Select Domain:"),
        dcc.Dropdown(id='domain-dropdown', options=create_dropdown_options("Application Domain"), multi=True)
    ], style={'width': '32%', 'display': 'inline-block'}),

    html.Div([
        html.Label("Select XAI Type:"),
        dcc.Dropdown(id='xai-type-dropdown', options=create_dropdown_options("XAI Type"), multi=True)
    ], style={'width': '32%', 'display': 'inline-block'}),

    html.Div([
        html.Label("Select XAI Technique:"),
        dcc.Dropdown(id='xai-technique-dropdown', options=create_dropdown_options("XAI Technique"), multi=True)
    ], style={'width': '32%', 'display': 'inline-block'}),

    html.Div([
        html.Label("Select XAI Method:"),
        dcc.Dropdown(id='xai-method-dropdown', options=create_dropdown_options("XAI Method"), multi=True)
    ], style={'width': '32%', 'display': 'inline-block'}),

    html.Div([
        html.Label("Select Audience:"),
        dcc.Dropdown(id='audience-dropdown', options=create_dropdown_options("Audience"), multi=True)
    ], style={'width': '32%', 'display': 'inline-block'}),

    html.Div([
        html.Label("Select AI Model:"),
        dcc.Dropdown(id='ai-model-dropdown', options=create_dropdown_options("AI Model"), multi=True)
    ], style={'width': '32%', 'display': 'inline-block'}),

    html.Div([
        html.Label("Select Reliance Type:"),
        dcc.Dropdown(
            id='reliance-type-dropdown',
            options=[
                {'label': 'Over-reliance', 'value': 'Over-reliance'},
                {'label': 'Under-reliance', 'value': 'Under-reliance'},
                {'label': 'Appropriate reliance', 'value': 'Appropriate reliance'}
            ],
            multi=True
        )
    ], style={'width': '32%', 'display': 'inline-block'}),

    html.Div([
        html.Label("Select Reliance Effect:"),
        dcc.Dropdown(
            id='reliance-effect-dropdown',
            options=[
                {'label': 'Increase', 'value': 'Increase'},
                {'label': 'Decrease', 'value': 'Decrease'}
            ],
            multi=True
        )
    ], style={'width': '32%', 'display': 'inline-block'}),

    # Tableau interactif
    html.H2("Filtered Data Table"),
    dash_table.DataTable(
        id='filtered-table',
        columns=[{"name": col, "id": col} for col in df_melted.columns],
        page_size=10,
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'left'}
    ),

    # Graphiques interactifs
    dcc.Graph(id='reliance-bar-chart'),
    dcc.Graph(id='reliance-heatmap')
])

# Callback pour mettre à jour la table et les graphiques
@app.callback(
    [Output('filtered-table', 'data'),
     Output('reliance-bar-chart', 'figure'),
     Output('reliance-heatmap', 'figure')],
    [Input('modality-dropdown', 'value'),
     Input('format-dropdown', 'value'),
     Input('task-dropdown', 'value'),
     Input('domain-dropdown', 'value'),
     Input('xai-type-dropdown', 'value'),
     Input('xai-technique-dropdown', 'value'),
     Input('xai-method-dropdown', 'value'),
     Input('audience-dropdown', 'value'),
     Input('ai-model-dropdown', 'value'),
     Input('reliance-type-dropdown', 'value'),
     Input('reliance-effect-dropdown', 'value')]
)
def update_output(selected_modality, selected_format, selected_task, selected_domain, selected_xai_type,
                  selected_xai_technique, selected_xai_method, selected_audience, selected_ai_model,
                  selected_reliance, selected_effect):
    
    filtered_df = df_melted.copy()
    
    filters = {
        "Explanation Modality": selected_modality,
        "Explanation Format": selected_format,
        "Decision-Making Task": selected_task,
        "Application Domain": selected_domain,
        "XAI Type": selected_xai_type,
        "XAI Technique": selected_xai_technique,
        "XAI Method": selected_xai_method,
        "Audience": selected_audience,
        "AI Model": selected_ai_model,
        "Reliance Type": selected_reliance,
        "Reliance Effect": selected_effect
    }

    for col, values in filters.items():
        if values:
            filtered_df = filtered_df[filtered_df[col].isin(values)]

    # Mettre à jour la table
    table_data = filtered_df.to_dict('records')

    # Bar Chart
    reliance_counts = filtered_df.groupby(["Explanation Modality", "Reliance Type", "Reliance Effect"]).size().reset_index(name="Count")
    bar_fig = px.bar(
        reliance_counts,
        x="Explanation Modality",
        y="Count",
        color="Reliance Effect",
        facet_col="Reliance Type",
        barmode="group",
        title="Reliance Effects by Explanation Modality"
    )

    # Heatmap
    heatmap_data = filtered_df.pivot_table(index="Explanation Modality", columns="Explanation Format", values="Reliance Effect", aggfunc="count")
    heatmap_fig = px.imshow(
        heatmap_data,
        title="Co-occurrences of Explanation Modality, Format, and Reliance Effects",
        color_continuous_scale="viridis"
    )
    
    return table_data, bar_fig, heatmap_fig

# Lancer l'application
if __name__ == '__main__':
    app.run_server(debug=True)
