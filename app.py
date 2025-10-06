import dash
from dash import dcc, html, Input, Output, callback
import pandas as pd
import plotly.graph_objects as go
import base64
import urllib.request
import os  # For environment variables (e.g., PORT for Render)
import logging  # For logging debug/info messages
from flask import Flask  # For explicit server control
import gunicorn  # For production server hint (used by Render)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load data
df = pd.read_csv('main_data.csv')
years = sorted(df['year'].unique())

app = dash.Dash(__name__, server=Flask(__name__))  # Use Flask server explicitly

# Define colors for categories
colors = {
    'Near_Normal': '#90EE90',
    'Moderately_Wet': '#4169E1', 
    'Extremely_Wet': '#0000FF',
    'Moderate_Drought': '#FFA500',
    'Severe_Drought': '#FF4500',
    'Extreme_Drought': '#8B0000'
}

def get_image_base64(url):
    try:
        with urllib.request.urlopen(url) as response:
            img_data = response.read()
        return f"data:image/jpeg;base64,{base64.b64encode(img_data).decode()}"
    except Exception as e:
        logger.error(f"Failed to load image from {url}: {e}")
        return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="

def create_pie_chart(year_data, year):
    categories = ['Extreme_Drought', 'Severe_Drought', 'Moderate_Drought', 'Extremely_Wet', 'Moderately_Wet', 'Near_Normal']
    values = [year_data[cat].iloc[0] for cat in categories]
    chart_colors = [colors[cat] for cat in categories]
    
    fig = go.Figure(data=[go.Pie(
        labels=categories,
        values=values,
        marker_colors=chart_colors,
        textinfo='percent',
        textposition='inside'
    )])
    fig.update_layout(
        title={'text': f'{year} Distribution', 'x': 0.5, 'font': {'size': 14}},
        margin=dict(t=30, b=0, l=0, r=0), 
        height=250,
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def create_metric_card(category, value, side):
    icons = {
        'Extreme_Drought': '☀️',
        'Extremely_Wet': '💧',
        'Moderate_Drought': '🌤️',
        'Moderately_Wet': '🌧️',
        'Near_Normal': '🌿',
        'Severe_Drought': '🔥'
    }
    
    return html.Div([
        html.Div(icons.get(category, '📊'), style={'font-size': '16px', 'margin-bottom': '2px'}),
        html.Div(category.replace('_', ' '), style={'font-weight': 'bold', 'font-size': '10px'}),
        html.Div(f'{value:.1f}', style={'font-size': '12px', 'color': '#333'})
    ], style={
        'background-color': colors.get(category, '#f0f0f0'),
        'padding': '8px',
        'margin': '2px',
        'border-radius': '6px',
        'text-align': 'center',
        'box-shadow': '0 1px 3px rgba(0,0,0,0.1)',
        'color': 'white' if category in ['Extreme_Drought', 'Severe_Drought', 'Extremely_Wet'] else 'black',
        'flex': '1'
    })

app.layout = html.Div([
    # Header with title and dropdowns
    html.Div([
        html.H1("Marathwada Drought Dashboard Comparison", 
                style={'color': '#ffffff', 'margin': '0', 'font-size': '24px'}),
        html.Div([
            html.Div([
                html.Label("Left Year", style={'color': '#ffffff', 'font-size': '12px', 'margin-bottom': '2px'}),
                dcc.Dropdown(
                    id='year-left',
                    options=[{'label': year, 'value': year} for year in years],
                    value=1982 if 1982 in years else years[0],
                    style={'width': '100px'}
                )
            ], style={'margin-right': '20px'}),
            html.Div([
                html.Label("Right Year", style={'color': '#ffffff', 'font-size': '12px', 'margin-bottom': '2px'}),
                dcc.Dropdown(
                    id='year-right',
                    options=[{'label': year, 'value': year} for year in years],
                    value=1981 if 1981 in years else years[1] if len(years) > 1 else years[0],
                    style={'width': '100px'}
                )
            ])
        ], style={'display': 'flex', 'align-items': 'center'})
    ], style={'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', 'padding': '15px', 'display': 'flex', 'justify-content': 'space-between', 'align-items': 'center'}),
    
    # Main content area
    html.Div([
        # Left column
        html.Div([
            # Left map (priority)
            html.Div([
                html.H4("Left Year", style={'text-align': 'center', 'margin': '5px 0', 'color': '#2c3e50'}),
                html.Img(id='map-left', style={'width': '100%', 'height': '280px', 'object-fit': 'contain', 'border-radius': '8px'})
            ], style={'background': '#ffffff', 'padding': '10px', 'border-radius': '8px', 'box-shadow': '0 2px 8px rgba(0,0,0,0.1)', 'margin-bottom': '10px'}),
            
            # Left pie chart
            html.Div([
                dcc.Graph(id='pie-left', style={'height': '250px'})
            ], style={'background': '#ffffff', 'border-radius': '8px', 'box-shadow': '0 2px 8px rgba(0,0,0,0.1)', 'margin-bottom': '10px'}),
            
            # Left metrics
            html.Div(id='metrics-left', style={'background': '#ffffff', 'padding': '10px', 'border-radius': '8px', 'box-shadow': '0 2px 8px rgba(0,0,0,0.1)'})
        ], style={'width': '48%'}),
        
        # Right column
        html.Div([
            # Right map (priority)
            html.Div([
                html.H4("Right Year", style={'text-align': 'center', 'margin': '5px 0', 'color': '#2c3e50'}),
                html.Img(id='map-right', style={'width': '100%', 'height': '280px', 'object-fit': 'contain', 'border-radius': '8px'})
            ], style={'background': '#ffffff', 'padding': '10px', 'border-radius': '8px', 'box-shadow': '0 2px 8px rgba(0,0,0,0.1)', 'margin-bottom': '10px'}),
            
            # Right pie chart
            html.Div([
                dcc.Graph(id='pie-right', style={'height': '250px'})
            ], style={'background': '#ffffff', 'border-radius': '8px', 'box-shadow': '0 2px 8px rgba(0,0,0,0.1)', 'margin-bottom': '10px'}),
            
            # Right metrics
            html.Div(id='metrics-right', style={'background': '#ffffff', 'padding': '10px', 'border-radius': '8px', 'box-shadow': '0 2px 8px rgba(0,0,0,0.1)'})
        ], style={'width': '48%'})
    ], style={'display': 'flex', 'justify-content': 'space-between', 'padding': '15px', 'gap': '15px'})
], style={'font-family': 'Segoe UI, Arial, sans-serif', 'background': 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)', 'min-height': '100vh', 'margin': '0'})

@callback(
    [Output('map-left', 'src'),
     Output('map-right', 'src'),
     Output('pie-left', 'figure'),
     Output('pie-right', 'figure'),
     Output('metrics-left', 'children'),
     Output('metrics-right', 'children')],
    [Input('year-left', 'value'),
     Input('year-right', 'value')]
)
def update_dashboard(year_left, year_right):
    if not year_left or not year_right:
        raise dash.exceptions.PreventUpdate
    
    # Get data for selected years
    left_data = df[df['year'] == year_left]
    right_data = df[df['year'] == year_right]
    
    # Get map images
    map_left_src = get_image_base64(left_data['Map Images Left'].iloc[0])
    map_right_src = get_image_base64(right_data['Map Images Left'].iloc[0])
    
    # Create pie charts
    pie_left = create_pie_chart(left_data, year_left)
    pie_right = create_pie_chart(right_data, year_right)
    
    # Create metric grids (3x2 layout)
    categories_grid = [
        ['Extreme_Drought', 'Severe_Drought', 'Moderate_Drought'],
        ['Extremely_Wet', 'Moderately_Wet', 'Near_Normal']
    ]
    
    metrics_left = html.Div([
        html.Div([
            create_metric_card(cat, left_data[cat].iloc[0], 'Left') for cat in row
        ], style={'display': 'flex', 'justify-content': 'space-between'}) for row in categories_grid
    ])
    
    metrics_right = html.Div([
        html.Div([
            create_metric_card(cat, right_data[cat].iloc[0], 'Right') for cat in row
        ], style={'display': 'flex', 'justify-content': 'space-between'}) for row in categories_grid
    ])
    
    return map_left_src, map_right_src, pie_left, pie_right, metrics_left, metrics_right

if __name__ == '__main__':
    logger.info("Starting Dash application locally on port 8080 - Access at http://localhost:8080")
    app.run(host="0.0.0.0", port=8080, debug=True)