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
        flight_data.append({
            "id": plane["id"],
            "type": plane["type"],
            "distance": round(distance, 2),
            "time_needed": round(time_needed, 2),
            "start_coords": plane["start_coords"],
            "block_time": plane["block_time"],
            "speed": plane["speed"]
        })
    return flight_data

flight_data = calculate_flight_data(planes, airport)

def adjust_speeds_to_avoid_collisions(flight_data):
    adjusted = True
    collision_log = []
    while adjusted:
        adjusted = False
        for i, plane_1 in enumerate(flight_data):
            for j, plane_2 in enumerate(flight_data):
                if i >= j:
                    continue

                t1 = plane_1['time_needed']
                t2 = plane_2['time_needed']
                if abs(t1 - t2) < collision_threshold:
                    adjusted = True
                    original_collision_time = (t1 + t2) / 2
                    if t1 < t2:
                        plane_1['speed'] *= 0.95
                        plane_2['speed'] *= 1.05
                    else:
                        plane_1['speed'] *= 1.05
                        plane_2['speed'] *= 0.95

                    plane_1['time_needed'] = plane_1['distance'] / plane_1['speed'] * 60
                    plane_2['time_needed'] = plane_2['distance'] / plane_2['speed'] * 60

                    collision_log.append({
                        "plane_1": plane_1['type'],
                        "plane_2": plane_2['type'],
                        "original_collision_time": round(original_collision_time, 2),
                        "new_speed_1": round(plane_1['speed'], 2),
                        "new_speed_2": round(plane_2['speed'], 2)
                    })

    return flight_data, collision_log

flight_data, collision_log = adjust_speeds_to_avoid_collisions(flight_data)
max_time = max([plane['time_needed'] for plane in flight_data])

app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div([
        html.H3("Angepasste Fluggeschwindigkeiten zur Unfallvermeidung:"),
        dcc.Dropdown(
            id='collision-dropdown',
            options=[
                {"label": f"{c['plane_1']} und {c['plane_2']}", "value": i} 
                for i, c in enumerate(collision_log)
            ],
            placeholder="Wähle eine Kollision aus..."
        ),
        html.Div(id='collision-details')
    ], style={'color': 'green', 'fontSize': 20}),
    dcc.Graph(id='3d-flight-paths'),
    dcc.Slider(
        id='time-slider',
        min=0,
        max=max_time+1,
        value=0,
        marks={i: str(i) for i in range(0, int(max_time) + 1, 10)},
        step=1
    ),
    dash_table.DataTable(
        id='flight-table',
        columns=[
            {"name": "Flugzeug", "id": "type"},
            {"name": "Fortschritt (%)", "id": "progress"},
            {"name": "Ankunftszeit (Min)", "id": "time_needed"}
        ],
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'center'}
    )
])

@app.callback(
    Output('collision-details', 'children'),
    [Input('collision-dropdown', 'value')]
)
def update_collision_details(selected_index):
    if selected_index is None:
        return ""
    c = collision_log[selected_index]
    return html.P(f"{c['plane_1']} und {c['plane_2']} hätten sich bei {c['original_collision_time']} Min getroffen. - {c['plane_1']}: {c['new_speed_1']} - {c['plane_2']}: {c['new_speed_2']}")

@app.callback(
    [Output('3d-flight-paths', 'figure'),
     Output('flight-table', 'data')],
    [Input('time-slider', 'value')]
)
def update_graph(current_time):
    fig = go.Figure()
    table_data = []

    fig.add_trace(go.Scatter3d(
        x=[airport[0]],
        y=[airport[1]],
        z=[airport[2]],
        mode='markers',
        marker=dict(size=10, color='yellow'),
        name="Flughafen"
    ))

    for plane in flight_data:
        progress = min(1, current_time / plane['time_needed']) * 100
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
            "time_needed": f"{plane['time_needed']:.1f} min"
        })

    fig.update_layout(scene=dict(
        xaxis_title='X', yaxis_title='Y', zaxis_title='Höhe',
        aspectmode='cube'
    ))

    return fig, table_data

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8080)
