# Timezone Clock

A Raspberry Pi-powered wall/desk timezone clock with a world map, day/night terminator, automatic daylight savings handling, and a built-in web interface for configuring displayed locations.

Designed to be an appliance rather than a desktop application. Once configured, the system boots directly into the clock display and can be managed entirely through a web browser.


---

# Features

- Multiple configurable timezones
- Automatic daylight savings adjustments using IANA timezones
- World map with:
  - Natural Earth coastline data
  - Day/night overlay
  - Twilight transition
  - Solar position indicator
  - City markers
- Automatic configuration reload (no restart required)
- Built-in web configuration interface
- Hardware accelerated via pygame

## UI

![photo showing time data across the top. the bottom displays a mercator projection with the sun, current light/dark lines, and the cities from clock display located on map](https://github.com/user-attachments/assets/934241ae-231e-455b-a06d-51ac59dfa645)

## Web Interface

![photo of the web interface for location and timezone configuration](https://github.com/user-attachments/assets/3f20cdaf-930d-443e-92f6-c924e56f53f8)



---

# Hardware

Designed to run on most modern Raspberry Pi devices

Development Hardware:
- Raspberry Pi 4B
- Raspberry Pi OS Desktop
- Adafruit 7" DSI Display


---

# Repository Layout

```
timezone-clock/

├── assets/
│   └── ne_110m_land.geojson
│
├── tzclock/
│   ├── astronomy.py
│   ├── config.py
│   ├── display.py
│   ├── icons.py
│   ├── map_renderer.py
│   └── web_config.py
│
├── clock.py
├── config.yaml
├── run_clock.sh
└── README.md
```

---

# Initial Setup

Update the Pi (optional)

```bash
sudo apt update
sudo apt full-upgrade -y
```

Install required packages.

```bash
sudo apt install \
    python3-pygame \
    python3-yaml \
    python3-flask \
    python3-requests \
    grim \
    feh
```

Install timezonefinder.

```bash
pip install timezonefinder --break-system-packages
```

Clone the repository.

HTTPS:

```bash
git clone https://github.com/ecubed99/world_clock.git
```

SSH Key:

```bash
git clone git@github.com:ecubed99/world_clock.git
```

---

# Running

## Launch manually.

```bash
python3 clock.py
```

If from SSH session, you have to define the display environment. Depending on setups, this command generally works If not you will have to get into the weyland and XDG settings, which are outside the scope of this project.

```bash
DISPLAY=:0 python3 clock.py
```

## Set to launch on boot

modify run_clock.sh to match your install location

then choose your preferred startup method below

### labwc

See the section on autorotation, it both fixes rotation and automatically starts the appliance.

### crontab

make run_clock.sh executable (if it isn't already)

```bash
chmod +x run_clock.sh
```
Edit your crontab settings

```bash
crontab -e
```

Add a line like this with your script location:

```bash
@reboot /path/to/run_clock.sh
```

---

# Display Rotation and Autostart

The project has been tested on Raspberry Pi OS 13.5 trixie using the Wayland/LabWC desktop.

Both display rotation and automatic startup are configured through the LabWC autostart file.

Create the directory if it does not already exist:

```bash
mkdir -p ~/.config/labwc
```

Edit:

```bash
nano ~/.config/labwc/autostart
```

Example:

```text
wlr-randr --output DSI-1 --transform 180
/home/pi/timezone-clock/run_clock.sh &
```

On login, LabWC will:

1. Rotate the display.
2. Launch the timezone clock.

---

## Determining the Display Name

The output name (`DSI-1`, `HDMI-A-1`, etc.) is hardware dependent.

List available outputs with:

```bash
wlr-randr
```
If you are in an SSH terminal, the following commands may be required:

```bash
# Find the active user's runtime directory
export XDG_RUNTIME_DIR=/run/user/$(id -u)

# Set the Wayland display socket
export WAYLAND_DISPLAY=wayland-0

# Now run wlr-randr
wlr-randr
```

Relevant outputs:

```text
DSI-1
  800x480
  Enabled

HDMI-A-1
  1920x1080
  Disabled
```

Use the output name shown by `wlr-randr` in the rotation command.

Examples:

Rotate the DSI display:

```bash
wlr-randr --output DSI-1 --transform 180
```

Rotate an HDMI monitor:

```bash
wlr-randr --output HDMI-A-1 --transform 180
```

---

## Available Rotations

| Rotation | Command |
|---|---|
| Normal orientation | `--transform normal` |
| Rotate 90° clockwise | `--transform 90` |
| Rotate 180° | `--transform 180` |
| Rotate 270° | `--transform 270` |

---

## Testing Rotation

You can test a rotation without rebooting:

```bash
wlr-randr --output DSI-1 --transform 180
```

If the display looks correct, add the command to the LabWC autostart file.

---

## Reboot

After editing the autostart file:

```bash
sudo reboot
```

The display should rotate automatically and the clock should launch immediately after login.

---

# Configuration

All user configuration lives in

```
config.yaml
```

The application automatically reloads this file when it changes.

No restart is required.

Example config file:

```yaml
use_24h: true
draw_connector_lines: false
show_map_labels: false

theme:
  night_alpha: 155
  twilight_degrees: 12

cities:
  - name: Cleveland
    timezone: America/New_York
    lat: 41.4993
    lon: -81.6944

  - name: Texas
    timezone: America/Chicago
    lat: 32.7767
    lon: -96.7970
```

---

# Web Configuration

The application starts a small Flask web server.

Browse to

```
http://<pi-hostname>:8080
```

or

```
http://<pi-ip>:8080
```

Features include:

- Search for locations
- Automatic GPS lookup
- Automatic timezone lookup
- Add cities
- Remove cities
- Reorder cities
- Automatic display update

---

# Assets

Currently required:

```
assets/ne_110m_land.geojson
```

This contains the Natural Earth coastline polygons used for rendering.

---

# Screenshots

You are able to take screenshots of the clock display, even from an SSH session using grim and display them over x11 with feh.

Install the utilities.

```bash
sudo apt install grim feh
```

Take a screenshot from SSH (you may need to adjust the display environment variables).

```bash
sudo -u pi \
XDG_RUNTIME_DIR=/run/user/1000 \
WAYLAND_DISPLAY=wayland-0 \
grim /tmp/screencap.png
```

Display the captured image.

```bash
feh /tmp/screencap.png
```

---

# Development

The project is split into modules.

| Module | Responsibility |
|---------|----------------|
| astronomy.py | Solar calculations |
| config.py | YAML loading |
| display.py | Main display layout |
| icons.py | Sun/moon icons |
| map_renderer.py | World map rendering |
| web_config.py | Flask configuration UI |

---
