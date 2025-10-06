import dash
from dash import dcc, html, Input, Output, callback
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dash.exceptions import PreventUpdate
import sqlite3
import base64
from urllib.request import urlopen
import os  # Added for PORT handling in Render

# Load CSV data (your provided data)
df = pd.read_csv('main_data.csv')

# Optional: Use SQLite for storage/querying
USE_SQLITE = True  # Set to False to use CSV directly
if USE_SQLITE:
    conn = sqlite3.connect('drought_data.db')
    df.to_sql('drought', conn, if_exists='replace', index=False)
    # Query from DB instead
    df = pd.read_sql('SELECT * FROM drought', conn)

# Available years
years = sorted(df['year'].unique())

# Function to get map image as base64 (for display)
def get_map_image(year):
    url = df[df['year'] == year]['Map Images Left'].iloc[0]
    try:
        with urlopen(url) as response:
            img_data = response.read()
        encoded = base64.b64encode(img_data).decode()
        return f"data:image/jpeg;base64,{encoded}"
    except Exception as e:
        # Fallback to a simple placeholder if image fails to load
        return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAACklEQVR4nGMAAQAABQABDQottAAAAABJRU5ErkJggg=="  # 1x1 pixel placeholder

# Initialize the Dash app
app = dash.Dash(__name__)

# For production (Render/Heroku)
server = app.server  # Expose Flask server for Gunicorn

# Layout of the dashboard
app.layout = html.Div([
    html.Div([
        html.Img(id='map-left', style={'width': '300px', 'height': '300px'}),
        html.Div(id='pie-chart-left', style={'width': '300px', 'display': 'inline-block'}),
        html.Img(id='map-right', style={'width': '300px', 'height': '300px'}),
        html.Div(id='pie-chart-right', style={'width': '300px', 'display': 'inline-block'}),
    ], style={'display': 'flex', 'justify-content': 'space-around'}),
    
    html.Div([
        html.Div(id='value-left', style={'width': '100px', 'display': 'inline-block'}),
        html.Div(id='value-right', style={'width': '100px', 'display': 'inline-block'}),
    ], style={'display': 'flex', 'justify-content': 'space-around', 'margin-top': '20px'}),
    
    html.Div([
        dcc.Dropdown(
            id='year-left',
            options=[{'label': str(y), 'value': y} for y in years],
            value=years[0],
            style={'width': '150px'}
        ),
        dcc.Dropdown(
            id='year-right',
            options=[{'label': str(y), 'value': y} for y in years],
            value=years[1],
            style={'width': '150px'}
        ),
    ], style={'display': 'flex', 'justify-content': 'space-around', 'margin-top': '20px'})
])

# Callback to update the dashboard
@app.callback(
    [Output('map-left', 'src'),
     Output('pie-chart-left', 'children'),
     Output('map-right', 'src'),
     Output('pie-chart-right', 'children'),
     Output('value-left', 'children'),
     Output('value-right', 'children')],
    [Input('year-left', 'value'),
     Input('year-right', 'value')]
)
def update_dashboard(left_year, right_year):
    if left_year is None or right_year is None:
        raise PreventUpdate

    # Get data for left year
    left_data = df[df['year'] == left_year].iloc[0]
    right_data = df[df['year'] == right_year].iloc[0]

    # Update maps
    left_map_src = get_map_image(left_year)
    right_map_src = get_map_image(right_year)

    # Create pie charts
    pie_left = go.Figure(data=[go.Pie(labels=['Near Normal', 'Moderately Wet', 'Extremely Wet', 'Moderate Drought', 'Severe Drought', 'Extreme Drought'],
                                     values=[left_data['Near_Normal'], left_data['Moderately_Wet'], left_data['Extremely_Wet'], 
                                             left_data['Moderate_Drought'], left_data['Severe_Drought'], left_data['Extreme_Drought']],
                                     hole=.3)])
    pie_right = go.Figure(data=[go.Pie(labels=['Near Normal', 'Moderately Wet', 'Extremely Wet', 'Moderate Drought', 'Severe Drought', 'Extreme Drought'],
                                      values=[right_data['Near_Normal'], right_data['Moderately_Wet'], right_data['Extremely_Wet'], 
                                              right_data['Moderate_Drought'], right_data['Severe_Drought'], right_data['Extreme_Drought']],
                                      hole=.3)])

    # Convert pie charts to HTML components
    pie_left_html = dcc.Graph(figure=pie_left)
    pie_right_html = dcc.Graph(figure=pie_right)

    # Update value bars (example sums, adjust as needed)
    value_left = html.Div([
        html.P(f"Extreme Drought: {left_data['Extreme_Drought']:.2f}"),
        html.P(f"Extremely Wet: {left_data['Extremely_Wet']:.2f}"),
        html.P(f"Moderate Drought: {left_data['Moderate_Drought']:.2f}"),
        html.P(f"Moderately Wet: {left_data['Moderately_Wet']:.2f}"),
        html.P(f"Near Normal: {left_data['Near_Normal']:.2f}"),
        html.P(f"Severe Drought: {left_data['Severe_Drought']:.2f}")
    ])
    value_right = html.Div([
        html.P(f"Extreme Drought: {right_data['Extreme_Drought']:.2f}"),
        html.P(f"Extremely Wet: {right_data['Extremely_Wet']:.2f}"),
        html.P(f"Moderate Drought: {right_data['Moderate_Drought']:.2f}"),
        html.P(f"Moderately Wet: {right_data['Moderately_Wet']:.2f}"),
        html.P(f"Near Normal: {right_data['Near_Normal']:.2f}"),
        html.P(f"Severe Drought: {right_data['Severe_Drought']:.2f}")
    ])

    return left_map_src, pie_left_html, right_map_src, pie_right_html, value_left, value_right

if __name__ == '__main__':
    app.run_server(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), debug=False)