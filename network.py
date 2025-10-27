from scapy.all import sniff, IP, conf
import plotly.graph_objs as go
from dash import Dash, dcc, html, Input, Output
import threading
import time
import requests
from collections import Counter, deque

# ----------------------------
# Global Data
# ----------------------------
incoming_ips = Counter()
outgoing_ips = Counter()
packet_timeline = deque(maxlen=100)
geolocation_cache = {}

# ----------------------------
# Function: Geolocate IP
# ----------------------------
def geolocate_ip(ip):
    if ip in geolocation_cache:
        return geolocation_cache[ip]
    try:
        res = requests.get(f"http://ip-api.com/json/{ip}", timeout=3).json()
        data = {
            "lat": res.get("lat"),
            "lon": res.get("lon"),
            "country": res.get("country", "Unknown")
        }
        geolocation_cache[ip] = data
        return data
    except:
        return {"lat": None, "lon": None, "country": "Unknown"}

# ----------------------------
# Packet Processing Function
# ----------------------------
def process_packet(packet):
    if packet.haslayer(IP):
        src = packet[IP].src
        dst = packet[IP].dst
        packet_timeline.append(time.time())

        # Separate Incoming vs Outgoing
        if src.startswith("192.168.") or src.startswith("10."):
            outgoing_ips[dst] += 1
        else:
            incoming_ips[src] += 1

# ----------------------------
# Sniff Packets
# ----------------------------
def packet_sniffer():
    try:
        print("[*] Sniffing packets... (Press CTRL+C to stop)")
        conf.sniff_promisc = True
        sniff(prn=process_packet, store=False)
    except Exception as e:
        print(f"[!] Packet sniffing failed: {e}")
        print("[!] Make sure Npcap is installed (https://npcap.org/) with WinPcap compatibility.")

# ----------------------------
# Dash App Layout
# ----------------------------
app = Dash(__name__)
app.title = "Network Attack Visualizer"

app.layout = html.Div(style={"backgroundColor": "#0d0d0d", "color": "#fff", "padding": "10px"}, children=[
    html.H1("🛡 Network Traffic Monitor", style={"textAlign": "center", "color": "#FF4C4C"}),

    dcc.Interval(id="interval", interval=2000, n_intervals=0),

    # Live Stats Counters
    html.Div(style={"textAlign": "center", "marginBottom": "20px"}, children=[
        html.Div(id="stats", style={"fontSize": "20px", "margin": "10px"})
    ]),

    html.Div([
        dcc.Graph(id="traffic-bar", style={"width": "48%", "display": "inline-block"}),
        dcc.Graph(id="traffic-line", style={"width": "48%", "display": "inline-block"})
    ]),

    html.Div([
        dcc.Graph(id="attack-map", style={"width": "100%", "height": "600px"})
    ])
])

# ----------------------------
# Callbacks
# ----------------------------
@app.callback(
    [Output("traffic-bar", "figure"),
     Output("traffic-line", "figure"),
     Output("attack-map", "figure"),
     Output("stats", "children")],
    Input("interval", "n_intervals")
)
def update_dashboard(n):
    # ---- Bar Graph: Incoming vs Outgoing ----
    bar_fig = go.Figure()
    bar_fig.add_trace(go.Bar(
        x=list(incoming_ips.keys()), y=list(incoming_ips.values()),
        name="Incoming", marker=dict(color="red")
    ))
    bar_fig.add_trace(go.Bar(
        x=list(outgoing_ips.keys()), y=list(outgoing_ips.values()),
        name="Outgoing", marker=dict(color="green")
    ))
    bar_fig.update_layout(
        title="Incoming vs Outgoing Packets",
        xaxis_title="IP Address",
        yaxis_title="Packet Count",
        barmode="group",
        template="plotly_dark",
        showlegend=True
    )

    # ---- Line Graph: Traffic Timeline ----
    if packet_timeline:
        timeline_x = list(packet_timeline)
        timeline_y = [i for i in range(1, len(timeline_x) + 1)]
    else:
        timeline_x, timeline_y = [], []

    line_fig = go.Figure()
    line_fig.add_trace(go.Scatter(
        x=timeline_x, y=timeline_y,
        mode="lines+markers",
        line=dict(color="cyan"),
        name="Traffic"
    ))
    line_fig.update_layout(
        title="Live Traffic Over Time",
        xaxis_title="Time (s)",
        yaxis_title="Packet Count",
        template="plotly_dark"
    )

    # ---- Map Visualization ----
    lats, lons, texts = [], [], []
    for ip, count in incoming_ips.most_common(20):
        geo = geolocate_ip(ip)
        if geo["lat"] and geo["lon"]:
            lats.append(geo["lat"])
            lons.append(geo["lon"])
            texts.append(f"{ip} ({geo['country']}) - {count} packets")

    map_fig = go.Figure(go.Scattermapbox(
        lat=lats,
        lon=lons,
        text=texts,
        mode="markers",
        marker=dict(size=12, color="red"),
    ))

    map_fig.update_layout(
        mapbox=dict(style="carto-darkmatter", center={"lat": 20, "lon": 0}, zoom=1),
        title="Top Incoming IPs (Geolocation)",
        template="plotly_dark"
    )

    # ---- Live Stats ----
    stats_text = f"📦 Total Packets: {len(packet_timeline)} | 🌐 Unique Incoming IPs: {len(incoming_ips)} | 📤 Unique Outgoing IPs: {len(outgoing_ips)}"

    return bar_fig, line_fig, map_fig, stats_text

# ----------------------------
# Run
# ----------------------------
if __name__ == "__main__":
    print("[*] Starting packet sniffer... open http://127.0.0.1:8050 in browser")
    threading.Thread(target=packet_sniffer, daemon=True).start()
    app.run(debug=True)