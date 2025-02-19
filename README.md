# Flugzeug-Datenvisualisierung – Dash-Projekt

---

## 1. Einführung

Dies ist eine kleine Web-App, die die Bewegungen von Flugzeugen zeigt, die auf einen Flughafen zufliegen. Die Flugzeuge werden mit Daten wie Startposition, Geschwindigkeit und Distanz zum Flughafen dargestellt. Außerdem werden mögliche Kollisionen angezeigt, falls Flugzeuge zu nah aneinander fliegen.

---

## 2. Funktionsweise

- **Berechnung der Flugzeit**: Jedes Flugzeug wird mit seiner Geschwindigkeit und der Distanz zum Flughafen berechnet. Die Zeit, die es braucht, um dort anzukommen, wird angezeigt.
- **Kollisionswarnung**: Wenn zwei Flugzeuge sich zu nahe kommen, wird eine Warnung ausgegeben.

---

## 3. Installation

### 3.1 Abhängigkeiten

Installiere die notwendigen Bibliotheken:

```bash
pip install dash plotly numpy
```

### 3.2 Flugzeug-Daten

Die Flugzeugdaten müssen in einer JSON-Datei gespeichert werden:

```json
[
    {
        "id": 1,
        "type": "Flugzeug A",
        "start_coords": [0, 0, 100],
        "speed": 600
    },
    {
        "id": 2,
        "type": "Flugzeug B",
        "start_coords": [50, 50, 100],
        "speed": 550
    }
]
```

---

## 4. Anwendung

### 4.1 Zeitschieberegler

Du kannst die Zeit in der Simulation mit einem Schieberegler steuern und die Bewegung der Flugzeuge beobachten.

### 4.2 Kollisionserkennung

Die App prüft, ob Flugzeuge zu nah aneinander fliegen und gibt eine Warnung aus, wenn es eine Kollision gibt.

---

## 5. Beispiel-Code

### 5.1 Flugzeitberechnung

Hier wird berechnet, wie lange ein Flugzeug braucht, um den Flughafen zu erreichen:

```python
def calculate_flight_data(planes, airport):
    flight_data = []
    for plane in planes:
        distance = np.linalg.norm(np.array(plane["start_coords"]) - np.array(airport))
        time_needed = distance / plane["speed"] * 60
        flight_data.append({
            "type": plane["type"],
            "time_needed": round(time_needed, 2)
        })
    return flight_data
```

### 5.2 Kollisionserkennung

Wenn zwei Flugzeuge zu nah aneinander kommen, wird eine Kollision erkannt:

```python
def check_for_collisions(flight_data, current_time):
    collisions = []
    for i, plane_1 in enumerate(flight_data):
        for j, plane_2 in enumerate(flight_data):
            if i >= j:
                continue
            distance = np.linalg.norm(np.array(plane_1['start_coords']) - np.array(plane_2['start_coords']))
            if distance < 50:  # Schwellenwert für Kollision
                collisions.append(f"{plane_1['type']} und {plane_2['type']} haben sich fast getroffen.")
    return collisions
```

### 5.3 Update der Anzeige

```python
@app.callback(
    [Output('flight-paths', 'figure'),
     Output('collision-alert', 'children')],
    [Input('time-slider', 'value')]
)
def update_display(current_time):
    collisions = check_for_collisions(flight_data, current_time)
    if collisions:
        return fig, f"Kollisionswarnung: {', '.join(collisions)}"
    return fig, "Keine Kollisionen."
```

---

## 6. Fazit

Diese App zeigt die Flugbewegungen und warnt vor Kollisionen, wenn Flugzeuge zu nahe kommen. Sie ist ein einfaches, aber effektives Werkzeug zur Visualisierung von Flugdaten.
