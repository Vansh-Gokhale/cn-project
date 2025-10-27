# 🛰️ network — Realtime Network Monitoring System 🚦

A lightweight, realtime network monitoring system implemented in Python. `network.py` collects network statistics and packet-level information, processes metrics, and exposes them for live dashboards and alerting. Ideal for learning, lab experiments, or small-scale monitoring setups. ⚡

---

## 🔍 Overview

This project captures and analyzes network activity in realtime, providing:

- Per-interface bandwidth and packet rate
- Active connection tracking (TCP/UDP)
- Basic packet inspection and protocol breakdown
- Live metrics stream for dashboards (WebSocket / HTTP)
- Exportable metrics for Prometheus or CSV

Use it as a standalone CLI tool or as a backend for a custom web dashboard. 🎛️

---

## 🚀 Key Features

- Realtime collection with configurable polling interval ⏱️
- Lightweight in-memory aggregation for low-latency updates 🧠
- WebSocket endpoint for live dashboards 🌐
- Optional Prometheus metrics endpoint for long-term scraping 📈
- Alert hooks for threshold-based notifications (email, webhook) 🔔

---

## ⚙️ Prerequisites

- Python 3.8+
- macOS / Linux (packet capture features may require root privileges)

Recommended Python libraries (add to `requirements.txt` if used):

- psutil — interface stats
- scapy or pyshark — packet capture/inspection (optional)
- websockets or aiohttp — realtime API
- prometheus_client — metrics export
- click or argparse — CLI parsing

---

## 🧩 Installation

1. Create a Python virtual environment and activate it:

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies (if you create a `requirements.txt`):

```bash
pip install -r requirements.txt
```

---

## ▶️ Usage (examples)

Run the main collector on a specific interface with a 1-second interval:

```bash
# capture on interface en0 every second and start the realtime server
python3 network.py --interface en0 --interval 1 --serve-websocket
```

See CLI help for available options:

```bash
python3 network.py --help
```

Prometheus scraping example (if enabled):

```bash
# run the collector with Prometheus exporter on port 8000
python3 network.py --prometheus-port 8000
```

---

## 🏗️ Architecture

1. Collector: polls OS interface counters and (optionally) packet capture library.
2. Processor: aggregates counters into per-second rates, histograms, and protocol counts.
3. Exporters:
   - WebSocket: push realtime updates to connected dashboards
   - HTTP/Prometheus: expose metrics for scraping
   - CSV/Log: optional persistent storage
4. Dashboard / Alerts: external or bundled frontend subscribes to WebSocket and visualizes metrics.

ASCII flow:

Collector -> Processor -> {WebSocket Server, Prometheus Exporter, CSV Logger} -> Dashboard / Alerting

---

## 🔧 Configuration

You can specify options via CLI flags or a config file (e.g., `config.yml`). Typical settings:

- interface: network interface to monitor (e.g., `en0`, `eth0`)
- interval: polling interval in seconds
- websocket_port: port to serve realtime updates
- prometheus_port: port for metrics scraping
- alert thresholds: bandwidth / packet rate thresholds

Example config snippet (YAML):

```yaml
interface: en0
interval: 1
websocket_port: 8765
prometheus_port: 8000
alerts:
  bandwidth_mbps: 500
```

---

## 🧪 Development & Extensibility

- Convert `network.py` into a package (`network/`) and split concerns: collector, processor, exporter, api.
- Add unit tests for aggregation logic with `pytest`.
- Integrate with a lightweight frontend (React/Vue) that connects to the WebSocket feed.
- Add authentication for the realtime API when exposing it publicly.

---

## 📈 Monitoring & Production Notes

- Packet capture requires elevated privileges — run with sudo when needed.
- For long-term metrics, use the Prometheus exporter and a TSDB (Prometheus + Grafana).
- Keep polling interval reasonable (>= 1s) to balance fidelity and CPU usage.

---

## 🤝 Contributing

Contributions welcome — open issues or PRs. Please include tests for new logic and document new CLI flags or config fields. 📝

---

## 📜 License

Add a `LICENSE` file to specify terms. If none is added, all rights are reserved. 🔒

---

## ✉️ Contact

Have questions or want help wiring this to a dashboard? Open an issue or PR and include logs and usage examples. Happy monitoring! 👀
