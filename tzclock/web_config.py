import html
import os
import tempfile
import threading

import requests
import yaml
from flask import Flask, jsonify, redirect, request
from timezonefinder import TimezoneFinder

from tzclock.config import CONFIG_PATH, load_config

tf = TimezoneFinder()
app = Flask(__name__)

USER_AGENT = "timezone-clock/0.1 local-config-ui"


def save_config(config):
    directory = os.path.dirname(CONFIG_PATH) or "."
    fd, tmp_path = tempfile.mkstemp(dir=directory, prefix=".config.", suffix=".yaml")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        yaml.safe_dump(config, f, sort_keys=False)
    os.replace(tmp_path, CONFIG_PATH)


@app.route("/")
def index():
    config = load_config()
    cities = config.get("cities", [])

    rows = ""
    for i, city in enumerate(cities):
        rows += f"""
        <tr>
          <td>
            <button name="move_up" value="{i}">↑</button>
            <button name="move_down" value="{i}">↓</button>
          </td>
          <td><input name="name_{i}" value="{html.escape(str(city['name']))}"></td>
          <td><input name="timezone_{i}" value="{html.escape(str(city['timezone']))}"></td>
          <td><input name="lat_{i}" value="{city['lat']}"></td>
          <td><input name="lon_{i}" value="{city['lon']}"></td>
          <td><button name="delete" value="{i}">Delete</button></td>
        </tr>
        """

    return f"""
    <html>
    <head>
      <title>Timezone Clock</title>
      <style>
        body {{ font-family: sans-serif; margin: 30px; background: #111; color: #eee; }}
        input {{ width: 150px; padding: 6px; background: #222; color: #eee; border: 1px solid #555; }}
        button {{ padding: 7px 12px; margin: 4px; cursor: pointer; }}
        table {{ border-collapse: collapse; }}
        td, th {{ padding: 6px; }}
        .lookup {{ margin-bottom: 25px; padding: 15px; background: #222; }}
        .result {{ margin: 8px 0; padding: 10px; background: #181818; border: 1px solid #444; }}
        .muted {{ color: #aaa; font-size: 0.9em; }}
      </style>
    </head>
    <body>
      <h1>Timezone Clock</h1>

      <div class="lookup">
        <h2>Lookup location</h2>
        <input id="q" placeholder="Dallas, TX">
        <button onclick="lookup()">Search</button>
        <div id="results"></div>
      </div>

      <form method="post" action="/save">
        <table>
          <tr>
            <th>Order</th><th>Name</th><th>Timezone</th><th>Latitude</th><th>Longitude</th><th></th>
          </tr>
          {rows}
        </table>

        <input type="hidden" name="count" value="{len(cities)}">
        <p>
          <button name="add_blank" value="1">Add blank city</button>
          <button type="submit">Save</button>
        </p>
      </form>

      <script>
        async function lookup() {{
          const q = document.getElementById("q").value;
          const results = document.getElementById("results");
          results.innerHTML = "Searching...";

          const r = await fetch("/lookup?q=" + encodeURIComponent(q));
          const data = await r.json();

          if (!Array.isArray(data)) {{
            results.textContent = JSON.stringify(data, null, 2);
            return;
          }}

          results.innerHTML = "";
          data.forEach(item => {{
            const div = document.createElement("div");
            div.className = "result";

            const title = document.createElement("div");
            title.textContent = item.display_name;

            const meta = document.createElement("div");
            meta.className = "muted";
            meta.textContent = `${{item.timezone}} | ${{item.lat}}, ${{item.lon}}`;

            const name = document.createElement("input");
            name.value = item.suggested_name;

            const button = document.createElement("button");
            button.textContent = "Add to clock";
            button.onclick = async () => {{
              const params = new URLSearchParams();
              params.set("name", name.value);
              params.set("timezone", item.timezone);
              params.set("lat", item.lat);
              params.set("lon", item.lon);

              await fetch("/add_city", {{
                method: "POST",
                headers: {{ "Content-Type": "application/x-www-form-urlencoded" }},
                body: params
              }});

              window.location.reload();
            }};

            div.appendChild(title);
            div.appendChild(meta);
            div.appendChild(name);
            div.appendChild(button);
            results.appendChild(div);
          }});
        }}
      </script>
    </body>
    </html>
    """


@app.route("/lookup")
def lookup():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify({"error": "missing query"}), 400

    r = requests.get(
        "https://nominatim.openstreetmap.org/search",
        params={"q": q, "format": "json", "limit": 5},
        headers={"User-Agent": USER_AGENT},
        timeout=10,
    )
    r.raise_for_status()

    results = []
    for item in r.json():
        lat = float(item["lat"])
        lon = float(item["lon"])
        tz = tf.timezone_at(lat=lat, lng=lon) or ""

        display_name = item.get("display_name", "")
        suggested_name = display_name.split(",")[0] if display_name else q

        results.append(
            {
                "display_name": display_name,
                "suggested_name": suggested_name,
                "lat": round(lat, 5),
                "lon": round(lon, 5),
                "timezone": tz,
            }
        )

    return jsonify(results)


@app.route("/add_city", methods=["POST"])
def add_city():
    config = load_config()
    cities = config.get("cities", [])

    cities.append(
        {
            "name": request.form["name"].strip(),
            "timezone": request.form["timezone"].strip(),
            "lat": float(request.form["lat"]),
            "lon": float(request.form["lon"]),
        }
    )

    config["cities"] = cities
    save_config(config)
    return jsonify({"ok": True})


@app.route("/save", methods=["POST"])
def save():
    config = load_config()
    count = int(request.form.get("count", 0))

    cities = []
    for i in range(count):
        if request.form.get("delete") == str(i):
            continue

        name = request.form.get(f"name_{i}", "").strip()
        tz = request.form.get(f"timezone_{i}", "").strip()
        lat = request.form.get(f"lat_{i}", "").strip()
        lon = request.form.get(f"lon_{i}", "").strip()

        if name and tz and lat and lon:
            cities.append(
                {
                    "name": name,
                    "timezone": tz,
                    "lat": float(lat),
                    "lon": float(lon),
                }
            )

    move_up = request.form.get("move_up")
    move_down = request.form.get("move_down")

    if move_up is not None:
        i = int(move_up)
        if 0 < i < len(cities):
            cities[i - 1], cities[i] = cities[i], cities[i - 1]

    if move_down is not None:
        i = int(move_down)
        if 0 <= i < len(cities) - 1:
            cities[i + 1], cities[i] = cities[i], cities[i + 1]

    if request.form.get("add_blank"):
        cities.append(
            {
                "name": "New City",
                "timezone": "Etc/UTC",
                "lat": 0.0,
                "lon": 0.0,
            }
        )

    config["cities"] = cities
    save_config(config)
    return redirect("/")


def start_web_config(host="0.0.0.0", port=8080):
    thread = threading.Thread(
        target=lambda: app.run(host=host, port=port, debug=False, use_reloader=False),
        daemon=True,
    )
    thread.start()
