# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")

# Compute payload bounds
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a Dash application
app = dash.Dash(__name__)

# Build dropdown options (All Sites + unique sites from data)
site_options = [{'label': 'All Sites', 'value': 'ALL'}] + [
    {'label': site, 'value': site} for site in sorted(spacex_df['Launch Site'].unique())
]

# Create an app layout
app.layout = html.Div(children=[
    html.H1(
        'SpaceX Launch Records Dashboard',
        style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}
    ),

    # TASK 1: Launch Site dropdown
    dcc.Dropdown(
        id='site-dropdown',
        options=site_options,
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True
    ),

    html.Br(),

    # TASK 2: Pie chart
    html.Div(dcc.Graph(id='success-pie-chart')),

    html.Br(),

    # TASK 3: Payload range slider
    html.P("Payload range (Kg):"),
    dcc.RangeSlider(
        id='payload-slider',
        min=0, max=10000, step=1000,
        marks={
            0: '0',
            2500: '2500',
            5000: '5000',
            7500: '7500',
            10000: '10000'
        },
        value=[min_payload, max_payload]
    ),

    # TASK 4: Scatter chart
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2: Callback to render success-pie-chart based on selected site
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def get_pie_chart(selected_site):
    if selected_site == 'ALL':
        # Aggregate successes (sum of class) by site
        df_success = (
            spacex_df.groupby('Launch Site', as_index=False)['class']
            .sum()
        )
        fig = px.pie(
            df_success,
            values='class',
            names='Launch Site',
            title='Total Successful Launches by Site'
        )
    else:
        # Filter for the selected site and show Success vs Failure counts
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site].copy()
        filtered_df['Outcome'] = filtered_df['class'].replace({0: 'Failure', 1: 'Success'})
        df_counts = filtered_df['Outcome'].value_counts().reset_index()
        df_counts.columns = ['Outcome', 'Count']
        fig = px.pie(
            df_counts,
            values='Count',
            names='Outcome',
            title=f'Success vs Failure for {selected_site}'
        )
    return fig

# TASK 4: Callback to render the success-payload-scatter-chart
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter(selected_site, payload_range):
    low, high = payload_range

    # Filter by payload range
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) &
        (spacex_df['Payload Mass (kg)'] <= high)
    ]

    # Filter by launch site if needed
    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]

    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title=('Correlation between Payload and Success for All Sites'
               if selected_site == 'ALL'
               else f'Correlation between Payload and Success for {selected_site}'),
        labels={'class': 'Launch Outcome (0=Failure, 1=Success)'},
        hover_data=['Launch Site']
    )
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
