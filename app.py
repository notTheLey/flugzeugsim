import json
import numpy as np
import plotly.graph_objects as go
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output

airport = [0, 0, 0]
collision_threshold = 10

def load_planes(json_file):
    with open(json_file, 'r') as file:
        return json.load(file)

planes = load_planes('planes.json')

def calculate_flight_data(planes, airport):
    flight_data = []
    for plane in planes:
        start = np.array(plane["start_coords"])
        distance = np.linalg.norm(start - np.array(airport))
        time_needed = distance / plane["speed"] * 60
        arrival_time = time_needed
        flight_data.append({
            "id": plane["id"],
            "type": plane["type"],
            "distance": round(distance, 2),
            "time_needed": round(time_needed, 2),
            "arrival_time": round(arrival_time, 2),
            "start_coords": plane["start_coords"],
            "block_time": plane["block_time"]
        })
    return flight_data

flight_data = calculate_flight_data(planes, airport)

def check_for_collisions(flight_data, current_time):
    detected_collisions = []
    for i, plane_1 in enumerate(flight_data):
        progress_1 = min(1, current_time / plane_1['time_needed']) * 100
        position_1 = np.array(plane_1['start_coords']) * (1 - progress_1 / 100)
        if current_time > plane_1['arrival_time'] + plane_1['block_time']:
            continue

        for j, plane_2 in enumerate(flight_data):
            if i >= j:
                continue
            progress_2 = min(1, current_time / plane_2['time_needed']) * 100
            position_2 = np.array(plane_2['start_coords']) * (1 - progress_2 / 100)
            if current_time > plane_2['arrival_time'] + plane_2['block_time']:
                continue
            distance = np.linalg.norm(position_1 - position_2)
            if distance < collision_threshold:
                detected_collisions.append({
                    "plane_1": plane_1["type"],
                    "plane_2": plane_2["type"],
                    "position": (position_1 + position_2) / 2,
                    "distance": distance
                })
    return detected_collisions

max_time = max([plane['arrival_time'] for plane in flight_data])

app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div(id='collision-warning', children=[
        html.H3("Keine Unfälle erkannt")
    ], style={'color': 'red', 'fontSize': 20}),
    dcc.Graph(id='3d-flight-paths'),
    dcc.Slider(
        id='time-slider',
        min=0,
        max=max_time,
        value=0,
        marks={i: str(i) for i in range(0, int(max_time) + 1, 10)},
        step=1
    ),
    dash_table.DataTable(
        id='flight-table',
        columns=[
            {"name": "Flugzeug", "id": "type"},
            {"name": "Fortschritt (%)", "id": "progress"},
            {"name": "Ankunftszeit (Min)", "id": "arrival_time"}
        ],
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'center'}
    )
])

@app.callback(
    [Output('3d-flight-paths', 'figure'),
     Output('flight-table', 'data'),
     Output('collision-warning', 'children')],
    [Input('time-slider', 'value')]
)
def update_graph(current_time):
    fig = go.Figure()
    table_data = []
    collision_warning = [html.H3("Keine Unfälle erkannt")]
    detected_collisions = check_for_collisions(flight_data, current_time)

    if detected_collisions:
        collision_warning = [html.H3("Unfall zwischen:")]
        for collision in detected_collisions:
            collision_warning.append(html.P(f"{collision['plane_1']} und {collision['plane_2']} bei Position {collision['position']}"))

    fig.add_trace(go.Scatter3d(
        x=[airport[0]],
        y=[airport[1]],
        z=[airport[2]],
        mode='markers',
        marker=dict(size=10, color='yellow'),
        name="Flughafen"
    ))

    for plane in planes:
        data = next(f for f in flight_data if f['id'] == plane['id'])
        progress = min(1, current_time / data['time_needed']) * 100
        remaining_time = max(0, data['time_needed'] - current_time)
        current_position = np.array(plane['start_coords']) * (1 - progress / 100)
        fig.add_trace(go.Scatter3d(
            x=[plane['start_coords'][0], airport[0]],
            y=[plane['start_coords'][1], airport[1]],
            z=[plane['start_coords'][2], airport[2]],
            mode='lines',
            name=f"{plane['type']} Path"
        ))
        fig.add_trace(go.Scatter3d(
            x=[current_position[0]],
            y=[current_position[1]],
            z=[current_position[2]],
            mode='markers',
            marker=dict(size=5, color='blue'),
            name=f"{plane['type']} ({progress:.1f}%)"
        ))
        table_data.append({
            "type": plane['type'],
            "progress": f"{progress:.1f}%",
            "arrival_time": f"{data['arrival_time']:.1f} min"
        })

    fig.update_layout(scene=dict(
        xaxis_title='X', yaxis_title='Y', zaxis_title='Höhe',
        aspectmode='cube'
    ))

    return fig, table_data, collision_warning

if __name__ == '__main__':
    app.run_server(debug=True, port=8080)
