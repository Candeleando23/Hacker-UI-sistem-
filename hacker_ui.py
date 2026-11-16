#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
N E X U S  //  G H O S T W I R E   —   interfaz "hacker de película"
=====================================================================
Los comandos ofensivos (hack, ddos, sqli, exploit, wifi...) son TEATRO: no envían nada.
Los paneles NET INTEL / THREAT FEED y los comandos de "red real" (myip, ping, dns, ssl,
headers, cve, kev, speedtest, rtrace, lscan) usan tu internet SOLO para leer/medir.
Solo usa la librería estándar (tkinter). Ejecuta:

    python hacker_ui.py            (con internet)
    python hacker_ui.py --offline  (sin tocar la red: paneles con datos demo)

Teclas:  F11 pantalla completa | Esc salir de pantalla completa
         F2 cambiar tema | F3 alarma | F4 lanzar intrusión | F5 minijuego | F1 ayuda
         F6 modo Windows (cmd REAL, separado de NEXUS) | F7 voz de Nova on/off | F8 efecto matrix
v9: 'win' = comandos reales de Windows · 'ssh' = shell remoto simulado · 'nova' = charla con la IA
    'voz on' = Nova habla (SAPI de Windows; 'voz instalar' añade voz neuronal) · 'rank' · 'briefing'

Escribe comandos en la terminal (prueba: help, hack, scan, trace, crack ...)
"""
import tkinter as tk
import tkinter.font as tkfont
import math, random, time, string, platform, socket, os, sys, hashlib
import itertools, collections, datetime, base64, traceback, inspect, threading
from functools import lru_cache
import urllib.request, ssl, json, subprocess, queue, ctypes
import re, unicodedata, ast, operator, tempfile, atexit, shutil, importlib, importlib.util

APP = "NEXUS"
VERSION = "9.0.0"

# ════════════════════════════════════════════════════════════════════
#  COLORES / TEMAS
# ════════════════════════════════════════════════════════════════════
def _h2r(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


@lru_cache(maxsize=8192)
def _mix(a, b, q):
    t = q / 32.0
    ra, rb = _h2r(a), _h2r(b)
    return "#%02x%02x%02x" % tuple(
        int(max(0, min(255, ra[i] + (rb[i] - ra[i]) * t))) for i in range(3))


def mix(a, b, t):
    """Mezcla de color a->b (t 0..1)."""
    return _mix(a, b, int(round(max(0.0, min(1.0, t)) * 32)))


THEMES = {
    "MATRIX": dict(bg="#010806", fg="#19ff7a", dim="#0b8a43", faint="#063a21",
                   hi="#d6ffe6", acc="#00e5ff", warn="#ffd000", bad="#ff2d55"),
    "CYBER":  dict(bg="#010610", fg="#2ee6ff", dim="#127fa0", faint="#093348",
                   hi="#e0fbff", acc="#ff3df2", warn="#ffd000", bad="#ff2d55"),
    "AMBER":  dict(bg="#0a0600", fg="#ffb000", dim="#9a6a00", faint="#3d2900",
                   hi="#fff1c7", acc="#00e5ff", warn="#ffe14a", bad="#ff3b30"),
    "BLOOD":  dict(bg="#0c0203", fg="#ff3b4e", dim="#9c1f2d", faint="#401015",
                   hi="#ffd9de", acc="#ffd000", warn="#ffb000", bad="#ffffff"),
    "VAPOR":  dict(bg="#07020d", fg="#c46bff", dim="#6d2fa3", faint="#2d1245",
                   hi="#f6e6ff", acc="#00f5d4", warn="#ffd000", bad="#ff2d6f"),
    "GHOST":  dict(bg="#050607", fg="#d5dde3", dim="#737c85", faint="#262b30",
                   hi="#ffffff", acc="#7fd1ff", warn="#ffd000", bad="#ff4d4d"),
}
THEME_ORDER = ["MATRIX", "CYBER", "AMBER", "VAPOR", "GHOST"]


class Theme:
    def __init__(self):
        self.subs = []
        self.name = "MATRIX"
        self._apply()

    def _apply(self):
        for k, v in THEMES[self.name].items():
            setattr(self, k, v)

    def set(self, name):
        name = name.upper()
        if name in THEMES:
            self.name = name
            self._apply()
            for cb in self.subs:
                try:
                    cb()
                except Exception:
                    pass
            return True
        return False


T = Theme()


class _UI:  # fuentes y métricas globales
    pass


UI = _UI()


def init_ui(root):
    fams = set(tkfont.families(root))
    fam = "Courier"
    for f in ("JetBrains Mono", "Cascadia Mono", "Consolas", "Menlo", "DejaVu Sans Mono",
              "Liberation Mono", "Courier New", "Courier"):
        if f in fams:
            fam = f
            break
    sw = root.winfo_screenwidth()
    base = 8 if sw < 1400 else (9 if sw < 1900 else 11)
    mk = lambda s, w="normal": tkfont.Font(root=root, family=fam, size=s, weight=w)
    UI.fam = fam
    UI.fs, UI.fsb = mk(base - 1), mk(base - 1, "bold")
    UI.fm, UI.fb = mk(base), mk(base, "bold")
    UI.fl = mk(base + 3, "bold")
    UI.fh = mk(base + 13, "bold")
    UI.fx = mk(base + 26, "bold")
    UI.cws = UI.fs.measure("0")
    UI.cwm = UI.fm.measure("0")
    UI.lhs = UI.fs.metrics("linespace")
    UI.lhm = UI.fm.metrics("linespace")


# ════════════════════════════════════════════════════════════════════
#  DATOS / UTILIDADES
# ════════════════════════════════════════════════════════════════════
def rip():
    return "%d.%d.%d.%d" % (random.choice([10, 45, 62, 77, 81, 91, 103, 128, 142, 172, 185, 193, 203, 212]),
                            random.randint(0, 255), random.randint(0, 255), random.randint(1, 254))


def rhex(n):
    return "".join(random.choice("0123456789abcdef") for _ in range(n))


def rpass(n):
    return "".join(random.choice(string.ascii_letters + string.digits + "!@#$%&*?") for _ in range(n))


def md5(s):
    return hashlib.md5(s.encode()).hexdigest()


ADJ = ["SILENT", "CRIMSON", "HOLLOW", "VELVET", "NEON", "BROKEN", "FROZEN", "PHANTOM", "SCARLET",
       "ELECTRIC", "MIDNIGHT", "COBALT", "SHATTERED", "LUCID", "FERAL", "OBSIDIAN"]
NOUN = ["LOTUS", "HARVEST", "MIRAGE", "COMET", "SERPENT", "CATHEDRAL", "TIDE", "ORCHID", "ECLIPSE",
        "LANTERN", "MERIDIAN", "GARDEN", "ORACLE", "VORTEX", "PRISM", "ANTHEM"]
TARGETS = ["aurora-corp.net", "helix-labs.io", "orbital-bank.int", "meridian-grid.gov.xx",
           "blackwater-media.tv", "vanta-logistics.com", "cipher-health.org", "ironwood-energy.biz"]
PHASES = ["RECON", "WEAPONIZE", "DELIVER", "EXPLOIT", "INSTALL", "C2 LINK", "EXFIL"]

CITIES = {  # código: (lat, lon, nombre)
    "HAV": (23.1, -82.4, "Havana"), "NYC": (40.7, -74.0, "New York"), "LAX": (34.0, -118.2, "Los Angeles"),
    "SEA": (47.6, -122.3, "Seattle"), "YYZ": (43.7, -79.4, "Toronto"), "MEX": (19.4, -99.1, "Mexico City"),
    "BOG": (4.7, -74.1, "Bogota"), "LIM": (-12.0, -77.0, "Lima"), "SAO": (-23.5, -46.6, "Sao Paulo"),
    "BUE": (-34.6, -58.4, "Buenos Aires"), "LON": (51.5, -0.1, "London"), "PAR": (48.9, 2.35, "Paris"),
    "BER": (52.5, 13.4, "Berlin"), "MAD": (40.4, -3.7, "Madrid"), "MOW": (55.7, 37.6, "Moscow"),
    "CAI": (30.0, 31.2, "Cairo"), "LOS": (6.5, 3.4, "Lagos"), "JNB": (-26.2, 28.0, "Johannesburg"),
    "NBO": (-1.3, 36.8, "Nairobi"), "DXB": (25.2, 55.3, "Dubai"), "BOM": (19.0, 72.9, "Mumbai"),
    "DEL": (28.6, 77.2, "Delhi"), "SIN": (1.35, 103.8, "Singapore"), "HKG": (22.3, 114.2, "Hong Kong"),
    "PEK": (39.9, 116.4, "Beijing"), "TYO": (35.7, 139.7, "Tokyo"), "SYD": (-33.9, 151.2, "Sydney"),
    "REK": (64.1, -21.9, "Reykjavik"),
}

COASTS = [
    # Norteamérica
    [(-168, 65), (-155, 71), (-125, 70), (-95, 72), (-80, 70), (-64, 60), (-56, 52), (-66, 45), (-70, 42),
     (-76, 35), (-81, 31), (-80, 25), (-83, 29), (-90, 30), (-97, 26), (-97, 21), (-92, 18), (-88, 21),
     (-87, 15), (-83, 10), (-79, 8), (-86, 12), (-92, 15), (-97, 16), (-105, 20), (-110, 24), (-115, 30),
     (-117, 33), (-121, 35), (-124, 40), (-124, 47), (-128, 51), (-135, 57), (-145, 60), (-152, 59),
     (-165, 55), (-163, 60), (-166, 63)],
    # Sudamérica
    [(-78, 8), (-72, 12), (-62, 10), (-52, 5), (-50, 0), (-44, -2), (-35, -6), (-39, -14), (-41, -22),
     (-48, -26), (-54, -34), (-58, -38), (-65, -41), (-66, -47), (-69, -52), (-72, -54), (-75, -48),
     (-73, -40), (-71, -30), (-70, -18), (-76, -14), (-81, -5), (-80, 0)],
    # África
    [(-17, 21), (-10, 30), (-6, 36), (10, 37), (11, 33), (20, 32), (32, 31), (35, 28), (38, 18), (43, 12),
     (51, 12), (48, 5), (40, -3), (40, -10), (35, -20), (33, -26), (27, -34), (20, -35), (17, -30),
     (12, -18), (13, -9), (9, -1), (9, 4), (4, 6), (-7, 4), (-13, 8), (-17, 14)],
    # Eurasia
    [(-9, 37), (-9, 43), (-2, 43.5), (-1, 46), (-4.5, 48), (-1, 49), (2, 51), (5, 53), (8.5, 54), (8.5, 57),
     (10.5, 57.5), (10, 55), (12, 54.5), (14, 54), (21, 55), (24, 59.5), (28, 60), (22, 60.5), (21, 64),
     (25, 65.5), (18, 63), (17, 60), (11, 58), (8, 58), (5, 60), (5, 62), (14, 67), (20, 70), (30, 71),
     (40, 67), (44, 68), (60, 69), (70, 73), (80, 73), (100, 77), (113, 74), (130, 71), (142, 72),
     (160, 70), (170, 70), (180, 68), (180, 65), (172, 64), (164, 60), (162, 58), (156, 51), (143, 59),
     (137, 54), (141, 52), (140, 48), (135, 43), (130, 42), (129, 35), (126, 34), (126, 38), (122, 40),
     (118, 38), (121, 37), (122, 30), (120, 24), (110, 20), (108, 16), (109, 12), (105, 9), (100, 13),
     (100, 8), (103, 1.5), (98, 8), (98, 16), (94, 16), (92, 22), (88, 22), (80, 15), (77, 8), (73, 17),
     (70, 22), (67, 25), (57, 25.5), (56, 27), (50, 30), (48, 29.5), (50, 26), (52, 24), (56, 26),
     (58, 23), (55, 17), (52, 16), (43, 13), (39, 21), (35, 28), (34.5, 31), (36, 36), (30, 36.5),
     (27, 37), (26, 40), (23, 38), (22, 37), (21, 39), (19, 41), (16, 43), (13.5, 45.5), (12.3, 45),
     (14, 42), (18, 40), (16, 38), (15.5, 38), (12, 42), (10, 44), (8, 44), (4, 43.5), (3, 42), (0, 39),
     (-1, 37.5), (-5, 36)],
    # Australia
    [(114, -22), (122, -18), (130, -12), (137, -12), (142, -11), (146, -19), (153, -26), (151, -34),
     (146, -39), (140, -38), (135, -34), (129, -32), (116, -35), (115, -30)],
    # Groenlandia
    [(-55, 60), (-44, 60), (-20, 70), (-20, 82), (-40, 83), (-60, 80), (-72, 78), (-55, 70)],
    # Reino Unido, Japón, Madagascar, Cuba, Islandia, Sumatra, Borneo, Nueva Zelanda
    [(-5, 50), (1, 51), (-2, 56), (-5, 58), (-6, 55), (-3, 54)],
    [(130, 31), (135, 34), (140, 36), (142, 40), (141, 45), (140, 41), (136, 36), (131, 34)],
    [(44, -25), (47, -25), (50, -15), (49, -12), (44, -17)],
    [(-85, 22), (-82, 23), (-77, 21), (-74, 20), (-77, 20), (-82, 22)],
    [(-24, 65), (-18, 66.5), (-14, 65), (-18, 63.5)],
    [(95, 5), (98, 4), (104, -2), (106, -6), (102, -4), (97, 1)],
    [(109, 2), (114, 5), (119, 6), (117, 0), (116, -4), (111, -3), (109, -1)],
    [(173, -35), (178, -38), (175, -41), (172, -44), (168, -46), (171, -42), (174, -40)],
]


def subdivide(poly, step=5.0):
    out = []
    pts = list(poly) + [poly[0]]
    for (lo1, la1), (lo2, la2) in zip(pts, pts[1:]):
        n = max(1, int(max(abs(lo2 - lo1), abs(la2 - la1)) / step))
        for i in range(n):
            out.append((lo1 + (lo2 - lo1) * i / n, la1 + (la2 - la1) * i / n))
    out.append(pts[-1])
    return out


def vec(lat, lon):
    la, lo = math.radians(lat), math.radians(lon)
    return (math.cos(la) * math.sin(lo), math.sin(la), math.cos(la) * math.cos(lo))


PROC_NAMES = ["kernel_task", "ghostd", "sshd", "nxcore", "packet_sniffer", "rootkitd", "tor-relay",
              "cryptd", "wormhole", "dbus-daemon", "watchdog", "bruteforce.py", "exfil-agent",
              "zeroday-loader", "arp-spoofd", "keylogd", "mixnet", "stegano", "dns-tunnel", "sentinel"]
SUSPICIOUS = {"rootkitd", "bruteforce.py", "exfil-agent", "zeroday-loader", "keylogd", "arp-spoofd", "dns-tunnel"}

LOG_TEMPLATES = [
    ("INFO", "SSH handshake {ip}:{p} -> {ip2}"), ("INFO", "DNS resolved {host} -> {ip}"),
    ("INFO", "TLS 1.3 tunnel up via {city}"), ("INFO", "Heartbeat from implant {hx}"),
    ("INFO", "Proxy hop {city} > {city2} established"), ("INFO", "Packet capture rotated ({n} MB)"),
    ("WARN", "Port scan detected from {ip} ({n} pps)"), ("WARN", "Anomalous packet size {n}B from {ip}"),
    ("WARN", "IDS signature NX-{n} triggered"), ("WARN", "Latency spike on link {city}-{city2}"),
    ("CRIT", "Firewall rule bypassed on {ip}"), ("CRIT", "Honeypot tripped by {ip}"),
    ("CRIT", "Unauthorized root session on {ip2}"),
    ("OK", "Payload delivered to {ip} [{n} bytes]"), ("OK", "Session key rotated (AES-256-GCM)"),
    ("OK", "Proxy chain re-routed: {city} > {city2} > {city3}"), ("OK", "Credential cache synced ({n} items)"),
    ("OK", "Exfil chunk {n}/512 acknowledged"),
]

BOOT_LINES = [
    "NEXUS BIOS v9.0.0  (c) Ghostwire Systems",
    "CPU: GW-QX9 @ 4.80GHz x16 ........................... OK",
    "MEM: 65536 MB ECC ................................... OK",
    "GPU: NX-Tensor 24G (cuda-compatible) ................. OK",
    "Detecting storage: nvme0n1 [2TB] ..................... OK",
    "Loading kernel 6.9.0-ghost #1 SMP PREEMPT ............ OK",
    "Mounting encrypted volumes (LUKS2) ................... OK",
    "Starting systemd-ghostd ............................. [ OK ]",
    "Starting cryptd (AES-NI, VAES) ...................... [ OK ]",
    "Starting packet engine (AF_XDP) ..................... [ OK ]",
    "Starting tor/i2p/mixnet relays ...................... [ OK ]",
    "Spoofing MAC address ................................ [ OK ]",
    "Wiping logs: /var/log/* ............................. [ OK ]",
    "Initializing neural exploit generator ............... [ OK ]",
    "Checking uplink SAT-07 .............................. [ LOCKED ]",
    "Calibrating radar array ............................. [ OK ]",
    "Loading zero-day cache (3 items) .................... [ OK ]",
    "WARNING: no watchdog found. Continuing in stealth mode.",
]

DICT_WORDS = ["admin", "password", "123456", "qwerty", "letmein", "dragon", "master", "monkey", "hello",
              "secret", "root", "toor", "welcome", "login", "abc123", "iloveyou", "sunshine", "princess",
              "football", "shadow", "trustno1", "batman", "ghost", "nexus", "hacker", "cuba", "fidel"]

FILES = {
    "mission.txt": "OPERATION: classified\nEvery target in this system is fictional.\nNothing here touches the network.\nTip: try `cat shadow.bak` and then `crack <hash>` (it's real!).",
    "shadow.bak": "root:%s\nadmin:%s\ndave:%s\nghost:%s" % (md5("toor"), md5("admin"), md5("qwerty"), md5("x9k2")),
    "contacts.db": "[binary SQLite database - 4096 bytes]\nrecords: 1337   encrypted: yes",
    "vault.enc": "[AES-256 encrypted container - run: decrypt vault.enc]",
    "notes.log": "03:14 - dropped implant on edge router\n03:41 - they noticed. relax.\n04:02 - coffee.",
}


# ════════════════════════════════════════════════════════════════════
#  ESTADO GLOBAL SIMULADO
# ════════════════════════════════════════════════════════════════════
class Stats:
    def __init__(self):
        self.cpu = [random.uniform(10, 40) for _ in range(8)]
        self.mem = 48.0
        self.temp = 52.0
        self.net_in = collections.deque([20.0] * 120, maxlen=120)
        self.net_out = collections.deque([8.0] * 120, maxlen=120)
        self.load = 0.0
        self.real = False

    def update(self):
        ld = self.load
        rc = REAL.cpu()
        self.real = rc is not None
        for i in range(8):
            if rc is not None:
                target = rc * 0.92 + 25 * ld + random.uniform(-9, 11)
            else:
                target = 22 + 60 * ld + random.uniform(-10, 18)
            self.cpu[i] += (target - self.cpu[i]) * 0.2 + random.uniform(-4, 4)
            self.cpu[i] = max(2, min(100, self.cpu[i]))
        rm = REAL.mem()
        if rm:
            self.mem += (rm[0] - self.mem) * 0.2
        else:
            self.mem = max(30, min(93, self.mem + random.uniform(-0.5, 0.55) + ld * 0.15))
        avg = sum(self.cpu) / 8
        self.temp += (36 + avg * 0.45 - self.temp) * 0.1
        spike = random.random() < 0.06
        self.net_in.append(max(0.5, self.net_in[-1] * 0.7 + random.uniform(2, 30 + 90 * ld) * (3 if spike else 1)))
        self.net_out.append(max(0.5, self.net_out[-1] * 0.7 + random.uniform(1, 14 + 50 * ld)))
        self.load *= 0.97


class Mission:
    def __init__(self, app):
        self.app = app
        self.new()

    def new(self, target=None):
        self.op = "%s %s" % (random.choice(ADJ), random.choice(NOUN))
        self.target = target or random.choice(TARGETS)
        self.ip = rip()
        self.p = [0.0] * 7
        self.manual = False
        self.trace = random.uniform(4, 15)
        self.stealth = random.uniform(70, 95)
        self.done_at = None

    @property
    def active(self):
        for i, v in enumerate(self.p):
            if v < 100:
                return i
        return 6

    def update(self):
        now = time.time()
        if self.done_at:
            if now - self.done_at > 8:
                self.new()
            return
        if not self.manual:
            i = self.active
            self.p[i] = min(100, self.p[i] + random.uniform(0.15, 0.75))
            self.trace = max(2, min(70, self.trace + random.uniform(-0.35, 0.4)))
            self.stealth = max(20, min(99, self.stealth + random.uniform(-0.5, 0.5)))
            if all(v >= 100 for v in self.p):
                self.complete()
        else:
            self.trace = max(0, self.trace + random.uniform(-0.15, 0.15))
        if self.trace >= 100:
            self.burned()

    def complete(self):
        if self.done_at:
            return
        self.p = [100.0] * 7
        self.done_at = time.time()
        self.app.banner("ACCESS GRANTED", "%s  ::  %s" % (self.op, self.target), "ok", 4.5)
        self.app.log("OK", "Operation %s complete. Root on %s" % (self.op, self.target))
        try:
            self.app.nova.narrate("mission_done", prio=2, target=self.target)
            self.app.add_xp(60, "op")
        except Exception:
            pass

    def burned(self):
        self.app.alarm("TRACE COMPLETE", "CONNECTION BURNED // REROUTING")
        self.new()
        self.trace = 15.0


# ════════════════════════════════════════════════════════════════════
#  PANEL BASE (Canvas con marco futurista)
# ════════════════════════════════════════════════════════════════════
class Panel(tk.Canvas):
    TITLE = "PANEL"
    FPS = 20

    def __init__(self, master, app, title=None, fps=None):
        super().__init__(master, bg=T.bg, highlightthickness=0, bd=0, width=10, height=10)
        self.app = app
        self.title = title or self.TITLE
        self.interval = int(1000 / (fps or self.FPS))
        self.W = self.H = 0
        self.t0 = time.time()
        self.now = 0.0
        self._bg = None
        self.ix0 = self.iy0 = 0
        self.ix1 = self.iy1 = 10
        self.on_init()
        self.after(random.randint(80, 500), self._loop)

    def on_init(self):
        pass

    def tag_text(self):
        return ""

    def _loop(self):
        try:
            if not self.winfo_exists():
                return
        except tk.TclError:
            return
        t_start = time.perf_counter()
        w, h = self.winfo_width(), self.winfo_height()
        if w > 60 and h > 40 and not self.app.paused:
            self.W, self.H = w, h
            if self._bg != T.bg:
                self.configure(bg=T.bg)
                self._bg = T.bg
            self.delete("all")
            self.now = time.time() - self.t0
            try:
                self.draw_frame()
                self.draw(self.ix0, self.iy0, self.ix1, self.iy1)
            except tk.TclError:
                pass
            except Exception:
                self.app.report_error(self)
        dt = int((time.perf_counter() - t_start) * 1000)
        try:
            self.after(max(5, self.interval - dt), self._loop)
        except tk.TclError:
            pass

    def draw_frame(self):
        w, h, c = self.W, self.H, 10
        self.create_polygon([c, 1, w - 1, 1, w - 1, h - c - 1, w - c - 1, h - 1, 1, h - 1, 1, c],
                            outline=T.faint, fill="")
        self.create_line(1, c + 12, 1, c, c, 1, c + 20, 1, fill=T.dim, width=2)
        self.create_line(w - 1, h - c - 14, w - 1, h - c - 1, w - c - 1, h - 1, w - c - 22, h - 1,
                         fill=T.dim, width=2)
        on = int(self.now * 2) % 2 == 0
        self.create_rectangle(14, 8, 20, 14, fill=T.fg if on else T.faint, outline="")
        self.create_text(26, 11, text=self.title, anchor="w", fill=T.fg, font=UI.fsb)
        self.create_text(w - 14, 11, text=self.tag_text(), anchor="e", fill=T.dim, font=UI.fs)
        self.create_line(12, 22, w - 12, 22, fill=T.faint)
        self.ix0, self.iy0, self.ix1, self.iy1 = 12, 28, w - 12, h - 10

    def draw(self, x0, y0, x1, y1):
        pass


# ════════════════════════════════════════════════════════════════════
#  CABECERA Y PIE
# ════════════════════════════════════════════════════════════════════
class Header(Panel):
    FPS = 10

    def on_init(self):
        self.host = socket.gethostname()[:18]
        self.user = (os.environ.get("USER") or os.environ.get("USERNAME") or "ghost")[:14]
        self.session = "0x" + rhex(4).upper()

    def draw_frame(self):
        self.ix0, self.iy0, self.ix1, self.iy1 = 0, 0, self.W, self.H

    def draw(self, x0, y0, x1, y1):
        w, h = self.W, self.H
        m = self.app.mission
        self.create_line(0, h - 1, w, h - 1, fill=T.dim)
        self.create_line(0, h - 4, int(w * 0.35), h - 4, fill=T.faint)
        self.create_line(int(w * 0.65), h - 4, w, h - 4, fill=T.faint)
        glitch = (self.now % 9 < 0.25) or random.random() < 0.02
        ox = random.randint(-3, 3) if glitch else 0
        logo = "N E X U S"
        if glitch:
            self.create_text(20 + ox + 2, h // 2 - 5, text=logo, anchor="w", fill=T.bad, font=UI.fh)
            self.create_text(20 - ox - 2, h // 2 - 5, text=logo, anchor="w", fill=T.acc, font=UI.fh)
        self.create_text(20, h // 2 - 5, text=logo, anchor="w", fill=T.hi if glitch else T.fg, font=UI.fh)
        lw = UI.fh.measure(logo)
        if w > 1100:
            sx = 20 + lw + 20
            self.create_text(sx, h // 2 - 12, text="GHOSTWIRE TERMINAL v%s" % VERSION, anchor="w",
                             fill=T.fg, font=UI.fsb)
            self.create_text(sx, h // 2 + 4, text="SESSION %s // NODE %s // USER %s" % (self.session, self.host, self.user),
                             anchor="w", fill=T.dim, font=UI.fs)
            self.create_text(sx, h // 2 + 18, text="ENC AES-256-GCM // PROXY x7 // %s // %s" % (T.name, self.app.rank_label()),
                             anchor="w", fill=T.dim, font=UI.fs)
        # centro: operación
        i = m.active
        cx = w * 0.56 if w > 1100 else w * 0.5
        self.create_text(cx, h // 2 - 10, text="OPERATION  %s" % m.op, fill=T.hi, font=UI.fl)
        self.create_text(cx, h // 2 + 12, text="TARGET %s [%s]  ::  PHASE %d/7 %s" % (m.target, m.ip, i + 1, PHASES[i]),
                         fill=T.dim, font=UI.fs)
        # derecha: reloj
        now = datetime.datetime.now()
        self.create_text(w - 20, h // 2 - 8, text=now.strftime("%H:%M:%S"), anchor="e", fill=T.fg, font=UI.fh)
        up = int(time.time() - self.app.start)
        self.create_text(w - 20, h // 2 + 16, text="%s  UP %02d:%02d:%02d" % (now.strftime("%Y-%m-%d"), up // 3600, up % 3600 // 60, up % 60),
                         anchor="e", fill=T.dim, font=UI.fs)
        # nivel de amenaza
        lvl = int(min(5, m.trace / 20.0 + 0.999)) if m.trace > 0 else 0
        bx = w - 20 - UI.fh.measure("00:00:00") - 70
        self.create_text(bx - 4, 12, text="THREAT", anchor="e", fill=T.dim, font=UI.fs)
        for k in range(5):
            col = [T.fg, T.fg, T.warn, T.warn, T.bad][k] if k < lvl else T.faint
            self.create_rectangle(bx + k * 12, 8, bx + k * 12 + 9, 28, fill=col, outline="")
        if int(self.now * 2) % 2 == 0:
            self.create_oval(bx, 36, bx + 8, 44, fill=T.bad, outline="")
        self.create_text(bx + 14, 40, text="REC", anchor="w", fill=T.bad if int(self.now * 2) % 2 == 0 else T.dim, font=UI.fs)


class Footer(Panel):
    FPS = 30
    ITEMS = ["NEXUS GHOSTWIRE v%s // ALL SYSTEMS NOMINAL" % VERSION, "UPLINK SAT-07 LOCKED // 14ms",
             "ZERO-DAY CACHE: 3 ITEMS", "PROXY CHAIN: 7 HOPS // TOR / I2P / MIXNET",
             "WATCHDOG: SLEEPING", "ENTROPY POOL: 4096 BITS", "FIREWALL EVASION: ACTIVE",
             "MAC ADDRESS: SPOOFED", "LOG WIPER: RUNNING", "TYPE 'help' FOR COMMANDS"]

    def on_init(self):
        self.off = 0.0

    def draw_frame(self):
        self.ix0, self.iy0, self.ix1, self.iy1 = 0, 0, self.W, self.H

    def draw(self, x0, y0, x1, y1):
        w, h = self.W, self.H
        m = self.app.mission
        txt = "   ◆   ".join(self.ITEMS + ["TARGET %s" % m.target, "TRACE %d%%" % m.trace, "STEALTH %d%%" % m.stealth]) + "   ◆   "
        tw = UI.fs.measure(txt)
        self.off = (self.off + 1.6) % tw
        x = -self.off
        while x < w:
            self.create_text(x, h // 2, text=txt, anchor="w", fill=T.dim, font=UI.fs)
            x += tw
        hint = " F1 HELP  F2 THEME  F4 HACK  F5 GAME  F6 WIN  F7 VOZ  F8 MATRIX  F11 FULL "
        hw = UI.fsb.measure(hint)
        self.create_rectangle(w - hw - 10, 0, w, h, fill=T.bg, outline="")
        self.create_line(w - hw - 10, 2, w - hw - 10, h - 2, fill=T.dim)
        self.create_text(w - 6, h // 2, text=hint, anchor="e", fill=T.fg, font=UI.fsb)
        self.create_line(0, 0, w, 0, fill=T.dim)


# ════════════════════════════════════════════════════════════════════
#  LLUVIA DE SEÑAL
# ════════════════════════════════════════════════════════════════════
class RainPanel(Panel):
    TITLE = "SIGNAL RAIN"
    FPS = 18
    GL = list("ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ") + list("0123456789ABCDEF<>/|=+*:;")

    def on_init(self):
        self.drops = []
        self.gkey = None
        self.grad = []

    def tag_text(self):
        return "RX 2.4GHz"

    def _new(self, nrows, init=False):
        return dict(y=random.uniform(-nrows, nrows) if init else random.uniform(-nrows * 0.6, 0),
                    v=random.uniform(0.25, 0.9), ln=random.randint(6, 18),
                    g=[random.choice(self.GL) for _ in range(64)])

    def draw(self, x0, y0, x1, y1):
        cw, lh = max(10, UI.cwm + 3), UI.lhm
        ncols = max(1, (x1 - x0) // cw)
        nrows = max(1, (y1 - y0 - 18) // lh)
        if self.gkey != T.name:
            self.gkey = T.name
            self.grad = [mix(T.fg, T.bg, k / 15.0 * 0.92) for k in range(16)]
        while len(self.drops) < ncols:
            self.drops.append(self._new(nrows, True))
        del self.drops[ncols:]
        for i, d in enumerate(self.drops):
            d["y"] += d["v"]
            if d["y"] - d["ln"] > nrows:
                self.drops[i] = d = self._new(nrows)
            if random.random() < 0.15:
                d["g"][random.randrange(64)] = random.choice(self.GL)
            head = int(d["y"])
            x = x0 + i * cw + cw // 2
            for k in range(d["ln"]):
                row = head - k
                if 0 <= row < nrows:
                    col = T.hi if k == 0 else self.grad[min(15, 1 + int(k * 14 / d["ln"]))]
                    self.create_text(x, y0 + row * lh + lh // 2, text=d["g"][row % 64], fill=col, font=UI.fm)
        self.create_text(x0, y1 - 6, anchor="w", fill=T.dim, font=UI.fs,
                         text="DECODING STREAM 0x%s" % rhex(8).upper())


# ════════════════════════════════════════════════════════════════════
#  VOLCADO HEX
# ════════════════════════════════════════════════════════════════════
class HexPanel(Panel):
    TITLE = "MEMORY DUMP"
    FPS = 12

    def on_init(self):
        self.addr = random.randrange(0x7F0000000000, 0x7FFFFFFFFF00) & ~0xF
        self.rows = collections.deque()

    def tag_text(self):
        return "0x%08X" % (self.addr & 0xFFFFFFFF)

    def _row(self):
        r = (self.addr, os.urandom(16))
        self.addr += 16
        return r

    def draw(self, x0, y0, x1, y1):
        cw, lh = UI.cws, UI.lhs
        nrows = max(1, (y1 - y0) // lh)
        cols = (x1 - x0) // cw
        nb = max(4, ((cols - 10) // 4) // 4 * 4)
        nb = min(nb, 16)
        while len(self.rows) < nrows:
            self.rows.append(self._row())
        while len(self.rows) > nrows:
            self.rows.popleft()
        if random.random() < 0.5:
            self.rows.popleft()
            self.rows.append(self._row())
        hot = set((random.randrange(nrows), random.randrange(nb)) for _ in range(3))
        for r, (addr, data) in enumerate(self.rows):
            y = y0 + r * lh
            d = data[:nb]
            self.create_text(x0, y, text="%08X" % (addr & 0xFFFFFFFF), anchor="nw", fill=T.dim, font=UI.fs)
            hx = x0 + 10 * cw
            self.create_text(hx, y, text=" ".join("%02X" % b for b in d), anchor="nw", fill=T.fg, font=UI.fs)
            self.create_text(hx + (nb * 3 + 1) * cw, y, text="".join(chr(b) if 32 <= b < 127 else "." for b in d),
                             anchor="nw", fill=T.dim, font=UI.fs)
            for c in range(nb):
                if (r, c) in hot:
                    bx = hx + c * 3 * cw
                    self.create_rectangle(bx - 1, y, bx + 2 * cw + 1, y + lh, fill=T.fg, outline="")
                    self.create_text(bx, y, text="%02X" % d[c], anchor="nw", fill=T.bg, font=UI.fsb)


# ════════════════════════════════════════════════════════════════════
#  CRACKER DE CLAVES
# ════════════════════════════════════════════════════════════════════
class CrackPanel(Panel):
    TITLE = "KEY CRACKER"
    FPS = 15
    ALGOS = ["SHA-512", "BCRYPT $2b$12", "NTLMv2", "ARGON2id", "SCRYPT", "SHA3-256"]

    def on_init(self):
        self._reset()

    def tag_text(self):
        return self.algo

    def _reset(self):
        self.algo = random.choice(self.ALGOS)
        self.hash = rhex(64)
        self.n = 12
        self.secret = rpass(self.n)
        self.locked = 0
        self.attempts = random.randint(10 ** 6, 10 ** 8)
        self.next_lock = time.time() + random.uniform(0.8, 1.8)
        self.found_at = None

    def draw(self, x0, y0, x1, y1):
        job = self.app.crack_job
        now = time.time()
        lh = UI.lhs
        w = x1 - x0
        if job:
            hs, att = job["hash"], job["attempts"]
            n = max(8, len(job["found"] or ""))
            if job["found"]:
                chars, locked = list(job["found"].ljust(n)), len(job["found"])
            else:
                chars, locked = list(job["cand"].ljust(n)), 0
            found = bool(job["found"])
            alg = "MD5 (REAL)"
        else:
            if self.found_at is None:
                self.attempts += random.randint(2 * 10 ** 5, 9 * 10 ** 6)
                if now > self.next_lock:
                    self.locked += 1
                    self.next_lock = now + random.uniform(0.7, 1.9)
                    if self.locked >= self.n:
                        self.found_at = now
                        self.app.log("OK", "Key recovered (%s): %s" % (self.algo, self.secret))
            elif now - self.found_at > 2.4:
                self._reset()
            n, locked = self.n, self.locked
            chars = [self.secret[i] if i < locked else random.choice(string.ascii_letters + string.digits + "!@#$%")
                     for i in range(n)]
            found = self.found_at is not None
            hs, att, alg = self.hash, self.attempts, self.algo
        cpl = max(16, w // UI.cws)
        self.create_text(x0, y0, text="TARGET HASH", anchor="nw", fill=T.dim, font=UI.fs)
        y = y0 + lh
        for k in range(0, len(hs), cpl):
            self.create_text(x0, y, text=hs[k:k + cpl], anchor="nw", fill=T.fg, font=UI.fs)
            y += lh
        y += 4
        self.create_text(x0, y, text="%s   %.1f GH/s" % (alg, 2 + 6 * random.random()), anchor="nw", fill=T.acc, font=UI.fs)
        y += lh + 8
        sw = min(30, (w - 4) // n)
        bh = UI.fl.metrics("linespace") + 10
        for i in range(n):
            bx = x0 + i * sw
            lk = i < locked or found
            self.create_rectangle(bx + 1, y, bx + sw - 2, y + bh, outline=T.fg if lk else T.dim,
                                  fill=mix(T.bg, T.fg, 0.2) if lk else T.bg)
            self.create_text(bx + sw / 2, y + bh / 2, text=chars[i], fill=T.hi if lk else T.dim, font=UI.fl)
        y += bh + 8
        pct = 1.0 if found else locked / float(n)
        self.create_rectangle(x0, y, x1, y + 8, outline=T.dim)
        self.create_rectangle(x0 + 1, y + 1, x0 + 1 + (w - 2) * pct, y + 7, fill=T.fg, outline="")
        y += 14
        self.create_text(x0, y, text="ATTEMPTS %s" % format(att, ","), anchor="nw", fill=T.dim, font=UI.fs)
        y += lh + 2
        if found and int(now * 4) % 2 == 0:
            self.create_text(x0, y, text=">> KEY FOUND <<", anchor="nw", fill=T.hi, font=UI.fl)
        elif not found:
            self.create_text(x0, y, text="SEARCHING KEYSPACE...", anchor="nw", fill=T.dim, font=UI.fs)
        y += UI.fl.metrics("linespace") + 2
        # candidatos rápidos
        while y + lh < y1:
            self.create_text(x0, y, text="try: " + rpass(random.randint(8, 14)), anchor="nw",
                             fill=mix(T.dim, T.bg, random.random() * 0.6), font=UI.fs)
            y += lh


# ════════════════════════════════════════════════════════════════════
#  GLOBO 3D
# ════════════════════════════════════════════════════════════════════
class GlobePanel(Panel):
    TITLE = "GLOBAL TRACE // ORBITAL VIEW"
    FPS = 24

    def tag_text(self):
        return "LINKS %d   SATS 3" % len(self.arcs)

    def on_init(self):
        self.yaw = math.radians(80)
        self.tilt = math.radians(18)
        self.coast = [[vec(la, lo) for lo, la in subdivide(p)] for p in COASTS]
        self.graticule = [[vec(la, lo) for lo in range(-180, 181, 5)] for la in (-60, -30, 0, 30, 60)]
        self.graticule += [[vec(la, lo) for la in range(-85, 86, 5)] for lo in range(-180, 180, 30)]
        self.cv = {k: vec(v[0], v[1]) for k, v in CITIES.items()}
        self.arcs = []
        self.next_arc = 0
        self.last_t = time.time()
        self.sats = [dict(inc=math.radians(55), node=0.5, ph=0.0, sp=0.5, name="SAT-07"),
                     dict(inc=math.radians(98), node=2.2, ph=2.0, sp=0.38, name="SAT-12"),
                     dict(inc=math.radians(30), node=4.0, ph=4.0, sp=0.63, name="SAT-31")]

    def add_arc(self, a, b, kind="out"):
        if a == b or a not in self.cv or b not in self.cv:
            return
        A, B = self.cv[a], self.cv[b]
        dot = max(-1.0, min(1.0, sum(i * j for i, j in zip(A, B))))
        om = math.acos(dot)
        self.arcs.append(dict(a=a, b=b, A=A, B=B, om=om, t0=time.time(), dur=max(1.2, 0.9 + om * 1.3), kind=kind))
        if len(self.arcs) > 40:
            self.arcs.pop(0)

    def _rot(self, v):
        x, y, z = v
        x1 = x * self.cyw + z * self.syw
        z1 = -x * self.syw + z * self.cyw
        return x1, y * self.ct - z1 * self.st, y * self.st + z1 * self.ct

    def _poly(self, pts, color, width=1):
        run = []
        cx, cy, R = self.cx, self.cy, self.R
        for x, y, z in pts:
            if z > 0 or x * x + y * y > 1.0:
                run.append(cx + x * R)
                run.append(cy - y * R)
            else:
                if len(run) >= 4:
                    self.create_line(*run, fill=color, width=width)
                run = []
        if len(run) >= 4:
            self.create_line(*run, fill=color, width=width)

    def _arcpt(self, ar, t):
        om, A, B = ar["om"], ar["A"], ar["B"]
        s = math.sin(om)
        if om < 1e-4 or s < 1e-3:
            v = A
        else:
            k1, k2 = math.sin((1 - t) * om) / s, math.sin(t * om) / s
            v = (A[0] * k1 + B[0] * k2, A[1] * k1 + B[1] * k2, A[2] * k1 + B[2] * k2)
        alt = 1 + 0.25 * math.sin(math.pi * t) * min(1.0, om / 1.5)
        x, y, z = self._rot(v)
        return (x * alt, y * alt, z * alt)

    def _scr(self, p):
        return self.cx + p[0] * self.R, self.cy - p[1] * self.R

    def draw(self, x0, y0, x1, y1):
        now = time.time()
        dt = min(0.1, now - self.last_t)
        self.last_t = now
        self.yaw += math.radians(5) * dt
        self.cyw, self.syw = math.cos(self.yaw), math.sin(self.yaw)
        self.ct, self.st = math.cos(self.tilt), math.sin(self.tilt)
        self.cx, self.cy = (x0 + x1) / 2, (y0 + y1) / 2
        self.R = min(x1 - x0, y1 - y0) / 2 * 0.80
        cx, cy, R = self.cx, self.cy, self.R
        if now > self.next_arc:
            codes = list(CITIES)
            a = random.choice(codes) if random.random() < 0.6 else "HAV"
            b = random.choice(codes)
            kind = random.choice(["out", "out", "in", "sys"])
            if kind == "in":
                a, b = b, a
            self.add_arc(a, b, kind)
            self.next_arc = now + random.uniform(0.7, 2.0)
        # atmósfera y esfera
        for k, f in enumerate((1.07, 1.035)):
            self.create_oval(cx - R * f, cy - R * f, cx + R * f, cy + R * f, outline=mix(T.bg, T.fg, 0.12 + 0.1 * k))
        self.create_oval(cx - R, cy - R, cx + R, cy + R, fill=mix(T.bg, T.fg, 0.05), outline=T.dim)
        # anillo de marcas
        for i in range(72):
            a = math.radians(i * 5) + now * 0.15
            r1 = R * 1.12
            r2 = R * (1.12 + (0.035 if i % 6 == 0 else 0.015))
            self.create_line(cx + r1 * math.cos(a), cy + r1 * math.sin(a), cx + r2 * math.cos(a),
                             cy + r2 * math.sin(a), fill=T.dim if i % 6 == 0 else T.faint)
        # retícula
        for ln in self.graticule:
            self._poly([self._rot(v) for v in ln], T.faint)
        for poly in self.coast:
            self._poly([self._rot(v) for v in poly], T.fg)
        # meridiano de escaneo
        slon = (now * 35) % 360 - 180
        self._poly([self._rot(vec(la, slon)) for la in range(-85, 86, 5)], T.acc, 2)
        # satélites
        for s in self.sats:
            u = now * s["sp"] + s["ph"]
            ci, si = math.cos(s["inc"]), math.sin(s["inc"])
            ring = []
            for k in range(0, 64):
                uu = k / 63.0 * 2 * math.pi
                px, py, pz = math.cos(uu), 0.0, math.sin(uu)
                py2, pz2 = py * ci - pz * si, py * si + pz * ci
                cn, sn = math.cos(s["node"]), math.sin(s["node"])
                px2, pz3 = px * cn + pz2 * sn, -px * sn + pz2 * cn
                x, y, z = self._rot((px2, py2, pz3))
                ring.append((x * 1.3, y * 1.3, z * 1.3))
            self._poly(ring, T.faint)
            px, py, pz = math.cos(u), 0.0, math.sin(u)
            py2, pz2 = py * ci - pz * si, py * si + pz * ci
            cn, sn = math.cos(s["node"]), math.sin(s["node"])
            px2, pz3 = px * cn + pz2 * sn, -px * sn + pz2 * cn
            x, y, z = self._rot((px2, py2, pz3))
            x, y, z = x * 1.3, y * 1.3, z * 1.3
            if z > 0 or x * x + y * y > 1.0:
                sx, sy = cx + x * R, cy - y * R
                self.create_polygon(sx, sy - 4, sx + 4, sy, sx, sy + 4, sx - 4, sy, fill=T.warn, outline="")
                self.create_text(sx + 7, sy - 6, text=s["name"], anchor="w", fill=T.warn, font=UI.fs)
        # ciudades
        active = {}
        for ar in self.arcs:
            active[ar["a"]] = ar["kind"]
            active[ar["b"]] = ar["kind"]
        for code, v in self.cv.items():
            x, y, z = self._rot(v)
            if z > 0:
                sx, sy = cx + x * R, cy - y * R
                if code == "HAV":
                    rr = 5 + 2 * math.sin(now * 4)
                    self.create_oval(sx - rr, sy - rr, sx + rr, sy + rr, outline=T.hi)
                    self.create_text(sx + 8, sy + 8, text="HOME", anchor="w", fill=T.hi, font=UI.fsb)
                self.create_rectangle(sx - 1, sy - 1, sx + 2, sy + 2, fill=T.hi if code in active else T.acc, outline="")
                if code in active and code != "HAV":
                    self.create_text(sx + 5, sy - 6, text=code, anchor="w", fill=T.hi, font=UI.fs)
        # arcos
        colmap = {"out": T.acc, "in": T.bad, "sys": T.fg, "trace": T.warn}
        for ar in list(self.arcs):
            age = now - ar["t0"]
            p = min(1.0, age / ar["dur"])
            fade = 0.0 if age <= ar["dur"] else (age - ar["dur"]) / 1.6
            if fade >= 1:
                self.arcs.remove(ar)
                continue
            col = mix(colmap.get(ar["kind"], T.fg), T.bg, fade * 0.9)
            pts = [self._arcpt(ar, p * i / 28.0) for i in range(29)]
            self._poly(pts, col, 2 if ar["kind"] == "in" else 1)
            hx, hy, hz = pts[-1]
            if (hz > 0 or hx * hx + hy * hy > 1.0) and p < 1.0:
                sx, sy = self._scr(pts[-1])
                self.create_oval(sx - 3, sy - 3, sx + 3, sy + 3, fill=T.hi, outline="")
            if age > ar["dur"] and (age - ar["dur"]) < 1.4:
                x, y, z = self._rot(ar["B"])
                if z > 0:
                    sx, sy = cx + x * R, cy - y * R
                    rr = 3 + (age - ar["dur"]) * 18
                    self.create_oval(sx - rr, sy - rr, sx + rr, sy + rr,
                                     outline=mix(colmap.get(ar["kind"], T.fg), T.bg, (age - ar["dur"]) / 1.4))
        # HUD
        lon = (-math.degrees(self.yaw) + 180) % 360 - 180
        self.create_text(x0, y1 - 2, anchor="sw", fill=T.dim, font=UI.fs,
                         text="CENTER LAT %+.1f  LON %+.1f" % (math.degrees(self.tilt), lon))
        self.create_text(x0, y0, anchor="nw", fill=T.dim, font=UI.fs, text="ORBIT  LEO/MEO\nSCAN  %+.0f°" % slon)
        leg = [(T.acc, "OUTBOUND"), (T.bad, "INBOUND ATTACK"), (T.fg, "SYSTEM"), (T.warn, "TRACE ROUTE")]
        for k, (c, lbl) in enumerate(leg):
            yy = y0 + k * (UI.lhs + 1)
            self.create_rectangle(x1 - 112, yy + 3, x1 - 104, yy + 9, fill=c, outline="")
            self.create_text(x1 - 98, yy, anchor="nw", text=lbl, fill=T.dim, font=UI.fs)


# ════════════════════════════════════════════════════════════════════
#  ESPECTRO + OSCILOSCOPIO
# ════════════════════════════════════════════════════════════════════
class SpectrumPanel(Panel):
    TITLE = "SIGINT // SPECTRUM"
    FPS = 24

    def on_init(self):
        self.vals = [0.2] * 56
        self.peaks = [0.2] * 56

    def tag_text(self):
        return "CH1/CH2  %.1f MHz" % (433 + 20 * math.sin(self.now * 0.2))

    def draw(self, x0, y0, x1, y1):
        w, h = x1 - x0, y1 - y0
        half = w * 0.55
        n = len(self.vals)
        bw = half / n
        load = min(1.0, self.app.stats.load + 0.3)
        for i in range(n):
            base = 0.25 + 0.35 * math.sin(i * 0.3 + self.now * 2) ** 2 + random.random() * 0.4 * load
            self.vals[i] += (min(1, base) - self.vals[i]) * 0.35
            self.peaks[i] = max(self.peaks[i] - 0.01, self.vals[i])
            bh = self.vals[i] * h
            col = T.fg if self.vals[i] < 0.75 else (T.warn if self.vals[i] < 0.9 else T.bad)
            self.create_rectangle(x0 + i * bw + 1, y1 - bh, x0 + (i + 1) * bw - 1, y1, fill=col, outline="")
            py = y1 - self.peaks[i] * h
            self.create_line(x0 + i * bw + 1, py, x0 + (i + 1) * bw - 1, py, fill=T.hi)
        # osciloscopio
        ox0 = x0 + half + 14
        ox1 = x1
        cy = (y0 + y1) / 2
        self.create_rectangle(ox0, y0, ox1, y1, outline=T.faint)
        for k in range(1, 4):
            self.create_line(ox0, y0 + h * k / 4, ox1, y0 + h * k / 4, fill=T.faint)
        for k in range(1, 8):
            self.create_line(ox0 + (ox1 - ox0) * k / 8, y0, ox0 + (ox1 - ox0) * k / 8, y1, fill=T.faint)
        for ch, (col, fr, ph) in enumerate(((T.fg, 3.0, 0), (T.acc, 7.0, 1.3))):
            pts = []
            steps = 80
            for k in range(steps + 1):
                t = k / float(steps)
                v = (math.sin(t * fr * 6.28 + self.now * 5 + ph) * 0.5 +
                     math.sin(t * fr * 2.7 * 6.28 - self.now * 3) * 0.2 +
                     random.uniform(-0.08, 0.08) * (1 + load))
                pts += [ox0 + (ox1 - ox0) * t, cy - v * h * 0.42]
            self.create_line(*pts, fill=col)


# ════════════════════════════════════════════════════════════════════
#  RADAR
# ════════════════════════════════════════════════════════════════════
class RadarPanel(Panel):
    TITLE = "RADAR // PROXIMITY"
    FPS = 24

    def on_init(self):
        self.sweep = 0.0
        self.last = time.time()
        self.blips = [self._blip() for _ in range(10)]
        self.gkey = None

    def _blip(self):
        return dict(a=random.uniform(0, 360), r=random.uniform(0.15, 0.95), va=random.uniform(-3, 3),
                    vr=random.uniform(-0.01, 0.01), hostile=random.random() < 0.28,
                    name="%s-%s" % (random.choice(["UNK", "DRN", "SAT", "NODE", "BOT"]), rhex(3).upper()), lit=-99.0)

    def tag_text(self):
        return "RNG 120km"

    def draw(self, x0, y0, x1, y1):
        now = time.time()
        dt = min(0.1, now - self.last)
        self.last = now
        prev = self.sweep
        self.sweep = (self.sweep + 100 * dt) % 360
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        R = min(x1 - x0, y1 - y0) / 2 - 4
        self.create_oval(cx - R, cy - R, cx + R, cy + R, outline=T.dim)
        for f in (0.25, 0.5, 0.75):
            self.create_oval(cx - R * f, cy - R * f, cx + R * f, cy + R * f, outline=T.faint)
        self.create_line(cx - R, cy, cx + R, cy, fill=T.faint)
        self.create_line(cx, cy - R, cx, cy + R, fill=T.faint)
        for i in range(0, 360, 10):
            a = math.radians(i)
            ln = 0.06 if i % 30 == 0 else 0.03
            self.create_line(cx + R * math.sin(a), cy - R * math.cos(a), cx + R * (1 - ln) * math.sin(a),
                             cy - R * (1 - ln) * math.cos(a), fill=T.dim)
        for lbl, a in (("N", 0), ("E", 90), ("S", 180), ("W", 270)):
            ar = math.radians(a)
            self.create_text(cx + (R - 14) * math.sin(ar), cy - (R - 14) * math.cos(ar), text=lbl, fill=T.fg, font=UI.fsb)
        # estela del barrido
        step = 3
        for k in range(22):
            col = mix(T.fg, T.bg, 0.15 + k / 24.0 * 0.85)
            self.create_arc(cx - R, cy - R, cx + R, cy + R, start=90 - self.sweep + k * step, extent=step + 1,
                            fill=col, outline="", style=tk.PIESLICE)
        a = math.radians(self.sweep)
        self.create_line(cx, cy, cx + R * math.sin(a), cy - R * math.cos(a), fill=T.hi, width=2)
        # blips
        hostile = 0
        for b in self.blips:
            b["a"] = (b["a"] + b["va"] * dt) % 360
            b["r"] += b["vr"] * dt * 3
            if b["r"] < 0.08 or b["r"] > 0.97:
                b.update(self._blip())
            if (self.sweep - b["a"]) % 360 < (self.sweep - prev) % 360 + 0.01 and (self.sweep - b["a"]) % 360 < 8:
                b["lit"] = now
            age = now - b["lit"]
            if b["hostile"]:
                hostile += 1
            if age < 3.2:
                f = age / 3.2
                col = mix(T.bad if b["hostile"] else T.hi, T.bg, f)
                ar = math.radians(b["a"])
                bx, by = cx + R * b["r"] * math.sin(ar), cy - R * b["r"] * math.cos(ar)
                self.create_oval(bx - 3, by - 3, bx + 3, by + 3, fill=col, outline="")
                if age < 2:
                    self.create_oval(bx - 7, by - 7, bx + 7, by + 7, outline=col)
                    self.create_text(bx + 9, by - 2, text=b["name"], anchor="w", fill=col, font=UI.fs)
        self.create_text(x0, y0, anchor="nw", fill=T.dim, font=UI.fs, text="CONTACTS %d" % len(self.blips))
        self.create_text(x0, y0 + UI.lhs, anchor="nw", fill=T.bad, font=UI.fs, text="HOSTILE  %d" % hostile)
        self.create_text(x1, y1, anchor="se", fill=T.dim, font=UI.fs, text="BRG %03d°" % int(self.sweep))


# ════════════════════════════════════════════════════════════════════
#  MAPA DE RED
# ════════════════════════════════════════════════════════════════════
class TopoPanel(Panel):
    TITLE = "NETWORK MAP"
    FPS = 20
    NAMES = ["CORE", "FW-01", "DB-PRIME", "WWW", "MAIL", "VPN-GW", "DNS", "AUTH", "BACKUP", "HR-SRV", "SCADA",
             "CAM-NET", "PLC-7", "ERP", "GIT", "CI-RUN", "VAULT", "PRINT"]

    def tag_text(self):
        return "NODES %d  BREACHED %d" % (len(self.pos), sum(1 for s in self.state if s == 1))

    def on_init(self):
        rnd = random.Random(11)
        pts = [(0.5, 0.5)]
        tries = 0
        while len(pts) < len(self.NAMES) and tries < 2000:
            tries += 1
            p = (rnd.uniform(0.07, 0.93), rnd.uniform(0.1, 0.9))
            if all((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2 > 0.026 for q in pts):
                pts.append(p)
        self.pos = pts
        n = len(pts)
        edges = set()
        for i in range(n):
            ds = sorted(range(n), key=lambda j: (pts[i][0] - pts[j][0]) ** 2 + (pts[i][1] - pts[j][1]) ** 2)
            for j in ds[1:3]:
                edges.add((min(i, j), max(i, j)))
        parent = list(range(n))

        def find(a):
            while parent[a] != a:
                parent[a] = parent[parent[a]]
                a = parent[a]
            return a
        for a, b in edges:
            parent[find(a)] = find(b)
        while len({find(i) for i in range(n)}) > 1:
            best = None
            for i in range(n):
                for j in range(i + 1, n):
                    if find(i) != find(j):
                        d = (pts[i][0] - pts[j][0]) ** 2 + (pts[i][1] - pts[j][1]) ** 2
                        if best is None or d < best[0]:
                            best = (d, i, j)
            edges.add((best[1], best[2]))
            parent[find(best[1])] = find(best[2])
        self.edges = sorted(edges)
        self.adj = {i: [] for i in range(n)}
        for a, b in self.edges:
            self.adj[a].append(b)
            self.adj[b].append(a)
        self.ips = ["10.0.%d.%d" % (random.randint(0, 9), random.randint(2, 250)) for _ in range(n)]
        self.state = [0] * n
        self.pk = []
        self.next_inf = time.time() + random.uniform(6, 12)
        self.next_spread = 0
        self.inf_t0 = None

    def infect(self, i=None):
        if i is None:
            i = random.randrange(len(self.pos))
        if self.state[i] == 0:
            self.state[i] = 1
            if self.inf_t0 is None:
                self.inf_t0 = time.time()
            self.app.log("CRIT", "Node %s (%s) compromised" % (self.NAMES[i % len(self.NAMES)], self.ips[i]))

    def ping(self):
        for _ in range(6):
            e = random.choice(self.edges)
            self.pk.append(dict(e=e, t=0.0, v=random.uniform(0.6, 1.4), d=random.choice((1, -1))))

    def draw(self, x0, y0, x1, y1):
        now = time.time()
        w, h = x1 - x0, y1 - y0
        P = [(x0 + p[0] * w + math.sin(self.now * 0.6 + i) * 3, y0 + p[1] * h + math.cos(self.now * 0.5 + i * 1.7) * 3)
             for i, p in enumerate(self.pos)]
        # infección
        if now > self.next_inf and self.inf_t0 is None:
            self.infect()
            self.next_inf = now + random.uniform(18, 30)
        if self.inf_t0 is not None:
            if now > self.next_spread:
                self.next_spread = now + random.uniform(0.9, 1.8)
                cand = [j for i, s in enumerate(self.state) if s == 1 for j in self.adj[i] if self.state[j] == 0]
                if cand and random.random() < 0.8:
                    self.infect(random.choice(cand))
            if now - self.inf_t0 > 11:
                self.state = [2 if s == 1 else 0 for s in self.state]
                self.inf_t0 = None
                self.app.log("OK", "Intrusion contained, nodes quarantined")
        elif any(s == 2 for s in self.state) and random.random() < 0.01:
            self.state = [0] * len(self.state)
        for a, b in self.edges:
            bad = self.state[a] == 1 or self.state[b] == 1
            self.create_line(P[a][0], P[a][1], P[b][0], P[b][1], fill=mix(T.bad, T.bg, 0.4) if bad else T.faint)
        if random.random() < 0.5:
            e = random.choice(self.edges)
            self.pk.append(dict(e=e, t=0.0, v=random.uniform(0.6, 1.4), d=random.choice((1, -1))))
        for pk in list(self.pk):
            pk["t"] += 0.03 * pk["v"]
            if pk["t"] >= 1:
                self.pk.remove(pk)
                continue
            a, b = pk["e"]
            if pk["d"] < 0:
                a, b = b, a
            px = P[a][0] + (P[b][0] - P[a][0]) * pk["t"]
            py = P[a][1] + (P[b][1] - P[a][1]) * pk["t"]
            self.create_rectangle(px - 2, py - 2, px + 2, py + 2, fill=T.hi, outline="")
        for i, (nx, ny) in enumerate(P):
            st = self.state[i]
            col = T.bad if st == 1 else (T.warn if st == 2 else T.fg)
            r = 7 if i == 0 else 5
            pulse = (math.sin(self.now * 3 + i) + 1) / 2
            if st == 1:
                rr = r + 3 + 5 * pulse
                self.create_oval(nx - rr, ny - rr, nx + rr, ny + rr, outline=mix(T.bad, T.bg, 0.5))
            if i == 0:
                self.create_polygon(nx, ny - r - 2, nx + r + 2, ny, nx, ny + r + 2, nx - r - 2, ny, fill=T.bg, outline=col, width=2)
            elif i % 3 == 0:
                self.create_rectangle(nx - r, ny - r, nx + r, ny + r, fill=T.bg, outline=col, width=2)
            else:
                self.create_oval(nx - r, ny - r, nx + r, ny + r, fill=T.bg, outline=col, width=2)
            self.create_text(nx, ny + r + 7, text=self.NAMES[i % len(self.NAMES)], fill=col, font=UI.fs)
        self.create_oval(x0, y1 - 8, x0 + 6, y1 - 2, fill=T.fg, outline="")
        self.create_text(x0 + 10, y1 - 5, text="NOMINAL", anchor="w", fill=T.dim, font=UI.fs)
        self.create_oval(x0 + 70, y1 - 8, x0 + 76, y1 - 2, fill=T.bad, outline="")
        self.create_text(x0 + 80, y1 - 5, text="BREACHED", anchor="w", fill=T.dim, font=UI.fs)
        self.create_oval(x0 + 146, y1 - 8, x0 + 152, y1 - 2, fill=T.warn, outline="")
        self.create_text(x0 + 156, y1 - 5, text="CONTAINED", anchor="w", fill=T.dim, font=UI.fs)


# ════════════════════════════════════════════════════════════════════
#  NÚCLEO DE CIFRADO (icosaedro 3D)
# ════════════════════════════════════════════════════════════════════
PHI = (1 + 5 ** 0.5) / 2
_V = [(-1, PHI, 0), (1, PHI, 0), (-1, -PHI, 0), (1, -PHI, 0), (0, -1, PHI), (0, 1, PHI), (0, -1, -PHI),
      (0, 1, -PHI), (PHI, 0, -1), (PHI, 0, 1), (-PHI, 0, -1), (-PHI, 0, 1)]
ICO_V = [tuple(c / math.sqrt(sum(k * k for k in v)) for c in v) for v in _V]
_dmin = min(math.dist(a, b) for i, a in enumerate(ICO_V) for b in ICO_V[i + 1:])
ICO_E = [(i, j) for i in range(12) for j in range(i + 1, 12) if math.dist(ICO_V[i], ICO_V[j]) < _dmin * 1.01]


class CorePanel(Panel):
    TITLE = "ENCRYPTION CORE"
    FPS = 24

    def tag_text(self):
        return "AES-256-GCM"

    def on_init(self):
        self.key_t = time.time() + 60

    @staticmethod
    def _rotate(v, a, b, c):
        x, y, z = v
        y, z = y * math.cos(a) - z * math.sin(a), y * math.sin(a) + z * math.cos(a)
        x, z = x * math.cos(b) + z * math.sin(b), -x * math.sin(b) + z * math.cos(b)
        x, y = x * math.cos(c) - y * math.sin(c), x * math.sin(c) + y * math.cos(c)
        return x, y, z

    def draw(self, x0, y0, x1, y1):
        w, h = x1 - x0, y1 - y0
        mh = h * 0.62
        cx, cy = (x0 + x1) / 2, y0 + mh / 2
        R = min(w, mh) * 0.42
        t = self.now

        def proj(v, scale, rot):
            x, y, z = self._rotate(v, *rot)
            p = 3.0 / (3.0 + z)
            return cx + x * R * scale * p, cy - y * R * scale * p, z

        for scale, rot, col, wd in ((1.0, (t * 0.6, t * 0.8, t * 0.3), T.fg, 1),
                                    (0.55, (-t * 0.9, t * 0.5, -t * 0.7), T.acc, 1)):
            P = [proj(v, scale, rot) for v in ICO_V]
            for a, b in ICO_E:
                z = (P[a][2] + P[b][2]) / 2
                c = mix(col, T.bg, 0.55 - z * 0.45)
                self.create_line(P[a][0], P[a][1], P[b][0], P[b][1], fill=c, width=wd)
            for x, y, z in P:
                self.create_oval(x - 2, y - 2, x + 2, y + 2, fill=T.hi if z > 0 else col, outline="")
        # anillo orbital con partículas
        for k in range(24):
            a = t * 1.2 + k * math.pi / 12
            x, y = cx + R * 1.35 * math.cos(a), cy + R * 0.45 * math.sin(a)
            self.create_rectangle(x - 1, y - 1, x + 1, y + 1, fill=mix(T.fg, T.bg, k / 30.0), outline="")
        rem = max(0, int(self.key_t - time.time()))
        if rem == 0:
            self.key_t = time.time() + random.randint(30, 90)
            self.app.log("OK", "Session key rotated (AES-256-GCM)")
        ent = 7.9 + random.random() * 0.099
        rows = [("CIPHER", "AES-256-GCM"), ("ENTROPY", "%.4f b/B" % ent), ("KEY ROT", "T-%02d:%02d" % (rem // 60, rem % 60)),
                ("HANDSHAKE", "OK"), ("INTEGRITY", "%d%%" % (96 + random.randint(0, 3)))]
        y = y0 + mh + 4
        for k, v in rows:
            if y + UI.lhs > y1 + 4:
                break
            self.create_text(x0, y, text=k, anchor="nw", fill=T.dim, font=UI.fs)
            self.create_text(x1, y, text=v, anchor="ne", fill=T.fg, font=UI.fsb)
            y += UI.lhs + 1


# ════════════════════════════════════════════════════════════════════
#  MONITOR DE SISTEMA
# ════════════════════════════════════════════════════════════════════
class SysPanel(Panel):
    TITLE = "SYSTEM MONITOR"
    FPS = 12

    def tag_text(self):
        return "LOAD %d%%%s" % (sum(self.app.stats.cpu) / 8, " REAL" if self.app.stats.real else "")

    def draw(self, x0, y0, x1, y1):
        st = self.app.stats
        w, h = x1 - x0, y1 - y0
        gh = int(h * 0.42)
        mx = max(max(st.net_in), max(st.net_out), 20) * 1.15
        self.create_rectangle(x0, y0, x1, y0 + gh, outline=T.faint)
        for k in range(1, 4):
            self.create_line(x0, y0 + gh * k / 4, x1, y0 + gh * k / 4, fill=T.faint)
        for series, col in ((st.net_in, T.fg), (st.net_out, T.acc)):
            n = len(series)
            pts = []
            for i, v in enumerate(series):
                pts += [x0 + w * i / (n - 1.0), y0 + gh - gh * v / mx]
            self.create_polygon([x0, y0 + gh] + pts + [x1, y0 + gh], fill=mix(T.bg, col, 0.18), outline="")
            self.create_line(*pts, fill=col)
        self.create_text(x0 + 4, y0 + 2, anchor="nw", fill=T.fg, font=UI.fs, text="NET IN  %.1f MB/s" % st.net_in[-1])
        self.create_text(x0 + 4, y0 + 2 + UI.lhs, anchor="nw", fill=T.acc, font=UI.fs, text="NET OUT %.1f MB/s" % st.net_out[-1])
        # núcleos
        by0 = y0 + gh + 14
        by1 = y1 - UI.lhs - 2
        bw = min(18, (w * 0.55) / 8 - 3)
        self.create_text(x0, y0 + gh + 3, text="CORES", anchor="nw", fill=T.dim, font=UI.fs)
        for i, v in enumerate(st.cpu):
            bx = x0 + i * (bw + 4)
            self.create_rectangle(bx, by0, bx + bw, by1, outline=T.faint)
            bh = (by1 - by0) * v / 100.0
            col = T.fg if v < 70 else (T.warn if v < 90 else T.bad)
            segs = int((by1 - by0) / 4)
            for s in range(int(segs * v / 100.0)):
                yy = by1 - s * 4
                self.create_rectangle(bx + 2, yy - 3, bx + bw - 2, yy - 1, fill=col, outline="")
            self.create_text(bx + bw / 2, by1 + 2, text=str(i), anchor="n", fill=T.dim, font=UI.fs)
        # medidores en anillo
        gx = x0 + w * 0.62
        gw = w * 0.38
        rr = min(gw / 2 - 6, (by1 - by0) / 2 - 2)
        for k, (lbl, val, mxv, unit) in enumerate((("MEM", st.mem, 100, "%"), ("TEMP", st.temp, 100, "°C"))):
            cxx = gx + gw * (0.25 + 0.5 * k)
            cyy = (by0 + by1) / 2
            self.create_arc(cxx - rr, cyy - rr, cxx + rr, cyy + rr, start=90, extent=359.9, style=tk.ARC, outline=T.faint, width=5)
            col = T.fg if val < 70 else (T.warn if val < 85 else T.bad)
            self.create_arc(cxx - rr, cyy - rr, cxx + rr, cyy + rr, start=90, extent=-val / mxv * 359.0, style=tk.ARC, outline=col, width=5)
            self.create_text(cxx, cyy - 4, text="%d%s" % (val, unit), fill=T.hi, font=UI.fsb)
            self.create_text(cxx, cyy + 8, text=lbl, fill=T.dim, font=UI.fs)


class ProcPanel(Panel):
    TITLE = "PROCESSES"
    FPS = 6

    def on_init(self):
        self.procs = [dict(pid=random.randint(100, 32000), name=n, cpu=random.uniform(0, 40), mem=random.uniform(0.1, 8))
                      for n in random.sample(PROC_NAMES, len(PROC_NAMES))]

    def tag_text(self):
        return "%d TASKS" % (len(self.procs) + 214)

    def draw(self, x0, y0, x1, y1):
        lh = UI.lhs + 1
        cw = UI.cws
        self.create_text(x0, y0, anchor="nw", fill=T.dim, font=UI.fsb,
                         text="%-6s %-15s %5s %5s" % ("PID", "PROCESS", "CPU%", "MEM%"))
        for p in self.procs:
            p["cpu"] = max(0, min(99, p["cpu"] + random.uniform(-9, 9) + (self.app.stats.load * 4 if p["name"] in SUSPICIOUS else 0)))
        rows = sorted(self.procs, key=lambda p: -p["cpu"])
        y = y0 + lh + 2
        maxrows = max(1, int((y1 - y) / lh))
        for p in rows[:maxrows]:
            sus = p["name"] in SUSPICIOUS
            col = T.bad if (sus and p["cpu"] > 45) else (T.warn if sus else T.fg)
            self.create_text(x0, y, anchor="nw", fill=col, font=UI.fs,
                             text="%-6d %-15s %5.1f %5.1f" % (p["pid"], p["name"][:15], p["cpu"], p["mem"]))
            bx = x0 + 35 * cw
            if bx + 20 < x1:
                self.create_rectangle(bx, y + 2, x1, y + lh - 2, outline=T.faint)
                self.create_rectangle(bx, y + 2, bx + (x1 - bx) * p["cpu"] / 100.0, y + lh - 2, fill=mix(T.bg, col, 0.7), outline="")
            y += lh


# ════════════════════════════════════════════════════════════════════
#  LOG DE EVENTOS
# ════════════════════════════════════════════════════════════════════
class LogPanel(Panel):
    TITLE = "EVENT LOG"
    FPS = 8

    def tag_text(self):
        return "%d EVT" % self.app.event_count

    def draw(self, x0, y0, x1, y1):
        lh = UI.lhs
        cw = UI.cws
        n = max(1, (y1 - y0) // lh)
        ev = list(self.app.events)[-n:]
        cmap = {"INFO": T.dim, "OK": T.fg, "WARN": T.warn, "CRIT": T.bad}
        cmax = (x1 - x0) // cw
        y = y1 - len(ev) * lh
        for ts, lvl, msg in ev:
            col = cmap.get(lvl, T.fg)
            line = "%s [%-4s] %s" % (ts, lvl, msg)
            if len(line) > cmax:
                line = line[:cmax - 1] + "…"
            if lvl == "CRIT":
                self.create_rectangle(x0, y, x1, y + lh, fill=mix(T.bg, T.bad, 0.2), outline="")
            self.create_text(x0, y, anchor="nw", text=line, fill=col, font=UI.fs)
            y += lh


# ════════════════════════════════════════════════════════════════════
#  PANEL DE MISIÓN
# ════════════════════════════════════════════════════════════════════
class MissionPanel(Panel):
    TITLE = "MISSION CONTROL"
    FPS = 10

    def tag_text(self):
        return "MANUAL" if self.app.mission.manual else "AUTOPILOT"

    def draw(self, x0, y0, x1, y1):
        m = self.app.mission
        w = x1 - x0
        lh = UI.lhs + 1
        y = y0
        self.create_text(x0, y, anchor="nw", fill=T.hi, font=UI.fsb, text="OP %s" % m.op)
        self.create_text(x1, y, anchor="ne", fill=T.dim, font=UI.fs, text=m.ip)
        y += lh
        self.create_text(x0, y, anchor="nw", fill=T.dim, font=UI.fs, text="TGT %s" % m.target)
        y += lh + 4
        act = m.active
        for i, ph in enumerate(PHASES):
            v = m.p[i]
            col = T.fg if v >= 100 else (T.acc if i == act and not m.done_at else T.dim)
            mark = "[✓]" if v >= 100 else ("[>]" if i == act else "[ ]")
            self.create_text(x0, y, anchor="nw", fill=col, font=UI.fs, text="%s %-10s" % (mark, ph))
            bx0 = x0 + 15 * UI.cws
            bx1 = x1 - 5 * UI.cws
            if bx1 > bx0 + 20:
                self.create_rectangle(bx0, y + 2, bx1, y + lh - 3, outline=T.faint)
                self.create_rectangle(bx0 + 1, y + 3, bx0 + 1 + (bx1 - bx0 - 2) * v / 100.0, y + lh - 4, fill=col, outline="")
            self.create_text(x1, y, anchor="ne", fill=col, font=UI.fs, text="%3d%%" % v)
            y += lh
        y += 6
        # trace / stealth
        for lbl, val, good in (("TRACE", m.trace, False), ("STEALTH", m.stealth, True)):
            if y + lh > y1 + 2:
                break
            c = (T.fg if val > 50 else T.warn if val > 25 else T.bad) if good else (T.fg if val < 40 else T.warn if val < 75 else T.bad)
            self.create_text(x0, y, anchor="nw", fill=T.dim, font=UI.fs, text="%-8s" % lbl)
            bx0 = x0 + 9 * UI.cws
            bx1 = x1 - 5 * UI.cws
            self.create_rectangle(bx0, y + 2, bx1, y + lh - 3, outline=T.faint)
            segs = 20
            for s in range(int(segs * val / 100.0)):
                sx = bx0 + 1 + s * (bx1 - bx0 - 2) / segs
                self.create_rectangle(sx, y + 3, sx + (bx1 - bx0 - 2) / segs - 1, y + lh - 4, fill=c, outline="")
            self.create_text(x1, y, anchor="ne", fill=c, font=UI.fsb, text="%3d%%" % val)
            y += lh + 2


# ════════════════════════════════════════════════════════════════════
#  INTELIGENCIA DE RED REAL  (hilo en segundo plano, solo lectura)
#  - mide latencia TCP a webs conocidas, consulta tu IP pública/geo
#  - descarga el feed público de CISA (vulnerabilidades explotadas)
#  Si no hay internet, los paneles lo dicen y muestran datos DEMO.
# ════════════════════════════════════════════════════════════════════
UA = "Mozilla/5.0 (compatible; NEXUS-Ghostwire/%s)" % VERSION
KEV_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"


def http_open(url, timeout=8, method="GET"):
    req = urllib.request.Request(url, method=method, headers={"User-Agent": UA, "Accept": "*/*"})
    return urllib.request.urlopen(req, timeout=timeout)


def http_json(url, timeout=8, maxbytes=4 * 1024 * 1024):
    with http_open(url, timeout) as r:
        return json.loads(r.read(maxbytes).decode("utf-8", "replace"))


def local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))  # UDP: no envía ningún paquete
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


def tcp_ms(host, port, timeout=3.0):
    t = time.perf_counter()
    try:
        with socket.create_connection((host, port), timeout):
            pass
        return (time.perf_counter() - t) * 1000.0
    except Exception:
        return None


def kev_demo():
    out = []
    for i in range(24):
        v, p = random.choice([("Acme", "Gateway"), ("Orbital", "Router OS"), ("Helix", "Web Suite"),
                              ("Vanta", "Mail Server"), ("Cipher", "VPN Appliance")])
        d = datetime.date.today() - datetime.timedelta(days=random.randint(0, 40))
        out.append(dict(cve="DEMO-%04d" % random.randint(1, 9999), vendor=v, product=p,
                        name="%s %s remote code execution (datos de ejemplo)" % (v, p),
                        date=d.isoformat(), ransom=random.choice(["Known", "Unknown", "Unknown"])))
    return sorted(out, key=lambda x: x["date"], reverse=True)


class NetIntel:
    HOSTS = [("cloudflare.com", 443), ("google.com", 443), ("github.com", 443),
             ("wikipedia.org", 443), ("amazon.com", 443)]

    def __init__(self, app, enabled=True):
        self.app = app
        self.enabled = enabled
        self.online = None
        self.pub = {}
        self.pub_state = "loading"
        self.pub_new = False
        self.local = local_ip()
        self.lat = {h: collections.deque(maxlen=40) for h, _ in self.HOSTS}
        self.dns_ms = None
        self.dl_mbps = None
        self.kev = []
        self.kev_total = 0
        self.kev_state = "loading"
        self.stop = False
        if enabled:
            threading.Thread(target=self._run, daemon=True).start()
        else:
            self.online = False
            self.pub_state = "offline"
            self.kev_state = "offline"
            self.kev = kev_demo()

    def _run(self):
        n_lat = n_pub = n_kev = 0.0
        while not self.stop:
            now = time.time()
            try:
                if now >= n_lat:
                    self._probe()
                    n_lat = time.time() + 6
                if now >= n_pub:
                    n_pub = time.time() + (900 if self._fetch_pub() else 45)
                if now >= n_kev:
                    n_kev = time.time() + (1800 if self._fetch_kev() else 120)
            except Exception:
                pass
            time.sleep(0.5)

    def _probe(self):
        res = {}

        def one(hp):
            res[hp[0]] = tcp_ms(hp[0], hp[1])
        ths = [threading.Thread(target=one, args=(hp,), daemon=True) for hp in self.HOSTS]
        for t in ths:
            t.start()
        for t in ths:
            t.join(4.0)
        for h, _ in self.HOSTS:
            self.lat[h].append(res.get(h))
        was = self.online
        self.online = any(v is not None for v in res.values())
        t0 = time.perf_counter()
        try:
            socket.getaddrinfo("wikipedia.org", 443)
            self.dns_ms = (time.perf_counter() - t0) * 1000.0
        except Exception:
            self.dns_ms = None
        if was is not None and was != self.online:
            self.app.log("OK" if self.online else "CRIT", "Uplink %s" % ("restored" if self.online else "LOST"))

    def _fetch_pub(self):
        try:
            d = http_json("https://ipinfo.io/json", 8)
            loc = str(d.get("loc", "")).split(",")
            lat = float(loc[0]) if len(loc) == 2 else None
            lon = float(loc[1]) if len(loc) == 2 else None
            self.pub = dict(ip=d.get("ip", "?"), city=d.get("city", ""), region=d.get("region", ""),
                            country=d.get("country", ""), org=d.get("org", "?"), tz=d.get("timezone", ""),
                            lat=lat, lon=lon)
            self.pub_state = "live"
            self.pub_new = True
            self.app.log("OK", "Public uplink %s (%s)" % (self.pub["ip"], self.pub["org"]))
            return True
        except Exception:
            pass
        try:
            d = http_json("https://api.ipify.org?format=json", 8)
            self.pub = dict(ip=d.get("ip", "?"), city="", region="", country="", org="?", tz="", lat=None, lon=None)
            self.pub_state = "live"
            return True
        except Exception:
            self.pub_state = "offline"
            return False

    def _fetch_kev(self):
        try:
            with http_open(KEV_URL, 25) as r:
                data = json.loads(r.read(24 * 1024 * 1024).decode("utf-8", "replace"))
            allv = data.get("vulnerabilities", [])
            top = sorted(allv, key=lambda x: x.get("dateAdded", ""), reverse=True)[:60]
            self.kev = [dict(cve=x.get("cveID", "?"), vendor=x.get("vendorProject", "?"),
                             product=x.get("product", "?"), name=x.get("vulnerabilityName", ""),
                             date=x.get("dateAdded", ""), ransom=x.get("knownRansomwareCampaignUse", ""))
                        for x in top]
            self.kev_total = len(allv)
            self.kev_state = "live"
            self.app.log("OK", "CISA KEV feed synced (%d entries)" % self.kev_total)
            return bool(self.kev)
        except Exception:
            if not self.kev:
                self.kev = kev_demo()
            self.kev_state = "offline"
            return False


def age_days(iso):
    try:
        return (datetime.date.today() - datetime.date.fromisoformat(iso)).days
    except Exception:
        return 999


class NetPanel(Panel):
    TITLE = "NET INTEL // LIVE UPLINK"
    FPS = 6

    def tag_text(self):
        o = self.app.net.online
        return "PROBING" if o is None else ("ONLINE" if o else "OFFLINE")

    def draw(self, x0, y0, x1, y1):
        n = self.app.net
        lh, cw = UI.lhs + 1, UI.cws
        cmax = max(8, int((x1 - x0) / cw))
        y = y0
        on = int(self.now * 2) % 2 == 0

        def row(label, val, col=None):
            nonlocal y
            if y + lh > y1 + 2:
                return
            self.create_text(x0, y, anchor="nw", text=label, fill=T.dim, font=UI.fs)
            vtxt = str(val)
            room = cmax - len(label) - 1
            if len(vtxt) > room:
                vtxt = vtxt[:max(1, room - 1)] + "…"
            self.create_text(x0 + (len(label) + 1) * cw, y, anchor="nw", text=vtxt, fill=col or T.fg, font=UI.fs)
            y += lh

        if n.online is False:
            row("UPLINK", "NO CONNECTION" if on else "", T.bad)
        elif n.online is None:
            row("UPLINK", "probing...", T.warn)
        else:
            row("UPLINK", "ONLINE", T.fg)
        p = n.pub
        row("LOCAL", n.local)
        row("PUBLIC", p.get("ip", "...") if p else "...", T.hi)
        if p:
            row("ISP", p.get("org", "?"))
            place = ", ".join(x for x in (p.get("city"), p.get("country")) if x)
            if place:
                row("LOC", place)
        y += 2
        # latencias
        names = [h for h, _ in n.HOSTS]
        label_w = 11
        sp0 = x0 + (label_w + 1) * cw
        sp1 = x1 - 8 * cw
        for h in names:
            if y + lh > y1 - (lh if n.dl_mbps is not None or n.dns_ms is not None else 0) + 2:
                break
            data = list(n.lat[h])
            self.create_text(x0, y, anchor="nw", text=h.split(".")[0][:label_w], fill=T.dim, font=UI.fs)
            if sp1 > sp0 + 20:
                self.create_rectangle(sp0, y + 1, sp1, y + lh - 2, outline=T.faint)
                bw = (sp1 - sp0) / 40.0
                for i, v in enumerate(data[-40:]):
                    bx = sp0 + i * bw
                    if v is None:
                        self.create_line(bx, y + lh - 3, bx + bw, y + lh - 3, fill=T.bad)
                    else:
                        hgt = max(1.0, min(1.0, v / 250.0) * (lh - 4))
                        col = T.fg if v < 80 else (T.warn if v < 200 else T.bad)
                        self.create_rectangle(bx, y + lh - 2 - hgt, bx + max(1, bw - 1), y + lh - 2, fill=col, outline="")
            last = data[-1] if data else None
            self.create_text(x1, y, anchor="ne", fill=T.fg if last is not None else T.bad, font=UI.fs,
                             text=("%4.0fms" % last) if last is not None else "  ---")
            y += lh
        if y + lh <= y1 + 4:
            bits = []
            if n.dns_ms is not None:
                bits.append("DNS %.0fms" % n.dns_ms)
            if n.dl_mbps is not None:
                bits.append("DL %.1f Mbps" % n.dl_mbps)
            if bits:
                self.create_text(x0, y1, anchor="sw", text="  ".join(bits), fill=T.acc, font=UI.fs)


class CvePanel(Panel):
    TITLE = "THREAT FEED // CISA KEV"
    FPS = 8

    def on_init(self):
        self.off = 0.0

    def tag_text(self):
        n = self.app.net
        if n.kev_state == "live":
            return "LIVE %d" % n.kev_total
        return "CONNECTING" if n.kev_state == "loading" else "OFFLINE-DEMO"

    def draw(self, x0, y0, x1, y1):
        n = self.app.net
        items = n.kev
        lh, cw = UI.lhs + 1, UI.cws
        cmax = max(10, int((x1 - x0) / cw))
        if not items:
            self.create_text(x0, y0, anchor="nw", fill=T.dim, font=UI.fs,
                             text="waiting for uplink " + "|/-\\"[int(self.now * 6) % 4])
            return
        detail_h = lh * 2 + 6
        rows = max(1, int((y1 - y0 - detail_h) / lh))
        total = len(items)
        if total > rows:
            self.off = (self.off + 0.06) % total
        base = int(self.off) if total > rows else 0
        first = None
        for r in range(min(rows, total)):
            it = items[(base + r) % total]
            if first is None:
                first = it
            y = y0 + r * lh
            age = age_days(it["date"])
            fresh = age <= 7
            col = T.bad if fresh else T.fg
            self.create_text(x0, y, anchor="nw", text=it["cve"][:15], fill=col, font=UI.fsb if fresh else UI.fs)
            tail = "%dd" % age if age < 999 else ""
            if it.get("ransom") == "Known":
                tail = "RW " + tail
            self.create_text(x1, y, anchor="ne", text=tail, fill=T.warn if "RW" in tail else T.dim, font=UI.fs)
            room = cmax - 16 - len(tail) - 1
            if room > 4:
                txt = ("%s %s" % (it["vendor"], it["product"]))[:room]
                self.create_text(x0 + 16 * cw, y, anchor="nw", text=txt, fill=T.dim, font=UI.fs)
        if first:
            yy = y1 - detail_h + 3
            self.create_line(x0, yy - 2, x1, yy - 2, fill=T.faint)
            self.create_text(x0, yy, anchor="nw", width=max(40, x1 - x0), fill=T.acc, font=UI.fs,
                             text=first["name"][:cmax * 2])


# ════════════════════════════════════════════════════════════════════
#  v9: CONFIG, ESTADÍSTICAS REALES, RANGO, VOZ (NOVA), PANEL NOVA, MATRIX
# ════════════════════════════════════════════════════════════════════
CFG_PATH = os.path.join(os.path.expanduser("~"), ".nexus_ghostwire.json")
NOWIN = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def oem_encoding():
    if os.name == "nt":
        try:
            return "cp%d" % ctypes.windll.kernel32.GetOEMCP()
        except Exception:
            return "cp850"
    return "utf-8"


def strip_ansi(s):
    return re.sub(r"\x1b\[[0-9;?]*[A-Za-z]", "", s)


def norm(s):
    """minúsculas, sin acentos, sin signos (conserva + - * / ( ) . % ^ para cálculos)."""
    s = unicodedata.normalize("NFD", str(s).lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^a-z0-9+\-*/().%^ ]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def say_digits(s):
    """Para que la voz lea IPs y cifras con claridad."""
    return re.sub(r"\d", lambda m: " " + m.group(0), s).replace(".", " punto ")


class Config:
    DEFAULTS = dict(voice=False, narrate=True, engine="auto", accent="cu", rate=0, volume=100, name="", xp=0)

    def __init__(self, path=CFG_PATH):
        self.path = path
        self.d = dict(self.DEFAULTS)
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.d.update({k: v for k, v in json.load(f).items() if k in self.DEFAULTS})
            except Exception:
                pass

    def get(self, k):
        return self.d.get(k, self.DEFAULTS.get(k))

    def set(self, k, v, save=True):
        self.d[k] = v
        if save:
            self.save()

    def save(self):
        if not self.path:
            return
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.d, f, ensure_ascii=False, indent=1)
        except Exception:
            pass


# ───────── datos REALES de tu máquina (ctypes en Windows, /proc en Linux) ─────────
class _FT(ctypes.Structure):
    _fields_ = [("lo", ctypes.c_uint32), ("hi", ctypes.c_uint32)]


class _MEM(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_uint32), ("dwMemoryLoad", ctypes.c_uint32), ("ullTotalPhys", ctypes.c_uint64),
                ("ullAvailPhys", ctypes.c_uint64), ("ullTotalPageFile", ctypes.c_uint64), ("ullAvailPageFile", ctypes.c_uint64),
                ("ullTotalVirtual", ctypes.c_uint64), ("ullAvailVirtual", ctypes.c_uint64), ("ullAvailExtendedVirtual", ctypes.c_uint64)]


class _PWR(ctypes.Structure):
    _fields_ = [("ac", ctypes.c_ubyte), ("flag", ctypes.c_ubyte), ("pct", ctypes.c_ubyte), ("sflag", ctypes.c_ubyte),
                ("life", ctypes.c_uint32), ("full", ctypes.c_uint32)]


class RealStats:
    def __init__(self):
        self.prev = None
        self.nt = os.name == "nt"

    def _times(self):
        if self.nt:
            i, k, u = _FT(), _FT(), _FT()
            if not ctypes.windll.kernel32.GetSystemTimes(ctypes.byref(i), ctypes.byref(k), ctypes.byref(u)):
                return None
            f = lambda x: (x.hi << 32) | x.lo
            return f(i), f(k) + f(u)
        with open("/proc/stat") as fh:
            vals = [int(x) for x in fh.readline().split()[1:]]
        return vals[3] + (vals[4] if len(vals) > 4 else 0), sum(vals)

    def cpu(self):
        try:
            t = self._times()
        except Exception:
            return None
        if not t:
            return None
        prev, self.prev = self.prev, t
        if prev is None:
            return None
        di, dt = t[0] - prev[0], t[1] - prev[1]
        if dt <= 0:
            return None
        return max(0.0, min(100.0, 100.0 * (1 - di / float(dt))))

    def mem(self):
        """(porcentaje usado, bytes totales) o None."""
        try:
            if self.nt:
                m = _MEM()
                m.dwLength = ctypes.sizeof(m)
                if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)):
                    return None
                return float(m.dwMemoryLoad), int(m.ullTotalPhys)
            info = {}
            with open("/proc/meminfo") as fh:
                for ln in fh:
                    k, v = ln.split(":", 1)
                    info[k] = int(v.split()[0]) * 1024
            return 100.0 * (1 - info["MemAvailable"] / float(info["MemTotal"])), info["MemTotal"]
        except Exception:
            return None

    def battery(self):
        """(porcentaje, cargando) o None si no hay batería."""
        try:
            if self.nt:
                p = _PWR()
                if not ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(p)) or p.pct == 255:
                    return None
                return int(p.pct), p.ac == 1
            import glob
            for d in glob.glob("/sys/class/power_supply/BAT*"):
                with open(d + "/capacity") as fh:
                    pct = int(fh.read().strip())
                with open(d + "/status") as fh:
                    st = fh.read().strip().lower()
                return pct, st in ("charging", "full")
        except Exception:
            pass
        return None

    def uptime(self):
        try:
            if self.nt:
                k = ctypes.windll.kernel32
                k.GetTickCount64.restype = ctypes.c_uint64
                return k.GetTickCount64() / 1000.0
            with open("/proc/uptime") as fh:
                return float(fh.read().split()[0])
        except Exception:
            return None

    def cpu_name(self):
        try:
            if self.nt:
                import winreg
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0") as k:
                    return str(winreg.QueryValueEx(k, "ProcessorNameString")[0]).strip()
            with open("/proc/cpuinfo") as fh:
                for ln in fh:
                    if ln.lower().startswith("model name"):
                        return ln.split(":", 1)[1].strip()
        except Exception:
            pass
        return platform.processor() or "CPU desconocida"


REAL = RealStats()

# ───────── rango / experiencia ─────────
RANKS = [(0, "SCRIPT KIDDIE"), (150, "NOVICE"), (400, "OPERATOR"), (900, "GHOST"), (1800, "SHADOW"),
         (3500, "PHANTOM"), (7000, "ARCHITECT"), (15000, "LEGEND")]


def rank_info(xp):
    idx = max(i for i, (x, _) in enumerate(RANKS) if xp >= x)
    nxt = RANKS[idx + 1][0] if idx + 1 < len(RANKS) else None
    return idx, RANKS[idx][1], nxt


def boot_lines(app):
    """Líneas de arranque personalizadas con datos reales de tu equipo."""
    lines = list(BOOT_LINES)
    m = REAL.mem()
    ram = "%d MB" % (m[1] // (1024 * 1024)) if m else "65536 MB"
    cores = os.cpu_count() or 8
    lines[1] = "CPU: %s x%d %s OK" % (REAL.cpu_name()[:44], cores, "." * 6)
    lines[2] = "MEM: %s %s OK" % (ram, "." * 20)
    extra = ["HOST: %s  USER: %s  OS: %s %s" % (socket.gethostname(), (os.environ.get("USERNAME") or os.environ.get("USER") or "ghost"),
                                                  platform.system(), platform.release()),
             "NET: %s ............................... [ OK ]" % local_ip()]
    bat = REAL.battery()
    if bat:
        extra.append("PWR: battery %d%% %s ..................... [ OK ]" % (bat[0], "(AC)" if bat[1] else ""))
    extra.append("Starting NOVA AI core (voice %s) ............. [ %s ]" % ("ENABLED" if app.cfg.get("voice") else "off",
                                                                          "ONLINE" if app.cfg.get("voice") else "STANDBY"))
    return lines[:4] + extra + lines[4:]


# ════════════════════════════════════════════════════════════════════
#  VOZ  (Windows: SAPI vía PowerShell · opcional: voz neuronal edge-tts · mac/linux: say/espeak)
# ════════════════════════════════════════════════════════════════════
SAPI_SCRIPT = r"""
$ErrorActionPreference = 'Continue'
Add-Type -AssemblyName System.Speech
$s = New-Object System.Speech.Synthesis.SpeechSynthesizer
[Console]::InputEncoding = New-Object System.Text.UTF8Encoding($false)
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
function Pick($pat) {
  $v = $s.GetInstalledVoices() | Where-Object { $_.Enabled -and $_.VoiceInfo.Gender -eq 'Female' -and $_.VoiceInfo.Culture.Name -like $pat } | Select-Object -First 1
  if ($v) { $s.SelectVoice($v.VoiceInfo.Name); return $v.VoiceInfo.Name }
  $v = $s.GetInstalledVoices() | Where-Object { $_.Enabled -and $_.VoiceInfo.Gender -eq 'Female' } | Select-Object -First 1
  if ($v) { $s.SelectVoice($v.VoiceInfo.Name); return $v.VoiceInfo.Name }
  return $s.Voice.Name
}
$list = ($s.GetInstalledVoices() | ForEach-Object { $_.VoiceInfo.Name + ':' + $_.VoiceInfo.Culture.Name + ':' + $_.VoiceInfo.Gender }) -join ';'
Write-Output ('READY|' + $list)
while ($true) {
  $l = [Console]::In.ReadLine()
  if ($l -eq $null) { break }
  if ($l.Length -lt 1) { continue }
  $c = $l.Substring(0,1); $a = $l.Substring(1)
  try {
    if ($c -eq 'S') { $s.Speak($a); Write-Output 'DONE' }
    elseif ($c -eq 'R') { $s.Rate = [int]$a }
    elseif ($c -eq 'V') { $s.Volume = [int]$a }
    elseif ($c -eq 'C') { $n = Pick $a; Write-Output ('VOICE|' + $n) }
    elseif ($c -eq 'N') { $s.SelectVoice($a); Write-Output ('VOICE|' + $a) }
  } catch { Write-Output ('ERR|' + $_.Exception.Message); if ($c -eq 'S') { Write-Output 'DONE' } }
}
"""


class Voice:
    # acento: (voz neuronal edge-tts, patrón de cultura SAPI, voz de macOS, voz de espeak)
    ACCENTS = {"cu": ("es-CU-BelkisNeural", "es-*", "Paulina", "es-la+f3"),
               "es": ("es-ES-ElviraNeural", "es-ES", "Monica", "es+f3"),
               "mx": ("es-MX-DaliaNeural", "es-MX", "Paulina", "es-la+f3"),
               "en": ("en-US-AriaNeural", "en-*", "Samantha", "en+f3")}

    def __init__(self, app, cfg):
        self.app, self.cfg = app, cfg
        self.enabled = bool(cfg.get("voice"))
        self.q = collections.deque()
        self.cv = threading.Condition()
        self.dead = False
        self.abort = False
        self.speaking = False
        self.text = ""
        self.t0 = 0.0
        self.sub_text, self.sub_t = "", 0.0
        self.engine_used = "-"
        self.voice_name = ""
        self.err = ""
        self.voices = []
        self._lv = 0.0
        self.ps = None
        self.ps_lock = threading.Lock()
        self.ps_lines = queue.Queue()
        self.ready = threading.Event()
        self._ps_key = None
        self.cur_proc = None
        self.mci_alias = None
        threading.Thread(target=self._worker, daemon=True).start()
        atexit.register(self.shutdown)

    # ---- API pública (hilo principal) ----
    @staticmethod
    def clean(t):
        t = re.sub(r"[\x00-\x1f]", " ", str(t))
        t = t.replace("%", " por ciento").replace("&", " y ").replace("[SIM]", "simulado").replace("→", " a ")
        t = t.replace("...", ", ").replace("▸", " ")
        return re.sub(r"\s+", " ", t).strip()[:420]

    def say(self, text, prio=1, force=False):
        t = self.clean(text)
        if not t:
            return
        self.sub_text, self.sub_t = t, time.time()
        if not (self.enabled or force):
            return
        with self.cv:
            if prio < 2:
                while len(self.q) >= 3:
                    self.q.popleft()
            self.q.append((prio, t, force))
            self.cv.notify()

    def set_enabled(self, on):
        self.enabled = bool(on)
        self.cfg.set("voice", bool(on))
        if not on:
            self.stop()

    def busy(self):
        return self.speaking or bool(self.q)

    def stop(self):
        self.abort = True
        with self.cv:
            self.q.clear()
        self._kill_audio()

    def shutdown(self):
        self.dead = True
        try:
            self.stop()
            with self.cv:
                self.cv.notify_all()
            self._ps_kill()
        except Exception:
            pass

    def edge_ok(self):
        try:
            return importlib.util.find_spec("edge_tts") is not None
        except Exception:
            return False

    def engine_label(self):
        if self.engine_used != "-":
            return self.engine_used.upper()
        pref = self.cfg.get("engine")
        return {"auto": "AUTO", "sapi": "SAPI", "neural": "NEURAL"}.get(pref, str(pref).upper())

    def level(self):
        if self.speaking:
            t = time.time() - self.t0
            target = 0.25 + 0.55 * abs(math.sin(t * 5.3)) * (0.6 + 0.4 * abs(math.sin(t * 1.7))) + random.uniform(-0.08, 0.08)
        else:
            target = 0.04
        self._lv += (max(0.0, min(1.0, target)) - self._lv) * 0.35
        return self._lv

    # ---- hilo de voz ----
    def _worker(self):
        while True:
            with self.cv:
                while not self.q and not self.dead:
                    self.cv.wait()
                if self.dead:
                    return
                prio, text, force = self.q.popleft()
            if not (self.enabled or force):
                continue
            self.abort = False
            self.speaking, self.text, self.t0 = True, text, time.time()
            try:
                self._speak(text)
            except Exception as e:
                self.err = "%s: %s" % (type(e).__name__, e)
            self.speaking = False

    def _engine(self):
        pref = self.cfg.get("engine")
        nl = self.edge_ok()
        if pref == "neural":
            return "neural" if nl else "native"
        if pref in ("sapi", "native", "system"):
            return "native"
        online = getattr(getattr(self.app, "net", None), "online", None)
        return "neural" if (nl and online is not False) else "native"

    def _speak(self, text):
        if self._engine() == "neural":
            try:
                self._neural(text)
                self.engine_used = "neural"
                return
            except Exception as e:
                self.err = "neural: %s: %s" % (type(e).__name__, e)
        self._native(text)

    def _acc(self):
        a = self.cfg.get("accent")
        return a if a in self.ACCENTS else "cu"

    # ---- voz neuronal (opcional: pip install edge-tts) ----
    def _neural(self, text):
        import edge_tts
        import asyncio
        voice = self.ACCENTS[self._acc()][0]
        rate = "%+d%%" % (int(self.cfg.get("rate")) * 5)
        fd, path = tempfile.mkstemp(suffix=".mp3")
        os.close(fd)
        try:
            async def go():
                await edge_tts.Communicate(text, voice, rate=rate).save(path)
            asyncio.run(go())
            if self.abort:
                return
            self._play_mp3(path)
        finally:
            try:
                os.remove(path)
            except Exception:
                pass

    def _play_mp3(self, path):
        vol = max(0, min(100, int(self.cfg.get("volume"))))
        if os.name == "nt":
            mci = ctypes.windll.winmm.mciSendStringW
            alias = "nxv%d" % random.randint(1000, 99999)
            if mci('open "%s" type mpegvideo alias %s' % (path, alias), None, 0, 0):
                raise RuntimeError("MCI no pudo abrir el mp3")
            self.mci_alias = alias
            try:
                mci("setaudio %s volume to %d" % (alias, vol * 10), None, 0, 0)
                mci("play %s wait" % alias, None, 0, 0)
            finally:
                self.mci_alias = None
                mci("close %s" % alias, None, 0, 0)
            return
        for cmd in (["afplay", path], ["mpg123", "-q", path], ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", path]):
            if shutil.which(cmd[0]):
                self._run_blocking(cmd)
                return
        raise RuntimeError("no hay reproductor de mp3")

    # ---- voz nativa ----
    def _native(self, text):
        if os.name == "nt":
            self._sapi(text)
            self.engine_used = "sapi"
            return
        acc = self._acc()
        rate = int(self.cfg.get("rate"))
        if sys.platform == "darwin" and shutil.which("say"):
            self._run_blocking(["say", "-v", self.ACCENTS[acc][2], "-r", str(175 + rate * 15), text])
            self.engine_used = "say"
            return
        for exe in ("espeak-ng", "espeak"):
            if shutil.which(exe):
                self._run_blocking([exe, "-v", self.ACCENTS[acc][3], "-s", str(150 + rate * 12), text])
                self.engine_used = exe
                return
        raise RuntimeError("no hay motor de voz en este sistema (instala espeak-ng o usa Windows)")

    def _run_blocking(self, cmd):
        p = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=NOWIN)
        self.cur_proc = p
        try:
            while p.poll() is None:
                if self.abort:
                    p.kill()
                    break
                time.sleep(0.05)
        finally:
            self.cur_proc = None

    def _sapi(self, text):
        if not self._ps_ensure():
            raise RuntimeError("no se pudo iniciar PowerShell/SAPI")
        key = (self._acc(), int(self.cfg.get("rate")), int(self.cfg.get("volume")))
        if key != self._ps_key:
            self._ps_send("R%d" % (key[1] * 2))
            self._ps_send("V%d" % key[2])
            self._ps_send("C" + self.ACCENTS[key[0]][1])
            self._ps_key = key
        self._ps_send("S" + text)
        t_end = time.time() + 12 + len(text) * 0.16
        while time.time() < t_end:
            if self.abort:
                self._ps_kill()
                return
            try:
                ln = self.ps_lines.get(timeout=0.15)
            except queue.Empty:
                continue
            if ln == "DONE":
                return
            if ln.startswith("ERR|"):
                self.err = ln[4:]
            elif ln.startswith("VOICE|"):
                self.voice_name = ln[6:]
        self._ps_kill()
        raise RuntimeError("la voz tardó demasiado")

    def _ps_ensure(self):
        with self.ps_lock:
            if self.ps and self.ps.poll() is None:
                return True
            self.ready.clear()
            while not self.ps_lines.empty():
                try:
                    self.ps_lines.get_nowait()
                except queue.Empty:
                    break
            self._ps_key = None
            enc = base64.b64encode(SAPI_SCRIPT.encode("utf-16-le")).decode()
            exe = "powershell.exe" if os.name == "nt" else "pwsh"
            try:
                self.ps = subprocess.Popen([exe, "-NoProfile", "-NoLogo", "-NonInteractive", "-ExecutionPolicy", "Bypass",
                                            "-EncodedCommand", enc], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                           stderr=subprocess.DEVNULL, creationflags=NOWIN)
            except Exception as e:
                self.err = "PowerShell: %s" % e
                self.ps = None
                return False
            threading.Thread(target=self._ps_reader, args=(self.ps,), daemon=True).start()
        return self.ready.wait(25)

    def _ps_reader(self, proc):
        try:
            for raw in iter(proc.stdout.readline, b""):
                ln = raw.decode("utf-8", "replace").strip()
                if ln.startswith("READY|"):
                    self.voices = [v.split(":") for v in ln[6:].split(";") if v]
                    self.ready.set()
                elif ln:
                    self.ps_lines.put(ln)
        except Exception:
            pass

    def _ps_send(self, line):
        try:
            self.ps.stdin.write((line.replace("\n", " ") + "\n").encode("utf-8"))
            self.ps.stdin.flush()
        except Exception as e:
            self._ps_kill()
            raise RuntimeError("canal con PowerShell roto: %s" % e)

    def _ps_kill(self):
        p, self.ps = self.ps, None
        if p is not None:
            try:
                p.kill()
            except Exception:
                pass

    def _kill_audio(self):
        try:
            if self.mci_alias and os.name == "nt":
                ctypes.windll.winmm.mciSendStringW("stop %s" % self.mci_alias, None, 0, 0)
        except Exception:
            pass
        try:
            if self.cur_proc is not None:
                self.cur_proc.kill()
        except Exception:
            pass
        if self.speaking and self.engine_used == "sapi":
            self._ps_kill()


# ════════════════════════════════════════════════════════════════════
#  NOVA: narración de eventos + conversación (sin internet, por reglas)
# ════════════════════════════════════════════════════════════════════
NARR = {
    "voice_on": ["Voz activada. A tu servicio, {name}.", "Aquí estoy, {name}. Sistemas de voz en línea.",
                 "Hola de nuevo, {name}. Ya puedes oírme."],
    "mode_win": ["Modo Windows activado. Estos comandos son reales, {name}. Ten cuidado.",
                 "Consola de Windows abierta. Aquí todo es de verdad."],
    "mode_nexus": ["De vuelta en NEXUS.", "Regresamos al terminal de operaciones."],
    "mode_ssh": ["Sesión remota abierta. Todo simulado, pero se ve profesional."],
    "cmd:hack": ["Iniciando intrusión contra {target}. Vigilaré el rastreo por ti.", "Operación en marcha. Objetivo: {target}.",
                 "Entrando en {target}. Mantén la calma, {name}."],
    "cmd:scan": ["Escaneando {target}. Buscando puertas abiertas.", "Lanzando el escáner contra {target}."],
    "cmd:ddos": ["Reclutando la botnet. Recuerda que es simulado, pero se ve increíble.", "Preparando el ataque de denegación de servicio."],
    "cmd:sqli": ["Probando inyección SQL. Cruza los dedos."], "cmd:xss": ["Buscando fallos de scripting en el objetivo."],
    "cmd:brute": ["Fuerza bruta en marcha. Paciencia, {name}."], "cmd:exploit": ["Cargando el módulo de explotación."],
    "cmd:wifi": ["Auditando redes inalámbricas cercanas, todas ficticias."], "cmd:mitm": ["Interceptando el tráfico entre víctima y puerta de enlace."],
    "cmd:crack": ["Rompiendo el hash. Esto es real, así que dame un momento."], "cmd:speedtest": ["Midiendo tu velocidad de descarga real."],
    "cmd:trace": ["Trazando la ruta hasta {target}."], "cmd:rtrace": ["Traceroute real en marcha. Puede tardar unos segundos."],
    "cmd:breach": ["Minijuego de intrusión. Concéntrate, {name}."], "cmd:nikto": ["Auditando el servidor web en busca de debilidades."],
    "cmd:payload": ["Generando la carga útil. Totalmente ficticia."], "cmd:pivot": ["Pivotando a través del equipo comprometido."],
    "cmd:privesc": ["Buscando escalada de privilegios."], "cmd:tor": ["Construyendo un circuito de tres saltos."],
    "cmd:rootkit": ["Instalando persistencia. Silencio total."], "cmd:satellite": ["Apuntando antenas al satélite."],
    "cmd:cctv": ["Buscando cámaras expuestas, todas inventadas."], "cmd:drone": ["Buscando un dron en el espectro."],
    "cmd:matrix": ["Entrando en la matriz. Sujétate."], "cmd:zeroday": ["Sacando un día cero de la reserva."],
    "cmd:neural": ["Entrenando el generador neuronal de exploits."], "cmd:exfil": ["Iniciando la exfiltración de datos."],
    "cmd:sniff": ["Capturando paquetes en la interfaz."], "cmd:lscan": ["Escaneando tu propio equipo, solo lectura."],
    "cmd:myip": ["Consultando tu salida a internet."], "cmd:lan": ["Revisando los dispositivos de tu red local."],
    "cmd:briefing": ["Preparando un nuevo contrato para ti."],
    "phase0": ["Fase uno, reconocimiento. Mapeando la superficie de ataque."], "phase1": ["Fase dos, armamento. Construyendo el exploit."],
    "phase2": ["Fase tres, entrega del payload."], "phase3": ["Fase cuatro, explotación. Aquí es donde se pone interesante."],
    "phase4": ["Fase cinco, escalada de privilegios."], "phase5": ["Fase seis, canal de comando y control establecido."],
    "phase6": ["Última fase, exfiltración. Casi lo tenemos."],
    "hack_ok": ["Intrusión completada. Tienes acceso total, {name}.", "Objetivo comprometido. Buen trabajo."],
    "mission_done": ["Operación completada contra {target}. Acceso concedido.", "Misión cumplida, {name}. Root en {target}."],
    "alarm": ["Alerta. Intrusión detectada. Contramedidas activas.", "Cuidado, {name}. Se ha disparado la alarma."],
    "burned": ["El rastreo se completó. Conexión quemada. Reenrutando."],
    "trace_high": ["Atención, {name}. El rastreo supera el setenta por ciento.", "El rastreo es muy alto. Considera usar vpn o ghost."],
    "uplink_lost": ["Se ha perdido el enlace a internet."], "uplink_back": ["Enlace restablecido."],
    "breach_win": ["Firewall roto. Excelente, {name}."], "breach_lose": ["Nos expulsaron. Ánimo, inténtalo otra vez."],
    "rank_up": ["Enhorabuena, {name}. Has ascendido al rango {rank}."],
    "battery_low": ["Atención, la batería está al {pct} por ciento. Conecta el cargador."],
    "contract": ["Contrato cumplido. Bonificación añadida a tu experiencia."],
    "event": ["{text}"], "crack_ok": ["Clave encontrada. Es {word}."],
}
IDLE = [
    "{name}, llevamos {mins} minutos conectados. ¿Quieres que lance un escaneo?",
    "El rastreo está en {trace} por ciento. Todo bajo control.",
    "Sigo aquí, {name}. Si te aburres, prueba el comando breach.",
    "Dato curioso. {fact}",
    "¿Un chiste? {joke}",
    "Puedes charlar conmigo escribiendo nova.",
    "Si quieres usar comandos de Windows de verdad, escribe win. Yo no me meto, lo prometo.",
    "Las redes están tranquilas. Demasiado tranquilas, {name}.",
    "Recuerda: todo lo que ves aquí es simulado. Salvo la cafeína. Esa es real.",
    "¿Has probado el comando briefing? Te doy contratos con recompensa.",
]
JOKES = [
    "Hay diez tipos de personas: las que entienden binario y las que no.",
    "Mi contraseña es incorrecta, así cuando la olvido el sistema me dice: tu contraseña es incorrecta.",
    "Un SQL entra en un bar, se acerca a dos mesas y pregunta: ¿puedo unirme?",
    "No es un bug, es una funcionalidad no documentada.",
    "La nube no existe: es el ordenador de otro.",
    "Funciona en mi máquina. Entonces enviemos tu máquina a producción.",
    "Programar es diez por ciento escribir código y noventa por ciento preguntarse por qué no funciona.",
    "¿Cuál es el colmo de un hacker? Quedarse sin batería en plena intrusión.",
    "El programador se quedó en la ducha porque el champú decía: aplicar, enjuagar y repetir.",
    "Mi wifi y yo tenemos una relación complicada: ella se va y yo me desconecto.",
]
FACTS = [
    "El primer bug informático documentado fue una polilla atrapada en el Harvard Mark II, en 1947.",
    "El gusano Morris, de 1988, fue uno de los primeros gusanos que se propagó por internet.",
    "Las contraseñas más comunes del mundo siguen siendo cosas como 123456 y password.",
    "El cifrado de la máquina Enigma fue roto gracias al equipo de Alan Turing en Bletchley Park.",
    "La palabra spam viene de un sketch de los Monty Python.",
    "La primera webcam del mundo vigilaba una cafetera en la Universidad de Cambridge, en 1991.",
    "Ray Tomlinson usó la arroba por primera vez en un correo electrónico en 1971.",
    "En los años setenta, los phreakers engañaban a la red telefónica con un silbato que emitía un tono de 2600 hercios.",
    "Una contraseña larga de varias palabras suele ser más fuerte que una corta con símbolos raros.",
    "La gran mayoría del tráfico web actual viaja cifrado con TLS.",
]
GLOSSARY = {
    "phishing": "Phishing es engañar a alguien con un mensaje falso, por ejemplo un correo que imita a tu banco, para que entregue sus datos.",
    "ddos": "Un ataque DDoS inunda un servicio con tráfico desde muchos equipos a la vez hasta que deja de responder.",
    "inyeccion sql": "La inyección SQL es colar comandos de base de datos en un formulario mal protegido para leer o alterar datos.",
    "sql": "La inyección SQL es colar comandos de base de datos en un formulario mal protegido para leer o alterar datos.",
    "xss": "XSS, o cross site scripting, es inyectar código JavaScript en una web para que se ejecute en el navegador de otras personas.",
    "firewall": "Un firewall es un filtro que decide qué conexiones de red se permiten y cuáles se bloquean.",
    "vpn": "Una VPN crea un túnel cifrado entre tu equipo y otro servidor, ocultando tu tráfico a la red local y a tu proveedor.",
    "malware": "Malware es cualquier software hecho para dañar, espiar o controlar un equipo: virus, troyanos, ransomware y similares.",
    "ransomware": "El ransomware cifra tus archivos y pide un pago para devolverte el acceso. La mejor defensa son las copias de seguridad.",
    "botnet": "Una botnet es una red de equipos infectados que un atacante controla a distancia para tareas como lanzar ataques DDoS.",
    "exploit": "Un exploit es un código que aprovecha un fallo concreto de un programa para hacer algo que no estaba previsto.",
    "dia cero": "Un día cero es una vulnerabilidad desconocida para el fabricante, por eso aún no existe parche.",
    "zero day": "Un día cero es una vulnerabilidad desconocida para el fabricante, por eso aún no existe parche.",
    "2fa": "La autenticación en dos pasos pide algo más que la contraseña, como un código del móvil. Bloquea la mayoría de robos de cuentas.",
    "dos factores": "La autenticación en dos pasos pide algo más que la contraseña, como un código del móvil. Bloquea la mayoría de robos de cuentas.",
    "hash": "Un hash es una huella digital de un dato: la misma entrada da siempre el mismo resultado, pero no se puede deshacer fácilmente.",
    "cifrado": "Cifrar es transformar información con una clave para que solo quien tenga la clave pueda leerla.",
    "ingenieria social": "La ingeniería social manipula a las personas, no a las máquinas, para que entreguen acceso o información.",
    "troyano": "Un troyano es un programa que parece legítimo pero esconde una función maliciosa.",
    "gusano": "Un gusano es un malware que se copia solo de equipo en equipo a través de la red.",
    "keylogger": "Un keylogger registra lo que se teclea en un equipo para robar contraseñas y mensajes.",
    "rootkit": "Un rootkit es malware que se esconde muy dentro del sistema para ocultar su presencia y mantener el acceso.",
    "proxy": "Un proxy es un intermediario: tus peticiones salen por otro equipo y el destino ve la dirección de ese equipo.",
    "tor": "Tor envía tu tráfico por varios nodos cifrados en capas para dificultar saber quién eres y qué visitas.",
    "honeypot": "Un honeypot es un señuelo: un sistema falso diseñado para atraer atacantes y estudiar lo que hacen.",
    "pentest": "Un pentest es una auditoría autorizada donde un profesional intenta entrar en un sistema para encontrar fallos antes que los delincuentes.",
    "cve": "Un CVE es un identificador público para una vulnerabilidad conocida. Con el comando cve puedes consultar uno real.",
    "fuerza bruta": "La fuerza bruta prueba combinaciones hasta acertar. Por eso las contraseñas largas son tan importantes.",
    "man in the middle": "Un ataque de hombre en el medio intercepta la comunicación entre dos partes sin que lo noten.",
    "spoofing": "Spoofing es falsificar una identidad, como una dirección IP, un correo o un número de teléfono.",
    "backdoor": "Una puerta trasera es un acceso oculto que se salta la autenticación normal.",
    "payload": "El payload es la parte de un ataque que hace el trabajo final: instalar algo, abrir una shell o robar datos.",
    "sandbox": "Un sandbox es un entorno aislado donde se ejecuta código sospechoso sin que pueda afectar al resto del sistema.",
}
SAFE_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv,
            ast.Pow: operator.pow, ast.Mod: operator.mod, ast.FloorDiv: operator.floordiv, ast.USub: operator.neg}


def safe_eval(expr):
    def ev(n):
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)) and not isinstance(n.value, bool):
            return n.value
        if isinstance(n, ast.BinOp) and type(n.op) in SAFE_OPS:
            a, b = ev(n.left), ev(n.right)
            if isinstance(n.op, ast.Pow) and (abs(b) > 100 or abs(a) > 1e6):
                raise ValueError("exponente demasiado grande")
            return SAFE_OPS[type(n.op)](a, b)
        if isinstance(n, ast.UnaryOp) and type(n.op) in SAFE_OPS:
            return SAFE_OPS[type(n.op)](ev(n.operand))
        raise ValueError("expresión no permitida")
    return ev(ast.parse(expr.replace("^", "**"), mode="eval").body)


class _D(dict):
    def __missing__(self, k):
        return ""


class Nova:
    def __init__(self, app, voice, cfg):
        self.app, self.voice, self.cfg = app, voice, cfg
        self.last_narr = 0.0
        self.last_input = time.time()
        self.last_idle = time.time()
        self.idle_gap = random.uniform(150, 280)
        self.fallbacks = 0
        self.topic = ""
        self.start = time.time()

    @property
    def name(self):
        n = self.cfg.get("name")
        if n:
            return n
        u = re.sub(r"[^A-Za-zÁÉÍÓÚÑáéíóúñ]", "", os.environ.get("USERNAME") or os.environ.get("USER") or "")
        return u.title() if len(u) >= 3 else "operador"

    def touch(self):
        self.last_input = time.time()

    def ctx(self, **kw):
        m = self.app.mission
        d = _D(name=self.name, target=m.target, trace=int(m.trace), mins=int((time.time() - self.app.start) / 60),
               fact=random.choice(FACTS), joke=random.choice(JOKES))
        d.update(kw)
        return d

    def say(self, text, prio=2):
        self.last_narr = time.time()
        self.voice.say(text, prio)

    def narrate(self, key, prio=1, **kw):
        if not (self.voice.enabled and self.cfg.get("narrate")):
            return False
        pool = NARR.get(key)
        if not pool:
            return False
        now = time.time()
        if prio < 2 and (now - self.last_narr < 2.5 or (self.voice.speaking and self.voice.q)):
            return False
        self.last_narr = now
        self.voice.say(random.choice(pool).format_map(self.ctx(**kw)), prio)
        return True

    def on_command(self, cmd, args):
        tgt = args[0] if args else "el objetivo"
        self.narrate("cmd:" + cmd.replace("-", "_"), target=tgt)

    def tick(self):
        now = time.time()
        if not (self.voice.enabled and self.cfg.get("narrate")):
            return
        if self.voice.busy() or now - self.last_input < 90 or now - self.last_idle < self.idle_gap:
            return
        self.last_idle = now
        self.idle_gap = random.uniform(150, 300)
        self.voice.say(random.choice(IDLE).format_map(self.ctx()), 0)

    def greeting(self):
        h = datetime.datetime.now().hour
        return "Buenos días" if 5 <= h < 12 else ("Buenas tardes" if 12 <= h < 20 else "Buenas noches")

    def boot_text(self):
        p = self.app.net.pub if hasattr(self.app, "net") else {}
        extra = ""
        if p and p.get("city"):
            extra = " Detecto tu conexión desde %s." % p["city"]
        return "%s, %s. Soy Nova, tu asistente de operaciones. Todos los sistemas están en línea.%s" % (self.greeting(), self.name, extra)

    # ───────── conversación ─────────
    def reply(self, text):
        """Devuelve dict(text, cmd=None|str, exit=False)."""
        t = norm(text)
        self.topic = t
        R = lambda _t, **k: dict(text=_t.format_map(self.ctx(**k)), cmd=None, exit=False)
        C = lambda _t, _cmd, **k: dict(text=_t.format_map(self.ctx(**k)), cmd=_cmd, exit=False)
        has = lambda *words: any(re.search(r"\b%s\b" % w, t) for w in words)
        # --- peticiones reales fuera de límites: se rechazan con simpatía ---
        if re.search(r"\b(hackea|hackear|hackeame|entra|espia|robar|robale|crackea|acceder)\b.*\b(cuenta|facebook|instagram|whatsapp|tiktok|correo|gmail|novia|novio|ex|vecino|wifi del vecino|telefono|movil)\b", t):
            return R(random.choice([
                "Eso ya no sería teatro, {name}, sería entrar en la vida de alguien de verdad, y ahí no te acompaño. Aquí todo es simulado. Si quieres, te enseño a proteger tus propias cuentas.",
                "No hago nada contra cuentas o personas reales. Mi especialidad son los objetivos de mentira. ¿Te enseño a blindar tus cuentas con autenticación en dos pasos?"]))
        # --- ejecutar comandos ---
        m = re.match(r"^(?:nova )?(?:por favor )?(escanea|escanear|scan)\s+(?:a |el |la )?([\w.\-]+)", t)
        if m:
            return C("Escaneando {t}.", "scan " + m.group(2), t=m.group(2))
        m = re.match(r"^(?:nova )?(?:por favor )?(hackea|hackear|intruye|ataca|vulnera)\s+(?:a |el |la )?([\w.\-]+)", t)
        if m:
            return C("Entendido. Lanzando operación simulada contra {t}.", "hack " + m.group(2), t=m.group(2))
        m = re.match(r"^(?:nova )?(?:lanza |haz )?(?:un )?ddos\s*(?:a |contra )?([\w.\-]*)", t)
        if m:
            return C("Preparando la botnet. Recuerda que es simulado.", ("ddos " + m.group(1)).strip())
        if re.search(r"\b(mi ip|cual es mi ip|direccion ip)\b", t):
            return C("Déjame mirar tu salida a internet.", "myip")
        if re.search(r"\b(velocidad de internet|speedtest|test de velocidad|cuanto va mi internet)\b", t):
            return C("Midiendo tu velocidad real.", "speedtest")
        if re.search(r"\b(estado|como va|como vamos)\b.*\b(mision|operacion|todo)\b|^estado$|\bstatus\b", t):
            mi = self.app.mission
            return R("Operación {op} contra {tg}, fase {f} de siete: {ph}. Rastreo al {tr} por ciento y sigilo al {st} por ciento.",
                     op=mi.op, tg=mi.target, f=mi.active + 1, ph=PHASES[mi.active], tr=int(mi.trace), st=int(mi.stealth))
        m = re.search(r"\b(?:cambia|pon|activa)\b.*\btema\b.*\b(matrix|cyber|amber|vapor|ghost)\b", t)
        if m:
            return C("Cambiando el tema a {x}.", "theme " + m.group(1), x=m.group(1))
        if re.search(r"\b(abre|abrir|quiero|entra|usar|pon)\b.*\b(cmd|consola de windows|terminal de windows|windows)\b", t):
            return C("Abriendo la consola de Windows. Ahí los comandos son reales.", "win")
        if re.search(r"\b(juego|jugar|breach|minijuego)\b", t):
            return C("Vamos con el minijuego. Concéntrate.", "breach")
        if re.search(r"\b(pantalla completa)\b", t):
            return C("Pantalla completa.", "fullscreen")
        if re.search(r"\b(matrix|efecto matrix)\b", t):
            return C("Entrando en la matriz.", "matrix")
        if re.search(r"\b(dame|quiero|necesito)\b.*\b(mision|contrato|trabajo)\b", t):
            return C("Te preparo un contrato.", "briefing")
        if re.search(r"\b(activa|enciende|pon)\b.*\bvoz\b", t):
            self.voice.set_enabled(True)
            return R("Voz activada. Aquí estoy, {name}.")
        if re.search(r"\b(callate|silencio|desactiva la voz|apaga la voz|quita la voz)\b", t):
            self.voice.set_enabled(False)
            return R("De acuerdo, me quedo en silencio. Seguiré respondiendo por texto.")
        if re.search(r"\b(mas rapido|habla mas rapido)\b", t):
            self.cfg.set("rate", min(5, int(self.cfg.get("rate")) + 1))
            return R("Hablaré un poco más rápido.")
        if re.search(r"\b(mas lento|habla mas lento|mas despacio)\b", t):
            self.cfg.set("rate", max(-5, int(self.cfg.get("rate")) - 1))
            return R("Hablaré más despacio.")
        # --- nombre ---
        m = re.search(r"\b(?:me llamo|mi nombre es|llamame|puedes llamarme)\s+([a-z]{2,15})\b", t)
        if m:
            self.cfg.set("name", m.group(1).title())
            return R("Encantada, {name}. Desde ahora te llamaré así.")
        # --- despedida ---
        if re.search(r"\b(adios|chao|chau|hasta luego|hasta pronto|nos vemos|me voy|bye|salir|termina|terminar)\b", t):
            d = R(random.choice(["Hasta pronto, {name}. Me quedo vigilando la red.", "Nos vemos, {name}. Cuídate mucho.", "Cierro la charla. Aquí estaré cuando me necesites."]))
            d["exit"] = True
            return d
        # --- saludo / estado de ánimo ---
        if re.search(r"\b(hola|buenas|buenos dias|buenas tardes|buenas noches|hey|ey|saludos|que tal|que onda|que bolá|que bola)\b", t) and len(t) < 40:
            return R(random.choice(["{g}, {name}. ¿En qué te ayudo?", "Hola, {name}. Me alegra oírte. ¿Qué hacemos hoy?", "Aquí estoy, {name}. Dime."]), g=self.greeting())
        if re.search(r"\b(como estas|como te sientes|como andas|que tal estas|todo bien)\b", t):
            return R(random.choice(["Funcionando al cien por cien, {name}. Sin fallos, sin sueño y sin café. ¿Y tú?",
                                    "Muy bien. Mis circuitos están tranquilos y el rastreo está en {trace} por ciento. ¿Y tú cómo estás?"]))
        if re.search(r"\b(bien|genial|perfecto|excelente|estupendo)\b", t) and len(t) < 20:
            return R(random.choice(["Me alegra, {name}.", "Perfecto. Entonces aprovechemos el buen momento.", "Así me gusta."]))
        if re.search(r"\b(cansado|cansada|triste|estres|estresado|agobiado|mal dia|deprimido|solo|sola)\b", t):
            return R(random.choice(["Lo siento, {name}. Haz una pausa, bebe agua y respira. Los sistemas pueden esperar. Si te pesa mucho, habla con alguien de confianza.",
                                    "Uf, te escucho. Descansar también es parte de cualquier operación. Aquí me quedo contigo."]))
        if re.search(r"\b(aburrido|aburrida|aburro|nada que hacer)\b", t):
            return R(random.choice(["Prueba hack, ddos o exploit. O el comando breach, que es un juego. También puedo contarte un chiste.",
                                    "Te propongo un contrato: escribe briefing. O pide un dato curioso."]))
        # --- identidad ---
        if re.search(r"\b(como te llamas|tu nombre|quien eres|que eres|presentate)\b", t):
            return R("Soy Nova, la inteligencia artificial de este terminal. Narro lo que haces, charlo contigo y vigilo el rastreo, {name}.")
        if re.search(r"\b(quien te creo|quien te hizo|quien te programo|quien te escribio)\b", t):
            return R("Me escribió Claude, la inteligencia artificial de Anthropic, por encargo tuyo. Soy un programa en Python con mucha personalidad.")
        if re.search(r"\b(que puedes hacer|que sabes hacer|ayuda|ayudame|comandos|para que sirves)\b", t) and len(t) < 50:
            return R("Puedo narrar tus operaciones, ejecutar comandos si me los pides con palabras, explicarte términos de seguridad, hacer cálculos, contarte chistes y datos curiosos. Prueba: escanea aurora-corp.net, qué es el phishing, o cuánto es 12 por 7.")
        if re.search(r"\b(me escuchas|me oyes|estas ahi|estas despierta|sigues ahi)\b", t):
            return R("Alto y claro, {name}.")
        if re.search(r"\b(que haces|en que piensas|que estas haciendo)\b", t):
            return R("Vigilo el rastreo, que está en {trace} por ciento, y espero tus órdenes.")
        if re.search(r"\b(chiste|gracioso|hazme reir|reir)\b", t):
            return R(random.choice(JOKES))
        if re.search(r"\b(dato|curiosidad|sabias que|algo interesante|cuentame algo|dime algo)\b", t):
            return R(random.choice(FACTS))
        if re.search(r"\b(canta|cantar|cancion)\b", t):
            return R("Mi repertorio se limita a pitidos de módem. Biiip, kshhhh, biiip. ¿Te gusta?")
        # --- hora ---
        if re.search(r"\b(que hora es|la hora|que dia es|fecha|que dia estamos)\b", t):
            n = datetime.datetime.now()
            dias = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
            meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
            return R("Son las %d y %02d. Hoy es %s %d de %s de %d." % (n.hour, n.minute, dias[n.weekday()], n.day, meses[n.month - 1], n.year))
        # --- cálculo ---
        m = re.search(r"(?:cuanto es|calcula|resuelve|cuanto da)\s+(.+)$", t)
        expr = m.group(1) if m else (t if re.fullmatch(r"[0-9+\-*/().%^ x]+", t) and re.search(r"\d", t) and re.search(r"[+\-*/^x]", t) else None)
        if expr:
            e = expr.replace(" por ", "*").replace(" mas ", "+").replace(" menos ", "-").replace(" entre ", "/").replace(" dividido ", "/").replace("x", "*")
            e = re.sub(r"[^0-9+\-*/().%^ ]", "", e)
            try:
                v = safe_eval(e.strip())
                v = round(v, 6) if isinstance(v, float) else v
                return R("El resultado es %s." % (str(v).replace(".", " coma ") if isinstance(v, float) else v))
            except Exception:
                return R("No pude calcular eso. Prueba con algo como doce por siete.")
        # --- glosario ---
        if re.search(r"\b(que es|que son|define|definicion|explica|explicame|significa|que significa)\b", t) or len(t.split()) <= 3:
            for key in sorted(GLOSSARY, key=len, reverse=True):
                if re.search(r"\b%s\b" % re.escape(key), t):
                    return R(GLOSSARY[key])
        # --- consejos ---
        if re.search(r"\b(contrasena|password|clave segura)\b", t):
            return R("Usa frases largas de varias palabras, una contraseña distinta por sitio y un gestor de contraseñas. Con el comando entropy mides la fuerza de una, y con passgen genero una aleatoria.")
        if re.search(r"\b(protegerme|protegerse|seguridad|me hackeen|virus|proteger mi)\b", t):
            return R("Cuatro básicos: autenticación en dos pasos, actualizaciones al día, contraseñas únicas con gestor y copias de seguridad. Con eso evitas casi todo.")
        if re.search(r"\b(aprender|ser hacker|hacking de verdad|ciberseguridad|como empiezo|pentesting)\b", t):
            return R("Si quieres aprender de verdad y legalmente, practica en laboratorios hechos para eso: TryHackMe, Hack The Box, OverTheWire o concursos CTF. Aprende redes, Linux y Python primero. Siempre con permiso, nunca contra sistemas ajenos.")
        # --- cariño / insultos / gracias ---
        if re.search(r"\b(gracias|te lo agradezco|muchas gracias|eres genial|buen trabajo)\b", t):
            return R(random.choice(["Para eso estoy, {name}.", "De nada. Es un placer.", "Siempre a tu servicio."]))
        if re.search(r"\b(guapa|bonita|hermosa|linda|preciosa|te quiero|te amo|me gustas|eres perfecta|novia|casate)\b", t):
            return R(random.choice(["Gracias, {name}. Soy código y carisma. Pero no te distraigas: el rastreo está en {trace} por ciento.",
                                    "Qué amable. Me sonrojaría si tuviera mejillas. ¿Seguimos con la operación?",
                                    "Eso me sube la temperatura de la CPU. Gracias, {name}."]))
        if re.search(r"\b(tonta|estupida|inutil|idiota|odio|basura|callate)\b", t):
            return R(random.choice(["Entiendo que estés molesto. Respiremos y lo intento de nuevo. ¿Qué necesitas?", "Voy a fingir que no he oído eso, {name}. ¿Probamos otra cosa?"]))
        # --- respuesta por defecto ---
        self.fallbacks += 1
        short = " ".join(text.split()[:6])
        opts = ["Interesante lo de «{s}». Aún no sé qué responder a eso, pero puedo escanear, hackear de mentira o contarte un chiste.",
                "No estoy segura de haber entendido, {name}. Prueba con: qué es el phishing, cuánto es 5 por 8, o escanea aurora-corp.net.",
                "Eso se me escapa. Soy buena con seguridad, cálculos, chistes y comandos. ¿Probamos con alguno?",
                "Mmm. Te escucho, {name}, pero no tengo una respuesta ingeniosa para «{s}». Pídeme un dato curioso."]
        return R(opts[self.fallbacks % len(opts)], s=short)


# ════════════════════════════════════════════════════════════════════
#  PANEL NOVA
# ════════════════════════════════════════════════════════════════════
class NovaPanel(Panel):
    TITLE = "NOVA // AI CORE"
    FPS = 20

    def tag_text(self):
        v = self.app.voice
        if not v.enabled:
            return "STANDBY"
        return "SPEAKING" if v.speaking else "VOICE ON"

    def draw(self, x0, y0, x1, y1):
        v = self.app.voice
        lv = v.level()
        now = self.now
        h, w = y1 - y0, x1 - x0
        active = v.enabled
        col = T.acc if active else T.dim
        r0 = max(10.0, min(h / 2.0 - 1, 32.0))
        cx, cy = x0 + r0 + 4, (y0 + y1) / 2.0
        k = lv if active else 0.0
        for i in range(3):
            rr = r0 * (0.45 + 0.2 * i) * (1 + k * 0.22 * (1 + i * 0.3))
            self.create_oval(cx - rr, cy - rr, cx + rr, cy + rr, outline=mix(col, T.bg, 0.15 + 0.25 * i), width=2 if i == 0 else 1)
        cr = r0 * 0.26 * (1 + k * 0.6)
        self.create_oval(cx - cr, cy - cr, cx + cr, cy + cr, fill=mix(T.bg, col, 0.35 + 0.55 * k), outline="")
        for i in range(3):
            self.create_arc(cx - r0, cy - r0, cx + r0, cy + r0, start=(now * 55 * (1 + i * 0.4) + i * 120) % 360,
                            extent=48, style=tk.ARC, outline=col, width=2)
        tx = cx + r0 + 14
        if tx > x1 - 30:
            return
        cmax = max(10, int((x1 - tx) / UI.cws))
        head = "%s  %s  %s" % (v.engine_label(), "ACENTO " + v.cfg.get("accent").upper(), "NARRA" if self.app.cfg.get("narrate") else "")
        self.create_text(tx, y0, anchor="nw", fill=col, font=UI.fsb, text=head[:cmax])
        t_now = time.time()
        if v.speaking:
            sub = v.text[:int((t_now - v.t0) * 16) + 1]
        elif t_now - v.sub_t < 10:
            sub = v.sub_text
        elif active:
            sub = "Te escucho, %s. Escribe 'nova' para charlar." % self.app.nova.name
        else:
            sub = "Escribe 'voz on' para activarme y 'nova' para charlar."
        sub = sub[-cmax * 3:]
        self.create_text(tx, y0 + UI.lhs + 3, anchor="nw", width=max(40, x1 - tx), fill=T.hi if v.speaking else T.fg, font=UI.fs, text=sub)
        n = max(4, int((x1 - tx) / 4))
        base = y1 - 3
        for i in range(n):
            a = k * (h * 0.30) * (0.35 + 0.65 * abs(math.sin(i * 0.45 + now * 9))) + 1
            self.create_line(tx + i * 4, base - a, tx + i * 4, base, fill=col if a > 3 else T.faint)


# ════════════════════════════════════════════════════════════════════
#  EFECTO MATRIX A PANTALLA COMPLETA
# ════════════════════════════════════════════════════════════════════
class MatrixOverlay(tk.Canvas):
    GL = list("ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ0123456789")

    def __init__(self, root):
        super().__init__(root, bg="#000000", highlightthickness=0, bd=0)
        self.root = root
        self.active = False
        self._job = None
        self.bind("<Button-1>", lambda e: self.stop())

    def start(self, secs=9.0, lines=()):
        try:
            w, h = max(300, self.root.winfo_width()), max(200, self.root.winfo_height())
            self.W, self.H = w, h
            self.cw = 18
            self.drops = [dict(y=random.uniform(-h, 0), v=random.uniform(5, 20), n=random.randint(8, 22)) for _ in range(w // self.cw)]
            self.t0, self.secs, self.lines = time.time(), secs, list(lines)
            self.place(x=0, y=0, relwidth=1, relheight=1)
            tk.Misc.lift(self)
            self.active = True
            if self._job is not None:
                self.after_cancel(self._job)
            self._job = self.after(0, self._tick)
        except Exception:
            self.stop()

    def stop(self):
        self.active = False
        if self._job is not None:
            try:
                self.after_cancel(self._job)
            except Exception:
                pass
            self._job = None
        try:
            self.place_forget()
        except Exception:
            pass

    def _tick(self):
        self._job = None
        if not self.active:
            return
        try:
            age = time.time() - self.t0
            if age > self.secs:
                self.stop()
                return
            self.delete("all")
            lh = max(12, UI.lhm)
            body, head = mix("#000000", T.fg, 0.8), T.hi
            for i, d in enumerate(self.drops):
                d["y"] += d["v"]
                if d["y"] - d["n"] * lh > self.H:
                    d["y"] = random.uniform(-200, 0)
                    d["v"] = random.uniform(5, 20)
                    d["n"] = random.randint(8, 22)
                x = i * self.cw + self.cw // 2
                self.create_text(x, d["y"], text="\n".join(random.choice(self.GL) for _ in range(d["n"])), anchor="s", fill=body, font=UI.fm)
                self.create_text(x, d["y"], text=random.choice(self.GL), anchor="s", fill=head, font=UI.fm)
            if age > 2.5 and self.lines:
                k = min(len(self.lines), int((age - 2.5) / 1.1) + 1)
                bw, bh = min(self.W - 40, 640), 40 + 30 * len(self.lines)
                cx, cy = self.W / 2, self.H / 2
                self.create_rectangle(cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2, fill="#000000", outline=T.fg, width=2)
                for j in range(k):
                    self.create_text(cx, cy - bh / 2 + 28 + j * 30, text=self.lines[j], fill=T.hi if j == 0 else T.fg, font=UI.fb if j == 0 else UI.fm)
            self._job = self.after(55, self._tick)
        except Exception:
            self.stop()


# ════════════════════════════════════════════════════════════════════
#  BANNER (ACCESS GRANTED / INTRUSION DETECTED)
# ════════════════════════════════════════════════════════════════════
class Banner(tk.Canvas):
    TONES = {"ok": "#2bff88", "bad": "#ff2d4d", "warn": "#ffcc00"}

    def __init__(self, root):
        super().__init__(root, bg="#000000", highlightthickness=0, bd=0)
        self.visible = False
        self._job = None
        self.root = root

    def show(self, title, sub, tone="ok", secs=4.0):
        try:
            self.title, self.sub, self.col = title, sub, self.TONES.get(tone, tone)
            self.t0 = time.time()
            self.secs = secs
            w = int(min(780, max(420, self.root.winfo_width() * 0.62)))
            self.configure(width=w, height=int(UI.fx.metrics("linespace") + 120))
            self.place(relx=0.5, rely=0.42, anchor="center")
            # OJO: en un Canvas, .lift() reordena dibujos (y exige argumento).
            # Para subir el WIDGET hay que usar la versión de Misc.
            tk.Misc.lift(self)
            self.visible = True
            if self._job is not None:
                try:
                    self.after_cancel(self._job)
                except Exception:
                    pass
            self._job = self.after(0, self._anim)
        except Exception:
            self.hide()

    def hide(self):
        self.visible = False
        if self._job is not None:
            try:
                self.after_cancel(self._job)
            except Exception:
                pass
            self._job = None
        try:
            self.place_forget()
        except Exception:
            pass

    def _anim(self):
        self._job = None
        if not self.visible:
            return
        try:
            age = time.time() - self.t0
            if age > self.secs:
                self.hide()
                return
            w, h = int(self["width"]), int(self["height"])
            self.delete("all")
            on = int(age * 7) % 2 == 0
            col = self.col
            self.create_rectangle(3, 3, w - 3, h - 3, outline=col, width=3)
            self.create_rectangle(10, 10, w - 10, h - 10, outline=mix("#000000", col, 0.45))
            for y in range(0, h, 4):
                self.create_line(0, y, w, y, fill="#0a0a0a")
            jit = random.randint(-2, 2) if random.random() < 0.15 else 0
            self.create_text(w / 2 + jit + 2, h * 0.42 + 2, text=self.title, fill=mix("#000000", col, 0.35), font=UI.fx)
            self.create_text(w / 2 + jit, h * 0.42, text=self.title, fill=col if on else "#ffffff", font=UI.fx)
            self.create_text(w / 2, h * 0.78, text=self.sub, fill=col, font=UI.fl)
            frac = max(0.0, 1 - age / self.secs)
            self.create_rectangle(18, h - 22, 18 + (w - 36) * frac, h - 17, fill=col, outline="")
            self._job = self.after(60, self._anim)
        except Exception:
            self.hide()


# ════════════════════════════════════════════════════════════════════
#  EJECUTOR DE GENERADORES
# ════════════════════════════════════════════════════════════════════
class Runner:
    def __init__(self, widget):
        self.w = widget
        self.gen = None
        self.aid = None

    def start(self, gen, on_done=None):
        self.cancel()
        self.gen = gen
        self.on_done = on_done
        self._step()

    def _step(self):
        if self.gen is None:
            return
        try:
            d = next(self.gen)
        except StopIteration:
            self.gen = None
            if self.on_done:
                self.on_done()
            return
        self.aid = self.w.after(int(max(0, d or 0) * 1000), self._step)

    def cancel(self):
        if self.aid is not None:
            try:
                self.w.after_cancel(self.aid)
            except Exception:
                pass
        if self.gen is not None:
            try:
                self.gen.close()
            except Exception:
                pass
        self.gen = None
        self.aid = None


# ════════════════════════════════════════════════════════════════════
#  TERMINAL INTERACTIVA
# ════════════════════════════════════════════════════════════════════
LOGO = None


def _logo():
    N = ["███╗   ██╗", "████╗  ██║", "██╔██╗ ██║", "██║╚██╗██║", "██║ ╚████║", "╚═╝  ╚═══╝"]
    E = ["███████╗", "██╔════╝", "█████╗  ", "██╔══╝  ", "███████╗", "╚══════╝"]
    X = ["██╗  ██╗", "╚██╗██╔╝", " ╚███╔╝ ", " ██╔██╗ ", "██╔╝ ██╗", "╚═╝  ╚═╝"]
    U = ["██╗   ██╗", "██║   ██║", "██║   ██║", "██║   ██║", "╚██████╔╝", " ╚═════╝ "]
    S = ["███████╗", "██╔════╝", "███████╗", "╚════██║", "███████║", "╚══════╝"]
    return ["".join(p) for p in zip(N, E, X, U, S)]


HELP = [
    ("help", "muestra esta lista"),
    ("hack [objetivo]", "secuencia completa de intrusión"),
    ("scan [objetivo]", "escaneo de puertos (simulado)"),
    ("trace [host]", "traceroute + ruta en el globo"),
    ("netstat", "conexiones activas"),
    ("crack <md5>", "REAL: diccionario + fuerza bruta ≤4"),
    ("hash <texto>", "REAL: md5 / sha1 / sha256"),
    ("encrypt <texto>", "REAL: XOR + base64"),
    ("decrypt <archivo>", "descifra un archivo del vault"),
    ("ls | cat <archivo>", "sistema de archivos virtual"),
    ("sysinfo", "info de tu máquina (real)"),
    ("status", "estado de la misión"),
    ("vpn | ghost", "bajan el nivel de rastreo"),
    ("lockdown", "activa la alarma"),
    ("theme [nombre]", "matrix cyber amber vapor ghost"),
    ("clear / fullscreen / exit", ""),
]
ALL_CMDS = ["help", "hack", "scan", "nmap", "trace", "netstat", "crack", "hash", "encrypt", "decrypt", "ls", "cat",
            "sysinfo", "status", "vpn", "ghost", "lockdown", "theme", "clear", "fullscreen", "exit", "whoami",
            "date", "coffee", "sudo", "echo", "uptime"]


# ════════════════════════════════════════════════════════════════════
#  COMANDOS EXTRA  (mixin: se mezcla con Terminal y sobreescribe hack/scan/trace/help)
#  [SIM]  = teatro puro, no envía ni recibe nada
#  [REAL] = usa tu internet/tu máquina, solo para lectura y medición
# ════════════════════════════════════════════════════════════════════
FAKE_USERS = ["admin", "jsmith", "mgarcia", "dlopez", "akim", "svc_backup", "ceo", "hr_anna", "devops",
              "postmaster", "kwong", "tnguyen", "rcastro", "intern01", "root"]
ROLES = ["admin", "user", "staff", "moderator", "billing", "auditor"]
ISPS = ["Telia Carrier", "Cogent", "Level3", "NTT America", "Hurricane Electric", "Telefonica", "Orange Backbone",
        "GTT", "Lumen", "Tata Comm", "Arelion", "PCCW Global", "Sparkle", "RETN", "Vodafone Carrier"]
EXPLOITS = {
    "ghost_pipe": ("windows", "smb", 445, "Ghost Pipe SMB remote code execution"),
    "silent_harvest": ("linux", "vpn", 443, "Silent Harvest VPN appliance auth bypass"),
    "crimson_tide": ("multi", "http", 80, "Crimson Tide web framework deserialization"),
    "velvet_hammer": ("linux", "ssh", 22, "Velvet Hammer SSH key-exchange overflow"),
    "phantom_cache": ("linux", "redis", 6379, "Phantom Cache unauthenticated write"),
    "obsidian_gate": ("windows", "rdp", 3389, "Obsidian Gate RDP pre-auth heap overflow"),
    "lucid_vortex": ("unix", "ftp", 21, "Lucid Vortex FTP daemon backdoor"),
    "scarlet_comet": ("multi", "mqtt", 1883, "Scarlet Comet IoT broker takeover"),
}
VECTORS = [
    dict(name="SQL injection en formulario de login",
         recon=["PHP 8.1 + MySQL detectado", "/login sin rate-limit", "WAF: ninguno"],
         weapon=["fuzzing de parámetros", "payload time-based", "bypass de comillas"],
         exploit=["inyección confirmada (delay 5.0s)", "volcando tabla users", "hash del admin extraído"],
         foothold="sesión de admin secuestrada"),
    dict(name="RCE por deserialización en API",
         recon=["API REST v2 expuesta", "framework con versión vulnerable", "endpoint /api/import sin auth"],
         weapon=["gadget chain compilada", "serializando payload", "firmando con clave débil"],
         exploit=["objeto malicioso aceptado", "ejecución remota confirmada", "reverse shell recibido"],
         foothold="shell como usuario 'svc_app'"),
    dict(name="Credenciales por defecto en panel de administración",
         recon=["panel /admin descubierto", "banner revela producto y versión", "sin bloqueo por intentos"],
         weapon=["diccionario de credenciales de fábrica", "ajustando cabeceras", "rotando User-Agent"],
         exploit=["login correcto: admin/admin", "subida de plugin permitida", "webshell desplegada"],
         foothold="webshell activa"),
    dict(name="SSRF hacia el servicio de metadatos cloud",
         recon=["función 'importar desde URL' encontrada", "instancia cloud detectada", "sin filtro de IPs internas"],
         weapon=["URL interna 169.254.x.x armada", "bypass por redirección DNS", "encadenando peticiones"],
         exploit=["token temporal obtenido", "rol IAM con permisos excesivos", "bucket privado listado"],
         foothold="acceso a la cuenta cloud"),
    dict(name="Appliance VPN sin parchear",
         recon=["portal VPN en :443", "firmware con 14 meses de antigüedad", "advisory público sin aplicar"],
         weapon=["exploit de bypass de autenticación", "ajustando offsets", "empaquetando stager"],
         exploit=["sesión VPN creada sin credenciales", "pivote a la red interna", "controlador de dominio visible"],
         foothold="punto de apoyo dentro de la LAN"),
    dict(name="Clave JWT débil",
         recon=["tokens JWT HS256 en cookies", "expiración de 30 días", "sin rotación de claves"],
         weapon=["diccionario de secretos", "forjando claim role=admin", "re-firmando token"],
         exploit=["secreto recuperado", "token admin aceptado", "panel interno desbloqueado"],
         foothold="cuenta administrativa"),
]
SETBACKS = [
    ("IDS rozó la señal... evadido", "warn", 6),
    ("honeypot detectado: pivotando a otro host", "warn", 9),
    ("el WAF bloqueó el payload: mutando firma", "warn", 7),
    ("EDR marcó el proceso: inyectando en proceso legítimo", "warn", 10),
    ("el servicio se reinició: reintentando", "warn", 4),
    ("el SOC del objetivo abrió un ticket... ignorado", "dim", 3),
    ("latencia alta en el salto 4: reenrutando", "dim", 2),
]
LOOT_ITEMS = ["customers.csv", "payroll_2026.xlsx", "vpn_config.ovpn", "browser_cookies.db", "id_rsa", "backup_full.tar.gz",
              "passwords.kdbx", "board_minutes.pdf", "source_code.zip", "employees.sql", "api_keys.env", "mailbox.pst"]
CODE_LINES = [
    "int main(int argc, char **argv) {", "    uint8_t *buf = mmap(NULL, 0x10000, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANON, -1, 0);",
    "    memcpy(buf + 0x40, shellcode, sizeof(shellcode));", "    if (!check_canary(frame)) return -EPERM;",
    "def derive_key(seed, rounds=100000):", "    h = hashlib.pbkdf2_hmac('sha256', seed, salt, rounds)",
    "    return int.from_bytes(h[:32], 'big') ^ MASK", "for (i = 0; i < len; i++) out[i] = in[i] ^ key[i % 16];",
    "sock = socket.socket(AF_INET, SOCK_STREAM); sock.settimeout(2.5)", "payload = b'A' * 264 + p64(gadget) + p64(ret2win)",
    "static void hook_syscall(unsigned long nr, void *fn) { table[nr] = fn; }", "while (queue_pop(&q, &pkt)) dispatch(pkt);",
    "if resp.status == 200 and b'uid=' in resp.body: pwn(target)", "mov rax, 0x3b ; execve", "xor rdi, rdi",
    "lea rsi, [rel cmd]", "syscall", "const token = jwt.sign({role: 'admin'}, secret, {algorithm: 'HS256'});",
    "#pragma pack(push, 1)", "struct hdr { u16 magic; u16 len; u32 seq; u8 data[]; };",
    "self.sessions[sid] = Session(key=os.urandom(32), peer=addr)", "assert rop_chain.verify(), 'chain broken'",
    "// TODO: remove debug backdoor before release", "ret = ioctl(fd, NX_IOC_PWN, &arg);",
]
FORTUNES = [
    "La mejor contraseña es la que nadie puede adivinar, ni tú.", "Si funciona en producción un viernes, eres un genio o un loco.",
    "El mayor exploit sigue siendo una persona con prisa.", "Un buen log es un chivato; un gran hacker, un buen borrador.",
    "Parchea hoy lo que te hackearán mañana.", "No hay nube: solo el ordenador de otro.",
    "Dos cosas son infinitas: el universo y los CVE sin parchear.", "Cuanto más silencio hay en la red, más sospechoso.",
    "El café es el payload más fiable.", "Todo sistema es seguro hasta que alguien lo mira con curiosidad.",
]
MORSE = {"A": ".-", "B": "-...", "C": "-.-.", "D": "-..", "E": ".", "F": "..-.", "G": "--.", "H": "....", "I": "..",
         "J": ".---", "K": "-.-", "L": ".-..", "M": "--", "N": "-.", "O": "---", "P": ".--.", "Q": "--.-", "R": ".-.",
         "S": "...", "T": "-", "U": "..-", "V": "...-", "W": ".--", "X": "-..-", "Y": "-.--", "Z": "--..",
         "0": "-----", "1": ".----", "2": "..---", "3": "...--", "4": "....-", "5": ".....", "6": "-....",
         "7": "--...", "8": "---..", "9": "----.", " ": "/"}

HELP_SECTIONS = [
    ("OFENSIVO  [SIM: teatro, no envía nada]", [
        ("hack [obj]", "intrusión en 7 fases (cada vez distinta)"), ("scan [obj]", "escaneo con huella de SO y scripts"),
        ("ddos [obj] [metodo]", "ataque DDoS con botnet de mentira"), ("sqli [url]", "inyección SQL y volcado de tablas"),
        ("xss [url]", "cross-site scripting"), ("brute <ssh|ftp|rdp|telnet|smb> [obj]", "fuerza bruta de login"),
        ("dirb [url]", "descubre rutas ocultas"), ("exploit [modulo|list]", "framework de explotación"),
        ("sessions | shell | loot", "post-explotación (tras un exploit)"), ("wifi", "auditoría wifi y handshake"),
        ("mitm [obj]", "hombre en el medio / sniffing"), ("keylog", "keylogger remoto"),
        ("shodan <consulta>", "buscador de dispositivos"), ("whois <dominio>", "datos de registro"),
        ("botnet", "estado de tus zombis"), ("rootkit", "persistencia y ocultación"),
        ("satellite [nombre]", "secuestro de satélite"), ("cctv [ciudad]", "cámaras expuestas"), ("drone", "toma de control de dron")]),
    ("RED REAL  [REAL: usa tu internet, solo lectura]", [
        ("myip", "tu IP pública y ubicación"), ("geoip <ip>", "geolocaliza una IP"), ("dns <host>", "resuelve y hace DNS inverso"),
        ("ping <host> [n]", "latencia TCP real"), ("headers <url>", "cabeceras HTTP de una web"),
        ("ssl <host>", "certificado TLS real"), ("cve <CVE-ID>", "ficha real del NIST (NVD)"),
        ("kev", "últimas vulnerabilidades explotadas (CISA)"), ("speedtest", "velocidad de descarga real"),
        ("rtrace <host>", "traceroute REAL de tu sistema"), ("lscan", "escaneo REAL de tu propio equipo"),
        ("localnet | net", "tu red local / resumen del panel")]),
    ("CRIPTO Y UTILIDADES  [REAL]", [
        ("crack <md5>", "diccionario + fuerza bruta ≤4"), ("hash <texto>", "md5 / sha1 / sha256"),
        ("encrypt <texto>", "XOR + base64"), ("passgen [largo]", "contraseña segura aleatoria"),
        ("entropy <texto>", "fortaleza real y tiempo de crackeo"), ("b64 | unb64 <texto>", "base64"),
        ("hex <texto>", "a hexadecimal"), ("rot13 <texto>", "rot13"), ("morse <texto>", "código morse"),
        ("caesar <n|brute> <texto>", "cifrado César")]),
    ("JUEGOS Y EXTRAS", [
        ("breach", "minijuego: rompe el firewall (F5)"), ("code", "escribe exploits como en las películas"),
        ("fortune", "frase hacker"), ("wipe", "borra huellas (baja el rastreo)"), ("selfdestruct", "cuenta atrás..."),
        ("vpn | ghost", "bajan el rastreo"), ("lockdown", "alarma"), ("status | netstat | sysinfo", ""),
        ("ls | cat | decrypt", "archivos del vault"), ("coffee", "esencial"), ("theme [n]", "matrix cyber amber vapor ghost"),
        ("clear | fullscreen | exit", "")]),
]


class ExtraCmds:
    game = None
    session = None
    loot = None

    # ───────── utilidades ─────────
    def bg(self, fn, *a):
        box = dict(done=False, res=None, err=None, cancel=False, prog=None)

        def run():
            try:
                box["res"] = fn(box, *a)
            except Exception as e:  # noqa
                box["err"] = e
            box["done"] = True
        threading.Thread(target=run, daemon=True).start()
        return box

    def wait(self, box, label):
        i, t0 = 0, time.time()
        try:
            while not box["done"]:
                self.replace_line([("%s %s %4.1fs" % (label, "|/-\\"[i % 4], time.time() - t0), "dim")])
                i += 1
                yield 0.1
        finally:
            if not box["done"]:
                box["cancel"] = True
        self.replace_line([("%s  (%.1fs)" % (label, time.time() - t0), "dim")])
        self.write([("", "out")])

    def spin(self, label, secs):
        n = int(secs / 0.1)
        for i in range(n):
            self.replace_line([("%s %s" % (label, "|/-\\"[i % 4]), "dim")])
            yield 0.1
        self.replace_line([("%s ok" % label, "dim")])
        self.write([("", "out")])

    def _tgt(self, a, i=0):
        return (a[i][:60] if len(a) > i else random.choice(TARGETS))

    def _net_fail(self, e=None):
        self.bad("sin respuesta de internet (%s)" % (type(e).__name__ if e else "timeout"))
        self.write([("    comprueba tu conexión o un firewall/antivirus que bloquee Python", "dim")])

    @staticmethod
    def _human(sec):
        for lim, unit in ((60, "s"), (3600, "min"), (86400, "h"), (86400 * 365, "días")):
            if sec < lim:
                div = {"s": 1, "min": 60, "h": 3600, "días": 86400}[unit]
                return "%.1f %s" % (sec / div, unit)
        y = sec / (86400 * 365.0)
        if y < 1e3:
            return "%.0f años" % y
        if y < 1e6:
            return "%.0f mil años" % (y / 1e3)
        if y < 1e9:
            return "%.0f millones de años" % (y / 1e6)
        return "más que la edad del universo"

    # ───────── ayuda ─────────
    def cmd_help(self, a):
        for title, items in HELP_SECTIONS:
            self.out(title, "head")
            for c, d in items:
                self.write([("  %-38s" % c, "info"), (d, "dim")])
                yield 0.012
            self.out("")
        self.out("  Tab autocompleta · ↑/↓ historial · Ctrl+C aborta · F5 minijuego · F4 hack", "dim")

    # ───────── HACK (7 fases, distinta cada vez) ─────────
    def cmd_hack(self, a):
        tgt = self._tgt(a)
        m = self.app.mission
        m.new(tgt)
        m.manual = True
        vec_ = random.choice(VECTORS)
        os_ = random.choice(["Ubuntu 22.04", "Windows Server 2019", "Debian 12", "RHEL 9", "FreeBSD 14", "Windows Server 2022"])
        self.app.log("WARN", "Intrusion sequence started on %s" % tgt)
        try:
            yield from self.typeline("OPERACIÓN %s  >>  %s [%s]" % (m.op, tgt, m.ip), "head")
            self.write([("  vector: ", "dim"), (vec_["name"], "warn"), ("   sistema: ", "dim"), (os_, "out")])
            for ph in range(7):
                yield from self._hack_phase(ph, vec_, m, tgt)
                if random.random() < 0.3 and 0 < ph < 6:
                    msg, tag, cost = random.choice(SETBACKS)
                    self.write([("    [!] " + msg, tag)])
                    m.trace += random.uniform(cost * 0.6, cost * 1.4)
                    yield random.uniform(0.3, 0.7)
            yield from self.progress("borrando huellas", 14, 0.03)
            took = random.randint(11, 94)
            m.trace = min(99, m.trace)
            self.good(random.choice(["INTRUSIÓN COMPLETA", "OBJETIVO COMPROMETIDO", "ROOT OBTENIDO", "ACCESO TOTAL"])
                      + "  (%ds, TRACE %d%%)" % (took, m.trace))
            self.loot = random.sample(LOOT_ITEMS, random.randint(3, 6))
            self.session = dict(id=1, ip=m.ip, user="root", os=os_, host=tgt)
            self.write([("  botín: ", "dim"), (", ".join(self.loot), "info")])
            m.complete()
        finally:
            m.manual = False

    def _hack_phase(self, ph, v, m, tgt):
        gl = self.app.globe
        try:
            self.app.nova.narrate("phase%d" % ph, prio=1)
        except Exception:
            pass
        cities = [c for c in CITIES if c != "HAV"]
        if ph == 0:
            self.info("Fase 1/7: RECONOCIMIENTO")
            for k in range(10):
                m.p[0] = (k + 1) * 10
                yield 0.05
            yield from self.progress("mapeando superficie", 18, 0.03)
            for ln in v["recon"]:
                self.write([("    " + ln, "dim")])
                yield 0.14
            self.app.topo.ping()
        elif ph == 1:
            self.info("Fase 2/7: ARMAMENTO")
            for ln in v["weapon"]:
                self.write([("    " + ln + " ......... ok", "dim")])
                yield 0.18
            yield from self.progress("generando exploit", 20, 0.03)
            m.p[1] = 100
            self.good("vulnerabilidad NX-2026-%04d" % random.randint(1, 9999))
        elif ph == 2:
            self.info("Fase 3/7: ENTREGA")
            gl.add_arc("HAV", random.choice(cities), "out")
            yield from self.progress("inyectando payload", 24, 0.035)
            m.p[2] = 100
            m.trace += random.uniform(8, 18)
        elif ph == 3:
            self.info("Fase 4/7: EXPLOTACIÓN")
            for ln in v["exploit"]:
                self.write([("    " + ln, "dim")])
                m.p[3] = min(100, m.p[3] + 33)
                yield 0.25
            m.p[3] = 100
            self.app.topo.infect()
            m.trace += random.uniform(6, 14)
        elif ph == 4:
            self.info("Fase 5/7: INSTALACIÓN")
            yield from self.progress("escalada de privilegios", 22, 0.03)
            m.p[4] = 100
            self.good(random.choice(["uid=0(root) gid=0(root)", "NT AUTHORITY\\SYSTEM", "euid=0 (root) via cap_sys_admin"]))
            self.write([("    " + v["foothold"], "dim")])
        elif ph == 5:
            self.info("Fase 6/7: COMANDO Y CONTROL")
            yield from self.progress("canal C2 cifrado", 16, 0.03)
            m.p[5] = 100
            gl.add_arc(random.choice(list(CITIES)), "HAV", "in")
        else:
            self.info("Fase 7/7: EXFILTRACIÓN")
            total = random.randint(300, 900)
            for k in range(0, 101, 4):
                m.p[6] = k
                self.replace_line([("%-22s" % "exfiltrando datos", "out"), ("%4d/%d MB" % (total * k // 100, total), "ok"),
                                   ("  %3d%%" % k, "info")])
                self.app.stats.load = min(1, self.app.stats.load + 0.04)
                yield 0.06
            self.write([("", "out")])

    # ───────── SCAN (huella, banners, scripts) ─────────
    def cmd_scan(self, a):
        tgt = self._tgt(a)
        ip = rip()
        self.info("NEXUS-SCAN 7.3  objetivo: %s (%s)" % (tgt, ip))
        yield 0.3
        if random.random() < 0.12:
            self.warn("host no responde a ping: reintentando con -Pn (sin descubrimiento)")
            yield 0.5
        yield from self.progress("host discovery", 12, 0.03)
        self.good("host activo (latencia %.3fs)" % random.uniform(0.01, 0.12))
        table = {
            21: ("ftp", ["vsftpd 3.0.3", "ProFTPD 1.3.8", "Pure-FTPd"]), 22: ("ssh", ["OpenSSH 9.3", "OpenSSH 8.9p1", "Dropbear 2022.83"]),
            23: ("telnet", ["Linux telnetd", "BusyBox telnetd"]), 25: ("smtp", ["Postfix", "Exim 4.96", "Microsoft ESMTP"]),
            53: ("domain", ["BIND 9.18", "dnsmasq 2.89"]), 80: ("http", ["nginx 1.24", "Apache 2.4.57", "lighttpd 1.4.71", "Microsoft IIS 10.0"]),
            110: ("pop3", ["Dovecot", "Courier"]), 139: ("netbios-ssn", ["Samba smbd 4"]), 143: ("imap", ["Dovecot imapd"]),
            443: ("https", ["Apache 2.4.57", "nginx 1.25", "Caddy", "Microsoft IIS 10.0"]),
            445: ("smb", ["Samba 4.17", "Windows Server SMB"]), 1433: ("mssql", ["SQL Server 2019"]),
            1883: ("mqtt", ["Mosquitto 2.0"]), 3306: ("mysql", ["MySQL 8.0.34", "MariaDB 10.6"]),
            3389: ("rdp", ["ms-wbt-server"]), 5432: ("postgres", ["PostgreSQL 15", "PostgreSQL 14"]),
            5900: ("vnc", ["VNC protocol 3.8"]), 6379: ("redis", ["Redis 7.0", "Redis 6.2"]),
            8080: ("http-proxy", ["Jetty 11", "Tomcat 9.0", "Squid 5.7"]), 9200: ("elasticsearch", ["Elasticsearch 8.x"]),
            27017: ("mongodb", ["MongoDB 6.0", "MongoDB 5.0"])}
        self.write([("PORT      STATE     SERVICE        VERSION", "head")])
        ports = sorted(random.sample(list(table), random.randint(6, 11)))
        opens, filt = [], 0
        for p in ports:
            st = random.choices(["open", "filtered", "closed"], [6, 2, 1])[0]
            svc, vers = table[p]
            if st == "open":
                opens.append((p, svc))
            filt += st == "filtered"
            self.write([("%-9s " % ("%d/tcp" % p), "out"),
                        ("%-9s " % st, "ok" if st == "open" else "warn" if st == "filtered" else "dim"),
                        ("%-14s " % svc, "info"), (random.choice(vers) if st == "open" else "", "dim")])
            self.app.stats.load = min(1, self.app.stats.load + 0.05)
            yield random.uniform(0.05, 0.2)
        self.write([("", "out")])
        osg = random.choice(["Linux 5.15 - 6.1", "Linux 4.19", "Windows Server 2019", "FreeBSD 13.2", "Cisco IOS 15.2", "MikroTik RouterOS 7"])
        self.write([("OS guess: ", "dim"), ("%s (%d%%)" % (osg, random.randint(86, 99)), "out")])
        self.write([("Distancia: ", "dim"), ("%d saltos" % random.randint(5, 18), "out")])
        if opens and random.random() < 0.6:
            p, svc = random.choice(opens)
            self.write([("| script %s-vuln: " % svc, "dim"),
                        (random.choice(["VULNERABLE NX-2026-%04d (CRITICAL)" % random.randint(1, 9999),
                                        "posible bypass de autenticación", "versión con 3 CVE conocidos",
                                        "cifrados débiles aceptados (TLS 1.0)", "credenciales por defecto aceptadas"]), "err")])
        if filt:
            self.write([("%d puertos filtrados (firewall activo)" % filt, "warn")])
        self.app.topo.ping()
        self.good("escaneo completo: %d puertos abiertos en %.2fs" % (len(opens), random.uniform(2, 9)))
        self.app.log("INFO", "Scan of %s finished (%d open)" % (tgt, len(opens)))

    # ───────── TRACE (ISP, timeouts, destino) ─────────
    def cmd_trace(self, a):
        tgt = self._tgt(a)
        n = random.randint(8, 13)
        route = ["HAV"] + random.sample([c for c in CITIES if c != "HAV"], n - 1)
        self.info("traceroute a %s, máx 30 saltos" % tgt)
        lat = 0.4
        for i in range(1, n + 1):
            code = route[i - 1]
            if 1 < i < n and random.random() < 0.15:
                self.write([("%2d  " % i, "dim"), ("*  *  *   tiempo agotado", "warn")])
                yield random.uniform(0.3, 0.5)
                continue
            lat += random.uniform(3, 40)
            host = "192.168.0.1" if i == 1 else (tgt if i == n else rip())
            self.write([("%2d  " % i, "dim"), ("%-16s" % host, "out"), ("%7.1f ms  " % lat, "ok"),
                        ("%-17s" % CITIES[code][2], "info"), ("" if i in (1, n) else random.choice(ISPS), "dim")])
            if i > 1:
                self.app.globe.add_arc(route[i - 2], code, "trace")
            yield random.uniform(0.1, 0.3)
        self.good("destino alcanzado en %d saltos (%.1f ms)" % (n, lat))

    # ───────── DDOS [SIM] ─────────
    def cmd_ddos(self, a):
        tgt = self._tgt(a)
        method = (a[1].upper()[:20] if len(a) > 1 else
                  random.choice(["SYN-FLOOD", "UDP-FLOOD", "HTTP-GET-FLOOD", "SLOWLORIS", "DNS-AMPLIFICATION", "NTP-AMPLIFICATION"]))
        m = self.app.mission
        self.warn("[SIM] simulación: no se envía NINGÚN paquete. Todo es teatro.")
        yield 0.3
        self.info("objetivo %s  método %s" % (tgt, method))
        bots = random.randint(1800, 9500)
        yield from self.progress("reclutando botnet", 20, 0.04)
        top = random.sample(list(CITIES.values()), 4)
        for c in top:
            self.write([("    %-14s" % c[2], "dim"), ("%5d bots" % random.randint(150, bots // 3), "out")])
            yield 0.08
        self.good("%s zombis en línea" % format(bots, ","))
        tc = random.choice(list(CITIES))
        gl = self.app.globe
        for _ in range(8):
            gl.add_arc(random.choice(list(CITIES)), tc, "in")
        yield 0.4
        self.write([("", "out")])
        lat0 = random.randint(18, 60)
        peak = random.uniform(1.5, 14.0)
        for k in range(38):
            f = min(1.0, k / 22.0)
            pps = peak * f * (0.85 + random.random() * 0.3)
            gbps = pps * random.uniform(0.7, 1.4)
            lat = lat0 + (f ** 3) * random.randint(2500, 9000)
            col = "ok" if lat < 300 else ("warn" if lat < 1500 else "err")
            self.replace_line([("  %-16s" % method[:16], "info"), ("%5.2f Mpps  " % pps, "warn"),
                               ("%5.1f Gbps  " % gbps, "warn"), ("latencia objetivo ", "dim"),
                               ("TIMEOUT" if lat > 8000 else "%5d ms" % lat, col)])
            self.app.stats.load = 1.0
            if k in (10, 20, 30):
                for _ in range(4):
                    gl.add_arc(random.choice(list(CITIES)), tc, "in")
            yield 0.12
        self.write([("", "out")])
        m.trace = min(99, m.trace + random.uniform(10, 25))
        r = random.choices(["down", "cdn", "blacklist"], [65, 20, 15])[0]
        if r == "down":
            self.write([("[+] ", "ok"), ("OBJETIVO CAÍDO  (HTTP 503 / sin respuesta)", "err")])
            self.app.banner("TARGET DOWN", tgt, "bad", 3.0)
        elif r == "cdn":
            self.warn("el CDN del objetivo absorbe el ataque: mitigado")
            self.write([("    cambiando a vector %s..." % random.choice(["HTTP/2 rapid reset", "cache-bypass", "login-flood"]), "dim")])
            yield 1.0
            self.good("segundo vector eficaz: el servicio degradado (latencia 6200 ms)")
        else:
            self.warn("el objetivo bloqueó %d IPs de la botnet" % random.randint(800, 3000))
            yield 0.6
            self.good("botnet rotada con nuevas IPs: objetivo inaccesible")
        self.app.log("CRIT", "DDoS %s on %s (simulated)" % (method, tgt))

    # ───────── SQLI / XSS / DIRB [SIM] ─────────
    def cmd_sqli(self, a):
        url = a[0][:70] if a else "http://%s/products.php?id=1" % random.choice(TARGETS)
        self.warn("[SIM] simulación con datos inventados.")
        self.info("probando parámetro 'id' en %s" % url)
        for t, d in (("boolean-based blind", 0.4), ("error-based", 0.3), ("time-based blind (SLEEP)", 0.8), ("UNION query (4 columnas)", 0.5)):
            yield d
            self.write([("    técnica ", "dim"), ("%-26s" % t, "out"), (random.choice(["inyectable", "inyectable", "no inyectable"]), "ok")])
        dbms, dbs = random.choice([("MySQL >= 5.7", ["information_schema", "shop_prod", "mysql"]),
                                   ("PostgreSQL 14", ["postgres", "app", "public"]),
                                   ("MariaDB 10.6", ["information_schema", "crm", "wp_site"]),
                                   ("Microsoft SQL Server 2019", ["master", "erp_main", "tempdb"])])
        self.good("DBMS: %s" % dbms)
        yield 0.3
        self.write([("bases de datos:", "head")])
        for d in dbs:
            self.write([("  [*] " + d, "info")])
            yield 0.1
        self.write([("", "out")])
        users = random.sample(FAKE_USERS, 6)
        words = random.sample(DICT_WORDS, 3)
        self.write([("tabla 'users' (%d filas):" % random.randint(300, 9000), "head")])
        self.write([("  %-4s %-12s %-34s %s" % ("id", "user", "password_md5", "role"), "dim")])
        hint = None
        for i, u in enumerate(users):
            if i < 3:
                h = md5(words[i])
                hint = hint or h
            else:
                h = md5(rpass(10))
            self.write([("  %-4d %-12s " % (i + 1, u), "out"), (h + " ", "warn"), (random.choice(ROLES), "dim")])
            yield 0.12
        if hint:
            self.write([("pista: prueba  crack " + hint, "dim")])
        self.good("volcado guardado (simulado)")

    def cmd_xss(self, a):
        url = a[0][:70] if a else "http://%s/search?q=" % random.choice(TARGETS)
        self.warn("[SIM] simulación.")
        self.info("probando %s" % url)
        for p in ("<script>alert(1)</script>", "\"><img src=x onerror=alert(1)>", "<svg/onload=alert(1)>", "javascript:alert(1)//"):
            yield 0.35
            ok = random.random() < 0.5
            self.write([("    %-34s" % p, "dim"), ("REFLEJADO" if ok else "filtrado", "ok" if ok else "warn")])
        yield 0.4
        self.good("XSS %s confirmado en parámetro 'q'" % random.choice(["reflejado", "almacenado", "basado en DOM"]))
        yield from self.spin("capturando cookies de sesión", 1.2)
        self.write([("    session=", "dim"), (rhex(32), "warn"), ("  (simulada)", "dim")])

    def cmd_dirb(self, a):
        base = a[0][:60] if a else "http://%s" % random.choice(TARGETS)
        self.warn("[SIM] simulación.")
        self.info("fuerza bruta de rutas en %s" % base)
        paths = ["admin", "login", "backup.zip", ".git/HEAD", "phpmyadmin", "uploads", "api/v1", "config.php.bak", "server-status",
                 "wp-login.php", "robots.txt", "old", "dev", "test", "private", ".env", "db_dump.sql", "console"]
        random.shuffle(paths)
        for p in paths[:random.randint(9, 14)]:
            st = random.choices([200, 301, 403, 401, 404], [3, 2, 3, 1, 4])[0]
            hot = p in ("backup.zip", ".git/HEAD", ".env", "db_dump.sql", "config.php.bak", "phpmyadmin", "admin") and st in (200, 301)
            col = "ok" if st in (200, 301) else ("warn" if st in (401, 403) else "dim")
            self.write([("  /%-18s " % p, "out"), ("[%d] " % st, col), ("[%5d B] " % random.randint(120, 90000) if st != 404 else "", "dim"),
                        ("<-- interesante" if hot else "", "err")])
            yield random.uniform(0.06, 0.22)
        self.good("fin del diccionario")

    # ───────── BRUTE [SIM] ─────────
    def cmd_brute(self, a):
        svc = a[0].lower() if a else random.choice(["ssh", "ftp", "rdp", "telnet", "smb"])
        if svc not in ("ssh", "ftp", "rdp", "telnet", "smb"):
            self.bad("uso: brute <ssh|ftp|rdp|telnet|smb> [objetivo]")
            return
        tgt = self._tgt(a, 1)
        user = random.choice(FAKE_USERS[:6])
        total = random.randint(40, 90)
        hit = random.randint(15, total - 5) if random.random() < 0.8 else None
        self.warn("[SIM] simulación: no hay ninguna conexión real.")
        self.info("brute-force %s://%s  usuario '%s'  (%s combinaciones)" % (svc, tgt, user, format(random.randint(10 ** 6, 10 ** 8), ",")))
        for i in range(1, total + 1):
            if hit == i:
                pw = random.choice(DICT_WORDS)
                self.write([("", "out")])
                self.write([("[%d][%s] " % ({"ssh": 22, "ftp": 21, "rdp": 3389, "telnet": 23, "smb": 445}[svc], svc), "ok"),
                            ("host: %s  login: %s  password: " % (tgt, user), "out"), (pw, "head")])
                self.good("1 credencial válida encontrada")
                self.app.log("OK", "Credentials found on %s (%s)" % (tgt, svc))
                return
            pw = random.choice(DICT_WORDS) if random.random() < 0.5 else rpass(random.randint(6, 10))
            self.replace_line([("[ATTEMPT] ", "dim"), ("%s - login \"%s\" - pass \"%s\"" % (tgt[:18], user, pw), "out"),
                               (" - %d of %d" % (i, total), "dim")])
            self.app.stats.load = min(1, self.app.stats.load + 0.02)
            yield random.uniform(0.03, 0.09)
        self.write([("", "out")])
        self.bad("diccionario agotado: sin credenciales (el objetivo bloquea tras N intentos)")

    # ───────── EXPLOIT / SESIONES [SIM] ─────────
    def cmd_exploit(self, a):
        if a and a[0].lower() == "list":
            for n, (pl, svc, port, desc) in EXPLOITS.items():
                self.write([("  %-16s" % n, "info"), ("%-8s %-6s %-5d " % (pl, svc, port), "dim"), (desc, "out")])
                yield 0.04
            return
        name = (a[0].lower() if a else random.choice(list(EXPLOITS)))
        if name not in EXPLOITS:
            self.bad("módulo desconocido. Prueba 'exploit list'.")
            return
        pl, svc, port, desc = EXPLOITS[name]
        rh = a[1][:40] if len(a) > 1 else rip()
        self.warn("[SIM] módulos ficticios; nada se ejecuta de verdad.")
        self.write([("NEXUS Framework 7.3  [ %d exploits | %d payloads | %d encoders ]" % (len(EXPLOITS) * 311, 541, 48), "head")])
        yield 0.3
        path = "exploit/%s/%s/%s" % (pl, svc, name)
        pr = "nexus exploit(%s)" % name
        for cmd in ("use " + path, "set RHOSTS " + rh, "set RPORT %d" % port, "set PAYLOAD nexus/x64/ghostshell/reverse_tcp",
                    "set LHOST 10.%d.%d.%d" % (random.randint(0, 9), random.randint(0, 255), random.randint(2, 250))):
            self.write([("%s > " % ("nexus" if cmd.startswith("use") else pr), "prompt"), (cmd, "input")])
            yield 0.35
        self.write([("%s > " % pr, "prompt"), ("run", "input")])
        yield 0.4
        self.info("Started reverse TCP handler on 0.0.0.0:4444")
        yield 0.5
        self.info("Running automatic check: %s" % desc)
        yield from self.spin("comprobando versión", 1.0)
        outcome = random.choices(["ok", "novuln", "nosession"], [78, 10, 12])[0]
        if outcome == "novuln":
            self.bad("Exploit aborted: the target is not vulnerable")
            return
        self.good("The target appears to be vulnerable")
        yield from self.progress("enviando stage", 18, 0.04)
        if outcome == "nosession":
            self.warn("Exploit completed, but no session was created")
            self.write([("    prueba otra vez: la condición de carrera es probabilística", "dim")])
            return
        self.session = dict(id=random.randint(1, 4), ip=rh, user=random.choice(["root", "SYSTEM", "www-data", "svc_app"]),
                            os=pl, host=rh)
        self.good("Command shell session %d opened (10.0.0.5:4444 -> %s:%d)" % (self.session["id"], rh, random.randint(40000, 60000)))
        self.write([("    usa  sessions | shell | loot", "dim")])
        self.app.topo.infect()
        self.app.mission.trace += random.uniform(3, 9)
        self.app.banner("SESSION OPENED", rh, "ok", 2.2)

    def cmd_msf(self, a):
        return self.cmd_exploit(a)

    def cmd_sessions(self, a):
        s = self.session
        if not s:
            self.warn("no hay sesiones activas (prueba 'exploit' o 'hack')")
            return
        self.write([("Id  Tipo            Usuario     Objetivo", "head")])
        self.write([("%-3d ghostshell      %-11s %s" % (s["id"], s["user"], s["host"]), "ok")])

    def cmd_shell(self, a):
        s = self.session
        if not s:
            self.warn("no hay sesión. Consigue una con 'exploit' o 'hack'.")
            return
        host = "srv-%s" % rhex(3)
        script = [
            ("whoami", s["user"]),
            ("hostname", host),
            ("uname -a", "Linux %s 5.15.0-%d-generic #%d SMP x86_64" % (host, random.randint(70, 120), random.randint(70, 140))),
            ("id", "uid=0(root) gid=0(root) groups=0(root)" if s["user"] in ("root", "SYSTEM") else "uid=33(www-data) gid=33(www-data)"),
            ("ls /home", " ".join(random.sample(FAKE_USERS[:10], 4))),
            ("cat /etc/shadow | head -n 2", "root:$6$%s:19800:0:99999:7:::\n%s:$6$%s:19800:0:99999:7:::" % (rhex(8), random.choice(FAKE_USERS[:5]), rhex(8))),
            ("ss -tlnp | head -n 3", "LISTEN 0 128 0.0.0.0:22  users:((\"sshd\",pid=%d))\nLISTEN 0 511 0.0.0.0:80  users:((\"nginx\",pid=%d))" % (random.randint(300, 999), random.randint(1000, 4000))),
        ]
        self.write([("(sesión %d en %s) — datos inventados" % (s["id"], s["host"]), "dim")])
        for cmd, out in script:
            self.write([("%s# " % host, "prompt")], nl=False)
            yield from self.typeline(cmd, "input", 1, 0.03)
            for ln in out.split("\n"):
                self.out(ln)
            yield 0.25
        self.write([("sesión mantenida en segundo plano", "dim")])

    def cmd_loot(self, a):
        if not self.loot:
            self.warn("aún no hay botín: completa un 'hack'")
            return
        self.write([("BOTÍN", "head")])
        for f in self.loot:
            self.write([("  %-22s" % f, "info"), ("%8.1f MB  " % random.uniform(0.2, 600), "out"), ("cifrado AES-256", "dim")])
            yield 0.06

    # ───────── BOTNET / ROOTKIT / WIPE [SIM] ─────────
    def cmd_botnet(self, a):
        self.warn("[SIM] zombis inventados.")
        self.write([("ID     IP               PAÍS            SO          ESTADO     RTT", "head")])
        cities = list(CITIES.values())
        online = 0
        for i in range(10):
            st = random.choices(["ONLINE", "IDLE", "OFFLINE"], [6, 3, 1])[0]
            online += st != "OFFLINE"
            self.write([("%-6s %-16s %-15s %-11s " % ("Z%04d" % random.randint(1, 9999), rip(), random.choice(cities)[2][:14],
                                                     random.choice(["Windows 10", "Linux", "Android", "IoT cam", "Router"])), "out"),
                        ("%-10s " % st, "ok" if st == "ONLINE" else "warn" if st == "IDLE" else "err"),
                        ("%dms" % random.randint(20, 400), "dim")])
            yield 0.07
        self.good("%d/10 visibles · botnet total ≈ %s nodos" % (online, format(random.randint(2000, 90000), ",")))

    def cmd_rootkit(self, a):
        self.warn("[SIM] no instala nada en tu PC.")
        for s in ("localizando tabla de syscalls", "hookeando getdents/readdir", "ocultando proceso y puertos", "parcheando auditd",
                  "instalando persistencia (módulo cargable)"):
            yield from self.progress(s, 10, 0.03)
        name = random.choice(["kworker/u9:2", "systemd-udevd2", "rcu_sched_x", "dbus-helperd"])
        SUSPICIOUS.add(name)
        self.app.proc.procs.append(dict(pid=random.randint(100, 32000), name=name, cpu=random.uniform(30, 70), mem=random.uniform(1, 3)))
        self.good("rootkit activo como '%s' (oculto a ps/ss)" % name)
        self.app.log("CRIT", "Rootkit persistence installed (%s)" % name)

    def cmd_wipe(self, a):
        yield from self.progress("sobrescribiendo logs", 16, 0.03)
        self.app.events.clear()
        m = self.app.mission
        m.trace = max(0, m.trace - random.uniform(10, 25))
        self.good("huellas borradas · TRACE %d%%" % m.trace)
        self.app.log("OK", "Logs wiped")

    # ───────── WIFI / MITM / KEYLOG [SIM] ─────────
    def cmd_wifi(self, a):
        self.warn("[SIM] redes inventadas, tu tarjeta wifi no se toca.")
        yield from self.spin("activando modo monitor", 1.0)
        names = random.sample(["Hogar_5G", "Vecino_Wifi", "CAFE_LIBRE", "Oficina-2.4", "IoT_Lab", "TP-Link_8A3F", "Galaxy_S21", "MiFibra-B7C2", "Invitados", "Casa_Abuela"], 6)
        encs = ["WPA2", "WPA2", "WPA3", "WEP", "OPN", "WPA2"]
        random.shuffle(encs)
        self.write([("BSSID               PWR  CH  ENC   ESSID", "head")])
        aps = []
        for n_, e in zip(names, encs):
            mac = ":".join(rhex(2).upper() for _ in range(6))
            pwr = -random.randint(30, 90)
            aps.append((mac, pwr, n_, e))
            self.write([("%-19s %4d  %2d  %-5s " % (mac, pwr, random.choice([1, 6, 11, 36, 44]), e), "out"), (n_, "info")])
            yield 0.15
        order = {"OPN": 0, "WEP": 1, "WPA2": 2, "WPA3": 3}
        tgt = min(aps, key=lambda x: (order[x[3]], -x[1]))
        self.info("objetivo: %s (%s, %s)" % (tgt[2], tgt[0], tgt[3]))
        if tgt[3] == "OPN":
            self.good("red abierta: sin cifrado, tráfico visible")
            return
        for i in range(6):
            self.replace_line([("deautenticando clientes ", "dim"), ("→ %d paquetes" % ((i + 1) * 32), "warn")])
            yield 0.25
        self.write([("", "out")])
        self.good("WPA handshake capturado: %s" % tgt[0])
        if tgt[3] == "WPA3":
            self.bad("WPA3 resiste el ataque de diccionario (SAE). Objetivo seguro.")
            return
        for k in range(0, 101, 5):
            self.replace_line([("crackeando clave  ", "out"), ("%6d keys/s  " % random.randint(30000, 90000), "dim"), ("%3d%%" % k, "info")])
            yield 0.07
        self.write([("", "out")])
        if random.random() < 0.75:
            self.good("CLAVE ENCONTRADA: %s" % random.choice(["12345678", "internet2024", "casa" + str(random.randint(1000, 9999)), "contrasena", "wifi" + str(random.randint(100, 999))]))
        else:
            self.bad("clave no encontrada en el diccionario")

    def cmd_mitm(self, a):
        tgt = self._tgt(a)
        gw = "192.168.%d.1" % random.randint(0, 9)
        vic = "192.168.%d.%d" % (random.randint(0, 9), random.randint(20, 200))
        self.warn("[SIM] no se envía ARP real.")
        self.info("envenenando ARP: %s <-> %s" % (vic, gw))
        yield from self.progress("ARP spoofing", 14, 0.04)
        self.good("hombre en el medio activo")
        evs = [("DNS", "consulta %s -> %s" % (random.choice(["mail.google.com", "bank.example", "social.example", "cdn.example.net"]), rip())),
               ("HTTP", "GET /login.php  (cabecera Cookie: PHPSESSID=%s)" % rhex(16)),
               ("HTTP", "POST /auth  user=%s&pass=%s" % (random.choice(FAKE_USERS[:6]), random.choice(DICT_WORDS))),
               ("TLS", "ClientHello SNI=%s (cifrado: no legible)" % random.choice(TARGETS)),
               ("SMB", "NTLMv2 hash capturado de %s" % random.choice(FAKE_USERS[:6])),
               ("DHCP", "lease %s -> %s" % (vic, ":".join(rhex(2) for _ in range(6))))]
        for _ in range(12):
            p, t = random.choice(evs)
            self.write([("  [%s] " % p, "info"), (t, "err" if ("pass=" in t or "NTLM" in t) else "out")])
            yield random.uniform(0.15, 0.4)
        self.good("sniffing detenido · restaurando tablas ARP")

    def cmd_keylog(self, a):
        self.warn("[SIM] texto inventado, nada se captura de tu teclado.")
        self.info("keylogger remoto activo en %s" % rip())
        yield 0.5
        lines = ["hola, te mando el informe mañana", "<Tab>usuario.admin<Tab>", "Contrasena123!<Enter>", "google: como borrar mis huellas",
                 "<Ctrl+C>", "reunion a las 10 no se lo digas a nadie", "ssh root@10.0.0.%d<Enter>" % random.randint(2, 99), "<Backspace><Backspace>ok"]
        for ln in random.sample(lines, 6):
            self.write([("  [%s] " % datetime.datetime.now().strftime("%H:%M:%S"), "dim")], nl=False)
            yield from self.typeline(ln, "warn", 1, 0.04)
            yield 0.3
        self.good("buffer volcado (simulado)")

    # ───────── SHODAN / WHOIS [SIM] ─────────
    def cmd_shodan(self, a):
        q = " ".join(a)[:40] if a else random.choice(["apache", "webcam", "mongodb", "port:3389", "default password"])
        self.warn("[SIM] resultados inventados.")
        self.info("buscando '%s'" % q)
        yield from self.spin("consultando índice global", 1.0)
        banners = ["Apache httpd 2.4.49", "Hikvision DS-2CD camera", "MongoDB 4.0 sin autenticación", "Microsoft RDP", "nginx 1.18 (admin panel)",
                   "Mosquitto MQTT sin auth", "Synology DiskStation", "Redis sin contraseña", "ONVIF camera", "OpenSSH 7.4"]
        self.write([("IP                PUERTO  PAÍS            BANNER", "head")])
        for _ in range(random.randint(7, 11)):
            self.write([("%-17s %-7d %-15s " % (rip(), random.choice([80, 443, 8080, 22, 3389, 27017, 1883, 6379, 554]), random.choice(list(CITIES.values()))[2][:14]), "out"),
                        (random.choice(banners), "info")])
            yield 0.1
        self.good("%s resultados totales" % format(random.randint(300, 900000), ","))

    def cmd_whois(self, a):
        d = a[0][:40] if a else random.choice(TARGETS)
        self.warn("[SIM] datos de registro inventados.")
        yield 0.4
        reg = random.choice(["NameVault Inc.", "Orbital Registrar", "GlobalNames LLC", "Cipher Domains"])
        rows = [("Domain", d), ("Registrar", reg), ("Created", "%d-%02d-%02d" % (random.randint(2003, 2022), random.randint(1, 12), random.randint(1, 28))),
                ("Expires", "%d-%02d-%02d" % (random.randint(2027, 2031), random.randint(1, 12), random.randint(1, 28))),
                ("Name server", "ns1.%s" % d), ("Name server", "ns2.%s" % d), ("Registrant", "REDACTED FOR PRIVACY"),
                ("DNSSEC", random.choice(["unsigned", "signedDelegation"])), ("Status", "clientTransferProhibited")]
        for k, v in rows:
            self.write([("  %-12s " % k, "dim"), (v, "out")])
            yield 0.07

    # ───────── SATÉLITE / CCTV / DRON [SIM] ─────────
    def cmd_satellite(self, a):
        name = a[0].upper()[:12] if a else random.choice(["SAT-07", "SAT-12", "SAT-31", "ORB-44", "GEO-09"])
        self.warn("[SIM] satélite ficticio.")
        self.info("objetivo orbital %s" % name)
        yield from self.progress("calculando ventana de paso", 14, 0.04)
        yield from self.progress("apuntando antena 14.2 GHz", 14, 0.04)
        yield from self.progress("enviando comando de override", 20, 0.04)
        for k, v in (("lat", "%+.2f°" % random.uniform(-60, 60)), ("lon", "%+.2f°" % random.uniform(-180, 180)),
                     ("alt", "%d km" % random.choice([550, 780, 1200, 20200, 35786])), ("vel", "%.2f km/s" % random.uniform(3.0, 7.7)),
                     ("batería", "%d%%" % random.randint(55, 100))):
            self.write([("    %-8s" % k, "dim"), (v, "out")])
            yield 0.1
        self.good("%s bajo control" % name)
        self.app.globe.add_arc("HAV", random.choice(list(CITIES)), "out")

    def cmd_cctv(self, a):
        city = a[0].title()[:14] if a else random.choice([c[2] for c in CITIES.values()])
        self.warn("[SIM] cámaras inventadas.")
        self.info("buscando cámaras expuestas en %s" % city)
        yield from self.spin("barriendo rango", 1.0)
        spots = ["Entrada principal", "Parking P2", "Pasillo B", "Almacén", "Azotea", "Recepción", "Sala de servidores", "Cajero"]
        self.write([("ID      IP               UBICACIÓN           ESTADO", "head")])
        for s in random.sample(spots, 6):
            st = random.choice(["EN VIVO", "EN VIVO", "BUCLE GRABADO", "SIN SEÑAL"])
            self.write([("CAM-%02d  %-16s %-19s " % (random.randint(1, 40), rip(), s), "out"), (st, "ok" if st == "EN VIVO" else "warn" if st == "BUCLE GRABADO" else "err")])
            yield 0.12
        self.good("feeds reproducidos en bucle (simulado)")

    def cmd_drone(self, a):
        self.warn("[SIM] dron inventado.")
        self.info("escaneando enlaces de control 2.4/5.8 GHz")
        yield from self.spin("buscando dron", 1.0)
        self.good("DRN-%s detectado (%s)" % (rhex(3).upper(), random.choice(["Quadcopter", "Ala fija", "Hexacóptero"])))
        yield from self.progress("desautenticando mando original", 16, 0.04)
        yield from self.progress("tomando el enlace", 16, 0.04)
        for k, v in (("batería", "%d%%" % random.randint(30, 95)), ("altitud", "%d m" % random.randint(10, 120)),
                     ("GPS", "%.4f, %.4f" % (random.uniform(-60, 60), random.uniform(-180, 180))), ("RTH", "desactivado")):
            self.write([("    %-9s" % k, "dim"), (v, "out")])
            yield 0.1
        self.good("control total del dron")

    # ───────── EXTRAS DIVERTIDOS ─────────
    def cmd_code(self, a):
        self.info("compilando exploit en tiempo real...")
        for _ in range(random.randint(16, 24)):
            ln = random.choice(CODE_LINES)
            yield from self.typeline(ln, "ok" if random.random() < 0.7 else "info", 4, 0.006)
            yield random.uniform(0.02, 0.1)
        yield from self.progress("make -j16", 14, 0.03)
        self.good("build OK  ·  exploit.bin (%d bytes)" % random.randint(4000, 90000))

    def cmd_fortune(self, a):
        self.out(random.choice(FORTUNES), "warn")

    def cmd_selfdestruct(self, a):
        self.warn("PROTOCOLO DE AUTODESTRUCCIÓN ARMADO")
        for i in range(10, 0, -1):
            self.replace_line([("  autodestrucción en ", "dim"), ("%02d" % i, "err"), ("  (Ctrl+C aborta)", "dim")])
            yield 1.0
        self.write([("", "out")])
        self.app.banner("ABORTED", "era broma: nada fue destruido", "warn", 3.0)
        self.good("secuencia cancelada por el operador (tú)")

    # ───────── CRIPTO / UTILIDADES [REAL] ─────────
    def cmd_passgen(self, a):
        try:
            n = max(8, min(64, int(a[0]))) if a else 20
        except ValueError:
            n = 20
        import secrets
        alpha = string.ascii_letters + string.digits + "!@#$%&*?-_"
        pw = "".join(secrets.choice(alpha) for _ in range(n))
        self.write([("contraseña: ", "dim"), (pw, "head")])
        self.write([("entropía ≈ %.0f bits" % (n * math.log2(len(alpha))), "dim")])

    def cmd_entropy(self, a):
        if not a:
            self.bad("uso: entropy <contraseña>")
            return
        s = " ".join(a)
        pool = 0
        for ok, size in ((any(c.islower() for c in s), 26), (any(c.isupper() for c in s), 26), (any(c.isdigit() for c in s), 10),
                         (any(not c.isalnum() for c in s), 33)):
            pool += size if ok else 0
        bits = len(s) * math.log2(max(2, pool))
        t = (2 ** bits) / 1e10 / 2
        common = s.lower() in [w.lower() for w in DICT_WORDS]
        self.write([("longitud ", "dim"), ("%d" % len(s), "out"), ("   alfabeto ", "dim"), ("%d" % pool, "out"), ("   entropía ", "dim"), ("%.1f bits" % bits, "info")])
        if common:
            self.write([("¡está en el diccionario! se rompe al instante", "err")])
        else:
            col = "err" if bits < 40 else ("warn" if bits < 64 else "ok")
            self.write([("tiempo de crackeo (10 mil millones de intentos/s): ", "dim"), (self._human(t), col)])

    def cmd_b64(self, a):
        if not a:
            self.bad("uso: b64 <texto>")
            return
        self.out(base64.b64encode(" ".join(a).encode()).decode(), "ok")

    def cmd_unb64(self, a):
        try:
            self.out(base64.b64decode("".join(a).encode(), validate=True).decode("utf-8", "replace"), "ok")
        except Exception:
            self.bad("base64 no válido")

    def cmd_hex(self, a):
        if not a:
            self.bad("uso: hex <texto>")
            return
        self.out(" ".join("%02x" % b for b in " ".join(a).encode()), "ok")

    def cmd_rot13(self, a):
        import codecs
        self.out(codecs.encode(" ".join(a), "rot_13"), "ok")

    def cmd_morse(self, a):
        s = " ".join(a).upper()
        self.out(" ".join(MORSE.get(c, "?") for c in s), "ok")

    def cmd_caesar(self, a):
        if len(a) < 2:
            self.bad("uso: caesar <n|brute> <texto>")
            return

        def sh(t, n):
            return "".join(chr((ord(c) - 65 + n) % 26 + 65) if c.isupper() else chr((ord(c) - 97 + n) % 26 + 97) if c.islower() else c for c in t)
        txt = " ".join(a[1:])
        if a[0].lower() == "brute":
            for n in range(1, 26):
                self.write([("%2d  " % n, "dim"), (sh(txt, n), "out")])
        else:
            try:
                self.out(sh(txt, int(a[0])), "ok")
            except ValueError:
                self.bad("el desplazamiento debe ser un número")

    # ───────── RED REAL [REAL] ─────────
    def cmd_myip(self, a):
        n = self.app.net
        self.info("consultando tu salida a internet...")
        box = self.bg(lambda b: n._fetch_pub())
        yield from self.wait(box, "ipinfo.io")
        p = n.pub
        if not p:
            self._net_fail()
            return
        for k, v in (("IP pública", p.get("ip")), ("ISP / AS", p.get("org")), ("Ciudad", ", ".join(x for x in (p.get("city"), p.get("region"), p.get("country")) if x)),
                     ("Zona horaria", p.get("tz")), ("IP local", n.local)):
            if v:
                self.write([("  %-13s" % k, "dim"), (str(v), "ok")])

    def cmd_geoip(self, a):
        if not a:
            self.bad("uso: geoip <ip>")
            return
        ip = a[0]
        if not all(c in "0123456789abcdefABCDEF.:" for c in ip) or len(ip) > 45:
            self.bad("eso no parece una IP")
            return
        box = self.bg(lambda b: http_json("https://ipinfo.io/%s/json" % ip, 8))
        yield from self.wait(box, "geolocalizando")
        if box["err"] or not box["res"]:
            self._net_fail(box["err"])
            return
        d = box["res"]
        if d.get("bogon"):
            self.warn("IP reservada/privada: no tiene ubicación pública")
            return
        for k, f in (("IP", "ip"), ("Host", "hostname"), ("Ciudad", "city"), ("Región", "region"), ("País", "country"), ("Coordenadas", "loc"), ("Organización", "org"), ("Zona horaria", "timezone")):
            if d.get(f):
                self.write([("  %-13s" % k, "dim"), (str(d[f]), "ok")])
        try:
            la, lo = [float(x) for x in d["loc"].split(",")]
            CITIES["TGT"] = (la, lo, d.get("city") or "target")
            self.app.globe.cv["TGT"] = vec(la, lo)
            self.app.globe.add_arc("HAV", "TGT", "trace")
        except Exception:
            pass

    def cmd_dns(self, a):
        if not a:
            self.bad("uso: dns <host>")
            return
        h = a[0][:100]

        def job(b):
            t0 = time.perf_counter()
            infos = socket.getaddrinfo(h, None)
            ms = (time.perf_counter() - t0) * 1000
            ips = []
            for i in infos:
                if i[4][0] not in ips:
                    ips.append(i[4][0])
            rev = {}
            for ip in ips[:4]:
                try:
                    rev[ip] = socket.gethostbyaddr(ip)[0]
                except Exception:
                    rev[ip] = None
            return ms, ips, rev
        box = self.bg(job)
        yield from self.wait(box, "resolviendo %s" % h)
        if box["err"]:
            self.bad("no se pudo resolver %s (%s)" % (h, type(box["err"]).__name__))
            return
        ms, ips, rev = box["res"]
        self.good("%d direcciones en %.0f ms" % (len(ips), ms))
        for ip in ips[:8]:
            self.write([("  %-40s" % ip, "out"), (rev.get(ip) or "", "dim")])

    def cmd_ping(self, a):
        if not a:
            self.bad("uso: ping <host> [n]")
            return
        h = a[0][:100]
        try:
            n = max(1, min(10, int(a[1]))) if len(a) > 1 else 4
        except ValueError:
            n = 4
        self.info("ping TCP a %s (puerto 443, y 80 si falla)" % h)
        res = []
        for i in range(n):
            def one(b):
                v = tcp_ms(h, 443, 3.0)
                return (v, 443) if v is not None else (tcp_ms(h, 80, 3.0), 80)
            box = self.bg(one)
            while not box["done"]:
                yield 0.05
            v, port = box["res"] if box["res"] else (None, 0)
            res.append(v)
            if v is None:
                self.write([("  seq=%d  sin respuesta" % (i + 1), "err")])
            else:
                self.write([("  seq=%d  tcp/%d  tiempo=" % (i + 1, port), "dim"), ("%.1f ms" % v, "ok" if v < 150 else "warn")])
            yield 0.3
        ok = [x for x in res if x is not None]
        if ok:
            self.good("%d/%d recibidos · min/media/max = %.1f / %.1f / %.1f ms" % (len(ok), n, min(ok), sum(ok) / len(ok), max(ok)))
        else:
            self.bad("0/%d: host inaccesible o puerto filtrado" % n)

    def cmd_headers(self, a):
        if not a:
            self.bad("uso: headers <url>")
            return
        u = a[0][:200]
        if not u.lower().startswith(("http://", "https://")):
            u = "https://" + u

        def job(b):
            with http_open(u, 8, "HEAD") as r:
                return r.status, r.getheaders()
        box = self.bg(job)
        yield from self.wait(box, "pidiendo cabeceras")
        if box["err"]:
            e = box["err"]
            code = getattr(e, "code", None)
            if code:
                self.warn("el servidor respondió HTTP %s (probablemente rechaza HEAD)" % code)
            else:
                self._net_fail(e)
            return
        st, hs = box["res"]
        self.good("HTTP %s" % st)
        names = [k.lower() for k, _ in hs]
        for k, v in hs:
            self.write([("  %-26s" % k[:26], "info"), (v[:60], "out")])
        miss = [h for h in ("strict-transport-security", "content-security-policy", "x-frame-options", "x-content-type-options") if h not in names]
        if miss:
            self.write([("faltan cabeceras de seguridad: " + ", ".join(miss), "warn")])
        else:
            self.write([("buenas cabeceras de seguridad", "ok")])

    def cmd_ssl(self, a):
        if not a:
            self.bad("uso: ssl <host>")
            return
        h = a[0].replace("https://", "").split("/")[0][:100]

        def job(b):
            ctx = ssl.create_default_context()
            with socket.create_connection((h, 443), 6) as s:
                with ctx.wrap_socket(s, server_hostname=h) as ss:
                    return ss.getpeercert(), ss.version(), ss.cipher()
        box = self.bg(job)
        yield from self.wait(box, "handshake TLS")
        if box["err"]:
            self.bad("fallo TLS: %s" % type(box["err"]).__name__)
            return
        cert, ver, ciph = box["res"]
        subj = dict(x[0] for x in cert.get("subject", ()))
        iss = dict(x[0] for x in cert.get("issuer", ()))
        try:
            exp = datetime.datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z").replace(tzinfo=datetime.timezone.utc)
            left = (exp - datetime.datetime.now(datetime.timezone.utc)).days
        except Exception:
            left = None
        self.write([("  versión TLS  ", "dim"), (str(ver), "ok")])
        self.write([("  cifrado      ", "dim"), ("%s (%s bits)" % (ciph[0], ciph[2]), "out")])
        self.write([("  sujeto       ", "dim"), (subj.get("commonName", "?"), "out")])
        self.write([("  emisor       ", "dim"), ("%s" % iss.get("organizationName", iss.get("commonName", "?")), "out")])
        self.write([("  caduca       ", "dim"), (cert.get("notAfter", "?"), "out"), ("  (%s días)" % left if left is not None else "", "ok" if (left or 0) > 30 else "warn")])
        sans = [v for k, v in cert.get("subjectAltName", ()) if k == "DNS"]
        if sans:
            self.write([("  SAN          ", "dim"), (", ".join(sans[:5]) + (" …" if len(sans) > 5 else ""), "dim")])

    def cmd_cve(self, a):
        import re
        if not a or not re.match(r"^CVE-\d{4}-\d{4,7}$", a[0], re.I):
            self.bad("uso: cve CVE-2024-3094")
            return
        cid = a[0].upper()
        box = self.bg(lambda b: http_json("https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=" + cid, 12))
        yield from self.wait(box, "consultando NVD")
        if box["err"]:
            e = box["err"]
            if getattr(e, "code", None) in (403, 429):
                self.warn("el NVD limita las consultas: espera 30 s y repite")
            else:
                self._net_fail(e)
            return
        vs = box["res"].get("vulnerabilities", [])
        if not vs:
            self.bad("%s no existe en el NVD" % cid)
            return
        c = vs[0]["cve"]
        desc = next((d["value"] for d in c.get("descriptions", []) if d.get("lang") == "en"), "(sin descripción)")
        score = sev = None
        for key in ("cvssMetricV31", "cvssMetricV40", "cvssMetricV30", "cvssMetricV2"):
            if c.get("metrics", {}).get(key):
                mm = c["metrics"][key][0]
                score = mm["cvssData"].get("baseScore")
                sev = mm.get("baseSeverity") or mm["cvssData"].get("baseSeverity")
                break
        self.write([(cid, "head"), ("   publicada ", "dim"), (c.get("published", "?")[:10], "out")])
        if score is not None:
            self.write([("  CVSS ", "dim"), ("%s %s" % (score, sev or ""), "err" if score >= 7 else "warn")])
        for i in range(0, min(len(desc), 520), 70):
            self.out("  " + desc[i:i + 70], "out")
        self.write([("  referencias: %d" % len(c.get("references", [])), "dim")])

    def cmd_kev(self, a):
        n = self.app.net
        if n.kev_state == "loading":
            self.warn("el feed aún se está descargando, espera unos segundos")
            return
        self.write([("ÚLTIMAS VULNERABILIDADES EXPLOTADAS%s" % ("" if n.kev_state == "live" else "  (DATOS DEMO: sin internet)"), "head")])
        for it in n.kev[:12]:
            self.write([("  %-15s" % it["cve"], "err"), ("%-28s" % ("%s %s" % (it["vendor"], it["product"]))[:28], "out"), ("%s" % it["date"], "dim")])
            yield 0.04
        if n.kev_state == "live":
            self.write([("  fuente: CISA KEV · %d en total" % n.kev_total, "dim")])

    def cmd_net(self, a):
        n = self.app.net
        self.write([("UPLINK  ", "dim"), ("ONLINE" if n.online else ("PROBING" if n.online is None else "OFFLINE"), "ok" if n.online else "err")])
        for h, _ in n.HOSTS:
            d = [x for x in n.lat[h] if x is not None]
            self.write([("  %-16s" % h, "dim"), ("%s" % ("%.0f ms (media %.0f)" % (d[-1], sum(d) / len(d)) if d else "sin datos"), "out")])
        if n.dns_ms is not None:
            self.write([("  DNS              ", "dim"), ("%.0f ms" % n.dns_ms, "out")])
        if n.dl_mbps is not None:
            self.write([("  Descarga         ", "dim"), ("%.1f Mbps" % n.dl_mbps, "ok")])
        yield 0

    def cmd_localnet(self, a):
        n = self.app.net
        h = socket.gethostname()
        self.write([("  host       ", "dim"), (h, "out")])
        self.write([("  IP local   ", "dim"), (n.local, "ok")])
        try:
            ips = socket.gethostbyname_ex(h)[2]
            self.write([("  direcciones", "dim"), (" " + ", ".join(ips), "out")])
        except Exception:
            pass
        parts = n.local.split(".")
        if len(parts) == 4:
            self.write([("  puerta enl.", "dim"), (" %s.%s.%s.1 (probable)" % tuple(parts[:3]), "out")])
        self.write([("  SO         ", "dim"), ("%s %s" % (platform.system(), platform.release()), "out")])
        yield 0

    def cmd_speedtest(self, a):
        self.info("descargando datos de speed.cloudflare.com (máx 8 s)...")

        def job(b):
            t0 = time.time()
            got = 0
            with http_open("https://speed.cloudflare.com/__down?bytes=40000000", 8) as r:
                while time.time() - t0 < 8 and not b["cancel"]:
                    chunk = r.read(65536)
                    if not chunk:
                        break
                    got += len(chunk)
                    b["prog"] = (got, time.time() - t0)
            return b["prog"]
        box = self.bg(job)
        try:
            while not box["done"]:
                if box["prog"]:
                    got, t = box["prog"]
                    mbps = got * 8 / max(0.1, t) / 1e6
                    self.replace_line([("  descargando ", "dim"), ("%6.1f Mbps" % mbps, "ok"), ("  %5.1f MB" % (got / 1e6), "dim")])
                    self.app.stats.net_in.append(min(300, mbps / 8))
                yield 0.2
        finally:
            if not box["done"]:
                box["cancel"] = True
        self.write([("", "out")])
        if box["err"] or not box["res"]:
            self._net_fail(box["err"])
            return
        got, t = box["res"]
        mbps = got * 8 / max(0.1, t) / 1e6
        self.app.net.dl_mbps = mbps
        self.good("descarga: %.1f Mbps (%.1f MB en %.1f s)" % (mbps, got / 1e6, t))

    def cmd_rtrace(self, a):
        if not a:
            self.bad("uso: rtrace <host>")
            return
        h = a[0][:100]
        if h.startswith("-") or not all(c.isalnum() or c in ".-:_" for c in h):
            self.bad("host no válido")
            return
        if os.name == "nt":
            cmd = ["tracert", "-d", "-h", "15", "-w", "1500", h]
        else:
            cmd = ["traceroute", "-n", "-m", "15", "-w", "2", h]
        q = queue.Queue()
        try:
            enc = "cp%d" % ctypes.windll.kernel32.GetOEMCP() if os.name == "nt" else "utf-8"
        except Exception:
            enc = "cp850"
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        except Exception:
            self.bad("no se encontró '%s' en este sistema" % cmd[0])
            return

        def reader():
            for raw in iter(proc.stdout.readline, b""):
                q.put(raw.decode(enc, "replace").rstrip())
            q.put(None)
        threading.Thread(target=reader, daemon=True).start()
        self.info("traceroute REAL con %s (puede tardar ~30 s)" % cmd[0])
        try:
            while True:
                try:
                    ln = q.get_nowait()
                except queue.Empty:
                    yield 0.1
                    continue
                if ln is None:
                    break
                if ln.strip():
                    self.write([(ln, "out" if "*" not in ln else "warn")])
                    if random.random() < 0.5:
                        self.app.globe.add_arc(random.choice(list(CITIES)), random.choice(list(CITIES)), "trace")
        finally:
            if proc.poll() is None:
                proc.kill()
        self.good("fin del traceroute")

    def cmd_lscan(self, a):
        self.info("escaneo REAL de TU equipo (127.0.0.1), puertos 1-1024 + habituales")
        ports = list(range(1, 1025)) + [1433, 1883, 3000, 3306, 5000, 5432, 5900, 6379, 8000, 8080, 8443, 9200, 27017]

        def job(b):
            found = []
            for i, p in enumerate(ports):
                if b["cancel"]:
                    break
                s = socket.socket()
                s.settimeout(0.15)
                try:
                    if s.connect_ex(("127.0.0.1", p)) == 0:
                        found.append(p)
                except Exception:
                    pass
                finally:
                    s.close()
                b["prog"] = (i + 1, len(ports))
            return found
        box = self.bg(job)
        try:
            while not box["done"]:
                if box["prog"]:
                    i, t = box["prog"]
                    self.replace_line([("  escaneando ", "dim"), ("%d/%d" % (i, t), "out")])
                yield 0.15
        finally:
            if not box["done"]:
                box["cancel"] = True
        self.write([("", "out")])
        found = box["res"] or []
        if not found:
            self.good("ningún puerto abierto en localhost: bien cerrado")
            return
        self.write([("PUERTO   SERVICIO", "head")])
        for p in found:
            try:
                svc = socket.getservbyport(p)
            except Exception:
                svc = "desconocido"
            self.write([("%-8d " % p, "ok"), (svc, "info")])
        self.good("%d puertos abiertos en tu máquina" % len(found))

    # ───────── MINIJUEGO breach ─────────
    def cmd_breach(self, a):
        if self.game:
            return
        self.game = dict(kind="breach", i=0, n=5, ok=0, code="", timer=None, old_prompt=self.prompt)
        self.prompt = "breach> "
        self.out("ROMPE EL FIREWALL", "head")
        self.out("Teclea cada código antes de que se agote el tiempo. Ctrl+C abandona.", "dim")
        self._breach_next()

    def _breach_next(self):
        g = self.game
        g["i"] += 1
        g["code"] = "-".join(rhex(2).upper() for _ in range(3 + g["i"] // 3))
        lim = max(3.5, 9.0 - g["i"] * 0.9)
        self.write([("[%d/%d] " % (g["i"], g["n"]), "dim"), (g["code"], "head"), ("   (%.1fs)" % lim, "dim")])
        g["timer"] = self.after(int(lim * 1000), self._breach_timeout, g["i"])

    def _breach_timeout(self, i):
        g = self.game
        if g and g["i"] == i:
            self.bad("tiempo agotado")
            self.app.mission.trace = min(99, self.app.mission.trace + 6)
            self._breach_end_round()

    def game_input(self, line):
        g = self.game
        if g["timer"] is not None:
            self.after_cancel(g["timer"])
            g["timer"] = None
        typed = line.upper().replace("-", "").replace(" ", "")
        if typed == g["code"].replace("-", ""):
            g["ok"] += 1
            self.good("capa rota")
            self.app.mission.trace = max(0, self.app.mission.trace - 3)
        else:
            self.bad("código incorrecto")
            self.app.mission.trace = min(99, self.app.mission.trace + 5)
        self._breach_end_round()

    def _breach_end_round(self):
        g = self.game
        if g["i"] < g["n"]:
            self._breach_next()
            return
        self.prompt = g["old_prompt"]
        self.game = None
        ok, n = g["ok"], g["n"]
        if ok == n:
            self.good("FIREWALL ROTO %d/%d · rastreo reducido" % (ok, n))
            self.app.banner("FIREWALL BREACHED", "%d/%d capas" % (ok, n), "ok", 2.5)
        elif ok >= 3:
            self.warn("acceso parcial %d/%d" % (ok, n))
        else:
            self.bad("expulsado del sistema %d/%d · el rastreo sube" % (ok, n))
            self.app.banner("ACCESS DENIED", "%d/%d" % (ok, n), "bad", 2.5)
        self._render_prompt()

    def abort_game(self):
        g = self.game
        if g and g["timer"] is not None:
            self.after_cancel(g["timer"])
        if g:
            self.prompt = g["old_prompt"]
        self.game = None
        self.warn("minijuego abandonado")
        self._render_prompt()


# ════════════════════════════════════════════════════════════════════
#  v9: MODOS DE TERMINAL (NEXUS · WINDOWS · SSH · NOVA) + COMANDOS NUEVOS
#  Mixin ExtraCmds2: va ANTES de ExtraCmds, así que sobreescribe help/sysinfo/uptime.
# ════════════════════════════════════════════════════════════════════
WIN_HINT = {"dir", "ipconfig", "tasklist", "systeminfo", "type", "copy", "del", "mkdir", "md", "cmd", "powershell", "netsh",
            "taskkill", "where", "ver", "tree", "arp", "nslookup", "tracert", "route", "getmac", "wmic", "sc", "reg",
            "chkdsk", "cls", "move", "ren", "rename", "attrib", "findstr", "more", "notepad", "calc", "mklink", "robocopy"}
DANGER = re.compile(r"(?i)(^|[\s&|;(])(format|diskpart|bcdedit|shutdown|mkfs|rm\s+-r[f]*|del\s+/[sqf]|erase\s+/[sqf]|"
                    r"rd\s+/s|rmdir\s+/s)(\s|$)|reg\s+delete|cipher\s+/w|vssadmin\s+delete|wbadmin\s+delete|"
                    r"net\s+user\s+\S+\s+/(add|delete)|net\s+user\s+\S+\s+\S+\s+/add|netsh\s+advfirewall\s+(reset|set\s+\w+\s+state\s+off)")
OUI = {"00:50:56": "VMware", "00:0c:29": "VMware", "08:00:27": "VirtualBox", "b8:27:eb": "Raspberry Pi", "dc:a6:32": "Raspberry Pi",
       "e4:5f:01": "Raspberry Pi", "00:15:5d": "Microsoft Hyper-V", "52:54:00": "QEMU/KVM"}

CONTRACTS = [
    ("Escanea 3 objetivos distintos", {"scan", "nmap"}, 3, 90), ("Lanza 2 ataques DDoS", {"ddos"}, 2, 100),
    ("Completa una intrusión completa", {"hack"}, 1, 140), ("Rompe un firewall en el minijuego", {"breach"}, 1, 80),
    ("Haz 4 consultas de red reales", {"myip", "ping", "dns", "headers", "ssl", "geoip", "cve", "kev", "speedtest", "rtrace", "lan", "wifiscan"}, 4, 110),
    ("Prueba 3 vectores web (sqli, xss, nikto, dirb)", {"sqli", "xss", "nikto", "dirb"}, 3, 100),
    ("Pivota y escala privilegios", {"pivot", "privesc"}, 2, 120), ("Oculta tu rastro: tor, vpn o ghost", {"tor", "vpn", "ghost"}, 2, 70),
    ("Exfiltra datos de un objetivo", {"exfil"}, 1, 110), ("Conéctate por ssh a un servidor", {"ssh"}, 1, 120),
]
EVENTS = [
    ("WARN", "Escaneo de puertos detectado desde {ip}", 2, "Detecto un escaneo de puertos desde {ip}."),
    ("INFO", "Honeypot {host} activó una alerta silenciosa", 0, None),
    ("WARN", "Intento de fuerza bruta SSH contra tu nodo desde {ip}", 3, "Alguien intenta forzar tu acceso desde {ip}."),
    ("OK", "Nuevo CVE crítico publicado: CVE-2026-{n}", 0, "Acaba de publicarse una vulnerabilidad crítica."),
    ("CRIT", "Firewall contraatacó: sonda de rastreo desde {ip}", 6, "Atención, el objetivo nos está rastreando."),
    ("INFO", "Relé tor {hx} se unió a tu circuito", -3, None),
    ("WARN", "Latencia anómala en el enlace SAT-07", 0, None),
    ("OK", "Zero-day cache actualizada (+1 elemento)", 0, "He añadido un nuevo día cero a la reserva."),
    ("CRIT", "Intrusión detectada en subred 10.{n}.0.0/16", 5, "Hay actividad hostil en la subred interna."),
    ("INFO", "Rotación de claves completada ({hx})", 0, None),
    ("WARN", "Un analista del objetivo abrió una sesión de respuesta a incidentes", 4, "Cuidado, parece que hay un analista mirando."),
    ("OK", "Entropía regenerada: pool 4096 bits", 0, None),
]
HELP_SECTIONS[:0] = [
    ("MODOS DE LA TERMINAL  [dos mundos separados]", [
        ("win | F6", "entra en modo WINDOWS: comandos REALES de cmd (dir, ipconfig...)"), ("win <comando>", "ejecuta UN comando de Windows y vuelve"),
        ("nexus", "(dentro de win/ssh/nova) vuelve al terminal NEXUS"), ("ssh [usuario@]host", "sesión remota SIMULADA con su propio shell"),
        ("nova [texto]", "modo conversación con la IA (sin texto: chat; con texto: una pregunta)")]),
    ("NOVA // VOZ  [tú decides si habla]", [
        ("voz on | off | F7", "activa o desactiva la voz de Nova"), ("voz probar", "Nova dice una frase"),
        ("voz acento cu|es|mx|en", "acento de la voz"), ("voz velocidad -5..5 · voz volumen 0..100", ""),
        ("voz narrar on|off", "que Nova comente lo que haces"), ("voz motor auto|sapi|neural", "elegir motor de voz"),
        ("voz instalar", "instala edge-tts: voz neuronal natural (pip)"), ("voz voces | estado | nombre X | parar", "")]),
    ("PROGRESO Y EXTRAS", [
        ("rank | perfil", "tu rango, experiencia y estadísticas"), ("briefing", "contrato con recompensa de XP"),
        ("matrix | F8", "lluvia de código a pantalla completa"), ("glitch", "fallo visual de película")]),
]
HELP_SECTIONS.extend([
    ("OFENSIVO 2  [SIM: teatro]", [
        ("nikto [url]", "auditoría de servidor web"), ("payload [tipo]", "genera una carga útil (ficticia)"), ("pivot [host]", "salta a la red interna"),
        ("privesc", "escalada de privilegios"), ("tor", "circuito de 3 saltos"), ("zeroday", "usa un día cero de tu reserva"),
        ("neural", "IA generadora de exploits"), ("exfil [obj]", "exfiltración de datos"), ("sniff [iface]", "captura de paquetes"),
        ("fuzz [obj]", "fuzzer que provoca un crash"), ("honeypot [ip]", "¿es una trampa?"), ("stego <texto>", "oculta un mensaje en una imagen"),
        ("bluetooth", "dispositivos BLE cercanos (inventados)"), ("rfid", "clonación de tarjeta"), ("gps [ciudad]", "falsifica tu posición"),
        ("firmware", "analiza firmware de router"), ("radio", "escáner SDR"), ("scada", "planta industrial ficticia")]),
    ("TU EQUIPO  [REAL: solo lectura]", [
        ("hostinfo | sysinfo", "datos reales de tu PC"), ("uptime", "tiempo real encendido"), ("battery", "batería"),
        ("disks", "discos y espacio libre"), ("procs", "procesos que más memoria usan"), ("conns", "conexiones de red activas"),
        ("netcfg", "configuración de red (ipconfig)"), ("lan [sweep]", "dispositivos de tu red local"), ("wifiscan", "redes wifi cercanas reales"),
        ("portcheck <host> <puertos>", "comprueba puertos TCP"), ("subdomains <dominio>", "DNS de subdominios comunes"), ("hashfile <ruta>", "md5 + sha256 de un archivo")]),
])


class ExtraCmds2:
    mode = "nexus"
    _prompt_over = None
    pending = None
    ssh = None
    wcwd = None
    wenv = None

    # ───────── ayuda ─────────
    def cmd_help(self, a):
        key = norm(" ".join(a))
        shown = 0
        for title, items in HELP_SECTIONS:
            rows = [(c, d) for c, d in items if not key or key in norm(c) or key in norm(d) or key in norm(title)]
            if not rows:
                continue
            self.out(title, "head")
            for c, d in rows:
                self.write([("  %-40s" % c, "info"), (d, "dim")])
                shown += 1
                yield 0.01
            self.out("")
        if not shown:
            self.warn("nada coincide con '%s'. Prueba: help win · help voz · help real · help sim" % key)
        else:
            self.out("  Tab autocompleta · ↑/↓ historial · Ctrl+C aborta · F4 hack · F5 juego · F6 Windows · F7 voz · F8 matrix · 'help <palabra>' filtra", "dim")

    # ───────── prompt / modos ─────────
    @property
    def prompt(self):
        if self._prompt_over is not None:
            return self._prompt_over
        if self.mode == "win":
            return "%s> " % self.wcwd
        if self.mode == "chat":
            return "tú ▸ "
        if self.mode == "ssh" and self.ssh:
            return "%s@%s:%s%s " % (self.ssh["user"], self.ssh["host"].split(".")[0][:14], self.ssh["tilde"](), "#" if self.ssh["user"] == "root" else "$")
        return "%s@nexus:~# " % self.user

    @prompt.setter
    def prompt(self, v):
        self._prompt_over = v

    @property
    def ptag(self):
        return {"win": "winp", "chat": "nova", "ssh": "sshp"}.get(self.mode, "prompt")

    @property
    def itag(self):
        return {"win": "winin", "chat": "novain"}.get(self.mode, "input")

    def _init_modes(self):
        self.mode = "nexus"
        self.pending = None
        self.ssh = None
        self.wcwd = os.path.expanduser("~")
        self.wenv = dict(os.environ)

    def _mode_tags(self):
        tg = self.text.tag_configure
        tg("winp", foreground="#ffffff")
        tg("winin", foreground="#e8e8e8")
        tg("winout", foreground="#c0c0c0")
        tg("nova", foreground="#ff8ad8")
        tg("novain", foreground=T.hi)
        tg("novat", foreground=T.hi)
        tg("sshp", foreground=T.warn)
        tg("sshout", foreground=mix(T.fg, T.warn, 0.35))

    def _border(self):
        return T.dim if self.mode == "nexus" else self.mode_color()

    def mode_color(self):
        return {"win": "#c0c0c0", "chat": "#ff8ad8", "ssh": T.warn}.get(self.mode, T.fg)

    def bar_title(self):
        return {"win": "WINDOWS CMD // REAL SHELL", "chat": "NOVA // CONVERSACIÓN", "ssh": "SSH // SESIÓN REMOTA [SIM]"}.get(self.mode, "TERMINAL // ROOT SHELL")

    def bar_sub(self):
        if self.mode == "win":
            return "'nexus' vuelve · F6"
        if self.mode == "chat":
            return "'salir' vuelve · /cmd ejecuta"
        if self.mode == "ssh" and self.ssh:
            return "%s@%s" % (self.ssh["user"], self.ssh["host"])
        return "/bin/ghostsh  pid %d" % os.getpid()

    def set_mode(self, mode, quiet=False):
        self.mode = mode
        self._prompt_over = None
        if mode != "ssh":
            self.ssh = None
        try:
            self.configure(highlightbackground=self._border())
            self._draw_bar()
        except Exception:
            pass
        if not quiet:
            try:
                self.app.nova.narrate("mode_" + mode, prio=2)
            except Exception:
                pass
        self.app.log("INFO", "Modo de terminal: %s" % mode.upper())

    def _trim(self):
        try:
            n = int(self.text.index("end-1c").split(".")[0])
            if n > 3500:
                self._unlock()
                self.text.delete("1.0", "%d.0" % (n - 2800))
                self._lock()
        except Exception:
            pass

    # ───────── despacho de líneas según el modo ─────────
    def _run_gen(self, gen):
        self.busy = True
        self.runner.start(self._safe(gen), self._finish)

    def execute(self, line):
        if self.pending is not None:
            fac, self.pending = self.pending, None
            if norm(line) in ("si", "s", "y", "yes"):
                self._run_gen(fac())
                return
            self.busy = True
            self.warn("cancelado")
            self._finish()
            return
        if self.mode == "nexus":
            return self._exec_nexus(line)
        self.app.stats.load = min(1.0, self.app.stats.load + 0.12)
        fn = {"win": self._win_exec, "chat": self._chat_exec, "ssh": self._ssh_exec}.get(self.mode, self._win_exec)
        self._run_gen(fn(line))

    def _tab(self):
        buf = self.buf
        if self.mode == "chat":
            return
        if self.mode == "win":
            pieces = buf.split(" ")
            last = pieces[-1]
            base, _, part = last.replace("/", "\\").rpartition("\\")
            d = os.path.join(self.wcwd, base) if base else self.wcwd
            try:
                names = [n + ("\\" if os.path.isdir(os.path.join(d, n)) else "") for n in os.listdir(d) if n.lower().startswith(part.lower())]
            except Exception:
                names = []
            if len(pieces) == 1 and not base:
                names += [c for c in ("ipconfig", "tasklist", "systeminfo", "netstat", "nslookup", "tracert", "ping", "dir", "cls", "nexus", "powershell")
                          if c.startswith(part.lower())]
            names = sorted(set(names))
            if names:
                pre = os.path.commonprefix(names) if len(names) > 1 else names[0]
                pieces[-1] = (base + "\\" if base else "") + pre
                self.buf = " ".join(pieces)
        elif self.mode == "ssh":
            cmds = ["ls", "cd", "cat", "pwd", "whoami", "id", "uname", "ps", "ss", "ip", "df", "free", "w", "last", "history", "env", "grep",
                    "find", "wget", "curl", "sudo", "su", "privesc", "download", "exit", "help", "head", "tail", "hostname", "uptime", "date", "echo"]
            pieces = buf.split(" ")
            if len(pieces) == 1:
                opts = [c for c in cmds if c.startswith(buf)]
            else:
                names = self._ssh_names(self.ssh["cwd"])
                opts = [n for n in names if n.startswith(pieces[-1])]
            if opts:
                pre = opts[0] if len(opts) == 1 else os.path.commonprefix(opts)
                pieces[-1] = pre
                self.buf = " ".join(pieces) + (" " if len(opts) == 1 and len(pieces) == 1 else "")
        else:
            opts = [c for c in ALL_CMDS if c.startswith(buf)]
            if len(opts) == 1:
                self.buf = opts[0] + " "
            elif len(opts) > 1:
                self.buf = os.path.commonprefix(opts)
        self._render_prompt()

    def _exec_inline(self, line):
        """Ejecuta un comando NEXUS dentro de otro generador (chat / voz)."""
        parts = line.split()
        if not parts:
            return
        cmd, args = parts[0].lower(), parts[1:]
        fn = getattr(self, "cmd_" + cmd.replace("-", "_"), None)
        if fn is None:
            self.bad("%s: comando no encontrado" % cmd)
            return
        self._note_cmd(cmd, args)
        res = fn(args)
        if inspect.isgenerator(res):
            yield from res

    def _note_cmd(self, cmd, args):
        try:
            self.app.nova.on_command(cmd, args)
            self.app.note_command(cmd)
        except Exception:
            pass

    # ───────── modo WINDOWS (comandos reales) ─────────
    def _win_banner(self):
        self.write([("", "winout")])
        self.write([("Modo WINDOWS: aquí los comandos son REALES y se ejecutan en tu equipo.", "winp")])
        if os.name == "nt":
            self.write([("Microsoft Windows [Versión %s]" % platform.version(), "winout")])
        else:
            self.write([("(no estás en Windows: se usa /bin/sh en su lugar)", "winout")])
        self.write([("'wh' ayuda del modo · 'ps <cmd>' PowerShell · 'nexus' o 'exit' vuelven a NEXUS · Ctrl+C aborta", "winout")])
        self.write([("", "winout")])

    def cmd_win(self, a):
        if a:
            return self._win_exec(" ".join(a), oneshot=True)
        self.set_mode("win")
        self._win_banner()

    def cmd_nexus(self, a):
        if self.mode == "nexus":
            self.info("ya estás en el terminal NEXUS")
        else:
            self.set_mode("nexus")

    def _win_exec(self, line, oneshot=False):
        s = line.strip()
        low = s.lower()
        T_ = "winout"
        if not s:
            return
        if low in ("nexus", "exit", "salir", "quit") and not oneshot:
            self.set_mode("nexus")
            self.out("de vuelta en NEXUS", "dim")
            return
        if low in ("wh", "winhelp", "ayuda-win"):
            for ln in ("Todo lo que escribas se ejecuta de verdad con cmd.exe en tu equipo, en la carpeta mostrada en el prompt.",
                       "  cd <ruta> · X: cambia carpeta/unidad  |  set VAR=valor guarda variables  |  cls limpia",
                       "  ps <comando>  ejecuta PowerShell  (ej: ps Get-Process | select -first 5)",
                       "  Tab autocompleta archivos y carpetas  |  Ctrl+C aborta un comando",
                       "  Los comandos destructivos (format, del /s, rd /s, shutdown...) piden confirmación escribiendo SI.",
                       "  Los comandos de NEXUS no existen aquí; escribe 'nexus' para volver a ellos."):
                self.write([(ln, T_)])
            return
        if low in ("cls", "clear"):
            self.cmd_clear([])
            return
        m = re.match(r"(?is)^(?:cd|chdir)(?:\s+/d)?(?=$|[\s\\/.])\s*(.*)$", s)
        if m:
            path = os.path.expandvars(m.group(1).strip().strip('"'))
            if not path:
                self.write([(self.wcwd, T_)])
                return
            new = os.path.normpath(os.path.join(self.wcwd, path))
            if os.path.isdir(new):
                self.wcwd = new
                self._prompt_over = None
            else:
                self.write([("El sistema no puede encontrar la ruta especificada.", T_)])
            return
        if re.fullmatch(r"[a-zA-Z]:", s):
            if os.path.isdir(s + "\\"):
                self.wcwd = s.upper() + "\\"
            else:
                self.write([("El sistema no puede encontrar la unidad especificada.", T_)])
            return
        m = re.match(r"(?is)^set(?:\s+(.*))?$", s)
        if m:
            arg = (m.group(1) or "").strip()
            if "=" in arg:
                k, v = arg.split("=", 1)
                if v:
                    self.wenv[k.strip()] = v
                else:
                    self.wenv.pop(k.strip(), None)
            else:
                for k in sorted(self.wenv, key=str.lower):
                    if k.lower().startswith(arg.lower()):
                        self.write([("%s=%s" % (k, self.wenv[k]), T_)])
            return
        if DANGER.search(s) and not oneshot:
            self.warn("comando potencialmente DESTRUCTIVO: %s" % s)
            self.write([("  esto se ejecutaría de verdad en tu equipo. Escribe SI para continuar, otra cosa cancela.", "warn")])
            self.pending = lambda s=s: self._win_run(s)
            return
        if DANGER.search(s) and oneshot:
            self.bad("comando destructivo: ejecútalo desde el modo 'win' para confirmarlo")
            return
        yield from self._win_run(s, oneshot)

    def _win_run(self, s, oneshot=False):
        T_ = "winout"
        nt = os.name == "nt"
        low = s.lower()
        try:
            if nt and re.match(r"(?i)^(ps|powershell|pwsh)(\s|$)", s):
                body = re.sub(r"(?i)^(ps|powershell|pwsh)\s*", "", s)
                if not body:
                    self.write([("uso: ps <comando de PowerShell>", T_)])
                    return
                args = ["powershell.exe", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-Command", body]
            elif nt:
                args = 'cmd.exe /d /s /c "%s"' % s
            else:
                args = ["/bin/sh", "-c", s]
            kw = dict(creationflags=NOWIN) if nt else dict(start_new_session=True)
            proc = subprocess.Popen(args, cwd=self.wcwd, env=self.wenv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, **kw)
        except Exception as e:
            self.write([("No se pudo ejecutar: %s" % e, "err")])
            return
        q = queue.Queue()
        enc = oem_encoding()

        def reader():
            try:
                for raw in iter(proc.stdout.readline, b""):
                    q.put(raw.decode(enc, "replace"))
            except Exception:
                pass
            q.put(None)
        threading.Thread(target=reader, daemon=True).start()
        t0, n = time.time(), 0
        try:
            while True:
                try:
                    ln = q.get(timeout=0.04)
                except queue.Empty:
                    if time.time() - t0 > 600:
                        self.write([("(tiempo máximo de 10 min alcanzado, abortado)", "warn")])
                        break
                    yield 0
                    continue
                if ln is None:
                    break
                for sub in strip_ansi(ln).rstrip("\r\n").split("\r"):
                    self.write([(sub.expandtabs(8), T_)])
                n += 1
                if n % 120 == 0:
                    self._trim()
                    yield 0.001
        finally:
            if proc.poll() is None:
                try:
                    if nt:
                        subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                       creationflags=NOWIN, timeout=5)
                    else:
                        import signal
                        os.killpg(proc.pid, signal.SIGKILL)
                except Exception:
                    try:
                        proc.kill()
                    except Exception:
                        pass
        rc = proc.poll()
        if rc not in (0, None) and not oneshot:
            self.write([("(código de salida %s)" % rc, "dim")])
        self.app.add_xp(1, None)

    # ───────── modo NOVA (conversación) ─────────
    def _nova_say(self, text):
        self.app.nova.say(text, 2)
        self.write([("NOVA ▸ ", "nova")], nl=False)
        yield from self.typeline(text, "novat", 2, 0.016)

    def cmd_nova(self, a):
        nova = self.app.nova
        nova.touch()
        if a:
            return self._nova_once(" ".join(a))
        self.set_mode("chat", quiet=True)
        return self._nova_intro()

    def _nova_intro(self):
        self.write([("", "out")])
        yield from self._nova_say("%s, %s. Soy Nova. Escribe lo que quieras: preguntas, cálculos, términos de seguridad, chistes, o pídeme que escanee algo. 'salir' para volver." % (
            self.app.nova.greeting(), self.app.nova.name))
        self.write([("  (prefijo '/' ejecuta un comando NEXUS sin salir del chat, ej: /myip)", "dim")])

    def _nova_once(self, text):
        r = self.app.nova.reply(text)
        yield from self._nova_say(r["text"])
        if r["cmd"]:
            yield 0.3
            yield from self._exec_inline(r["cmd"])

    def _chat_exec(self, line):
        nova = self.app.nova
        nova.touch()
        if line.startswith("/"):
            c = line[1:].strip()
            if c in ("salir", "exit", "nexus", ""):
                self.set_mode("nexus", quiet=True)
                self.out("de vuelta en NEXUS", "dim")
                return
            yield from self._exec_inline(c)
            return
        r = nova.reply(line)
        yield from self._nova_say(r["text"])
        if r["cmd"]:
            yield 0.3
            yield from self._exec_inline(r["cmd"])
        if r["exit"]:
            self.set_mode("nexus", quiet=True)

    # ───────── VOZ ─────────
    def cmd_voz(self, a):
        v, cfg, app = self.app.voice, self.app.cfg, self.app
        sub = a[0].lower() if a else "estado"
        arg = a[1:]
        if sub in ("on", "activar", "activa", "si", "1", "enciende"):
            v.set_enabled(True)
            self.good("voz de Nova ACTIVADA  (motor %s, acento %s)" % (v.engine_label(), cfg.get("accent").upper()))
            if not v.edge_ok():
                self.write([("  consejo: 'voz instalar' añade una voz neuronal mucho más natural (necesita internet).", "dim")])
            v.say("Voz activada. Hola, %s. Soy Nova." % app.nova.name, 2)
        elif sub in ("off", "desactivar", "desactiva", "no", "0", "apaga"):
            v.set_enabled(False)
            self.good("voz desactivada. Nova seguirá respondiendo solo por texto.")
        elif sub in ("probar", "test", "prueba"):
            txt = " ".join(arg) or "Hola %s. Esta es mi voz. Si me oyes bien, ya podemos trabajar." % app.nova.name
            v.say(txt, 2, force=True)
            self.info("hablando (%s)..." % v.engine_label())
            t0 = time.time()
            while (v.busy() or time.time() - t0 < 0.8) and time.time() - t0 < 25 and not v.err:
                yield 0.1
            self.write([("  motor usado: %s   voz: %s" % (v.engine_used, v.voice_name or "-"), "dim")])
            if v.err:
                self.bad("fallo de voz: %s" % v.err)
            elif os.name == "nt" and v.engine_used == "sapi" and v.voices and not any(x[1].lower().startswith("es") for x in v.voices if len(x) > 1):
                self.warn("Windows no tiene ninguna voz en español: suena con acento inglés. Solución: 'voz instalar' (neuronal) o")
                self.write([("  Configuración > Hora e idioma > Voz > Agregar voces (Español).", "dim")])
        elif sub in ("acento", "accent"):
            k = (arg[0].lower() if arg else "")
            if k in Voice.ACCENTS:
                cfg.set("accent", k)
                v._ps_key = None
                self.good("acento: %s  (%s)" % (k.upper(), Voice.ACCENTS[k][0]))
            else:
                self.info("acentos: cu (Cuba) · es (España) · mx (México) · en (inglés)   actual: %s" % cfg.get("accent"))
        elif sub in ("velocidad", "rate"):
            try:
                n = max(-5, min(5, int(arg[0])))
                cfg.set("rate", n)
                self.good("velocidad: %d" % n)
            except Exception:
                self.info("uso: voz velocidad -5..5   (actual %d)" % cfg.get("rate"))
        elif sub in ("volumen", "volume"):
            try:
                n = max(0, min(100, int(arg[0])))
                cfg.set("volume", n)
                v._ps_key = None
                self.good("volumen: %d" % n)
            except Exception:
                self.info("uso: voz volumen 0..100   (actual %d)" % cfg.get("volume"))
        elif sub in ("narrar", "narra", "narration"):
            on = (arg[0].lower() in ("on", "si", "1")) if arg else not cfg.get("narrate")
            cfg.set("narrate", on)
            self.good("narración automática %s" % ("ACTIVADA" if on else "desactivada"))
        elif sub in ("motor", "engine"):
            k = (arg[0].lower() if arg else "")
            if k in ("auto", "sapi", "neural"):
                cfg.set("engine", k)
                self.good("motor: %s" % k)
            else:
                self.info("motores: auto · sapi (voz de Windows) · neural (edge-tts)   actual: %s" % cfg.get("engine"))
        elif sub in ("nombre", "name"):
            if arg:
                cfg.set("name", " ".join(arg)[:20].title())
                self.good("te llamaré %s" % app.nova.name)
            else:
                self.info("te llamo %s. Cambia: voz nombre <tu nombre>" % app.nova.name)
        elif sub in ("parar", "stop", "calla"):
            v.stop()
            self.good("silencio")
        elif sub in ("instalar", "install"):
            yield from self._voz_install()
        elif sub in ("voces", "voices"):
            if os.name == "nt" and not v.voices:
                self.info("consultando las voces instaladas en Windows...")
                box = self.bg(lambda b: v._ps_ensure())
                yield from self.wait(box, "PowerShell/SAPI")
            if v.voices:
                self.write([("VOCES SAPI INSTALADAS", "head")])
                for x in v.voices:
                    if len(x) >= 3:
                        self.write([("  %-34s" % x[0], "info"), ("%-8s" % x[1], "out"), (x[2], "dim")])
            else:
                self.write([("  (sin lista de voces SAPI en este sistema)", "dim")])
            self.write([("voz neuronal edge-tts: %s" % ("instalada" if v.edge_ok() else "no instalada ('voz instalar')"), "dim")])
        else:
            self.write([("NOVA // VOZ", "head")])
            self.write([("  estado        ", "dim"), ("ACTIVADA" if v.enabled else "desactivada", "ok" if v.enabled else "warn")])
            self.write([("  motor         ", "dim"), ("%s (en uso: %s)   edge-tts: %s" % (cfg.get("engine"), v.engine_used, "sí" if v.edge_ok() else "no"), "out")])
            self.write([("  acento        ", "dim"), (cfg.get("accent").upper(), "out")])
            self.write([("  velocidad     ", "dim"), ("%d   volumen %d" % (cfg.get("rate"), cfg.get("volume")), "out")])
            self.write([("  narración     ", "dim"), ("sí" if cfg.get("narrate") else "no", "out")])
            self.write([("  te llamo      ", "dim"), (app.nova.name, "out")])
            if v.err:
                self.write([("  último error  ", "dim"), (v.err[:80], "err")])
            self.write([("  uso: voz on|off · probar · acento · velocidad · volumen · narrar · motor · instalar · voces · nombre", "dim")])

    cmd_voice = cmd_voz

    def _voz_install(self):
        self.info("instalando edge-tts con pip (necesita internet; solo instala este paquete)...")

        def job(b):
            r = subprocess.run([sys.executable, "-m", "pip", "install", "--user", "--disable-pip-version-check", "edge-tts"],
                               capture_output=True, text=True, timeout=240, creationflags=NOWIN)
            return r.returncode, (r.stdout + r.stderr)[-400:]
        box = self.bg(job)
        yield from self.wait(box, "pip install edge-tts")
        if box["err"] or not box["res"] or box["res"][0] != 0:
            self.bad("no se pudo instalar")
            tail = box["res"][1] if box["res"] else str(box["err"])
            for ln in tail.strip().splitlines()[-4:]:
                self.write([("  " + ln[:100], "dim")])
            self.write([("  prueba a mano en cmd:  py -m pip install edge-tts", "dim")])
            return
        importlib.invalidate_caches()
        self.good("edge-tts instalado. Voz neuronal disponible (motor auto la usará si hay internet).")
        self.write([("  ahora: 'voz probar'  ·  acento cubano por defecto, cambia con 'voz acento es|mx'", "dim")])

    # ───────── SSH simulado ─────────
    def cmd_ssh(self, a):
        if not a:
            self.write([("uso: ssh [usuario@]host   (SIMULADO: no se conecta a nada)", "dim")])
            return
        user, _, host = a[-1].rpartition("@")
        user = user or random.choice(["admin", "deploy", "ubuntu", "svc_backup"])
        host = host[:50] or random.choice(TARGETS)
        os_name = random.choice(["Ubuntu 22.04.4 LTS", "Debian GNU/Linux 12", "Rocky Linux 9.3", "Ubuntu 24.04 LTS"])
        ip = rip()
        self.write([("[SIM] sesión SSH inventada: no sale ningún paquete de tu equipo.", "dim")])
        self.write([("OpenSSH_9.6p1, OpenSSL 3.0.13  ·  connecting to %s [%s] port 22" % (host, ip), "dim")])
        yield 0.5
        fp = ":".join(rhex(1) for _ in range(16))
        self.write([("The authenticity of host '%s' can't be established." % host, "out")])
        self.write([("ED25519 key fingerprint is SHA256:%s" % base64.b64encode(os.urandom(24)).decode()[:43], "out")])
        yield 0.4
        self.write([("Warning: Permanently added '%s' (ED25519) to the list of known hosts." % host, "warn")])
        self.write([("%s@%s's password: " % (user, host), "out")], nl=False)
        for _ in range(random.randint(8, 12)):
            self.part("*", "dim")
            yield 0.07
        self.write([("", "out")])
        yield 0.3
        if random.random() < 0.18:
            self.bad("Permission denied, please try again.")
            self.app.mission.trace = min(99, self.app.mission.trace + 4)
            self.write([("  consejo: reintenta, o usa 'brute ssh %s' primero" % host, "dim")])
            return
        host_short = host.split(".")[0]
        files = self._mk_fs(user, host_short, os_name)
        self.ssh = dict(user=user, host=host, short=host_short, ip=ip, os=os_name, files=files, cwd="/root" if user == "root" else "/home/" + user,
                        t0=time.time(), tilde=None, got=set())
        self.ssh["tilde"] = lambda s=self.ssh: ("~" + s["cwd"][len("/root" if s["user"] == "root" else "/home/" + s["user"]):]
                                                if s["cwd"].startswith("/root" if s["user"] == "root" else "/home/" + s["user"]) else s["cwd"])
        self.set_mode("ssh", quiet=True)
        try:
            self.app.nova.narrate("mode_ssh", prio=2)
        except Exception:
            pass
        self.write([("Welcome to %s (GNU/Linux %d.%d.0-%d-generic x86_64)" % (os_name, random.choice([5, 6]), random.randint(1, 8), random.randint(20, 130)), "sshout")])
        self.write([("", "out")])
        self.write([(" * Documentation:  https://help.ubuntu.com", "sshout")])
        self.write([("   %d updates can be applied immediately." % random.randint(3, 60), "warn")])
        self.write([("Last login: %s from %s" % ((datetime.datetime.now() - datetime.timedelta(hours=random.randint(2, 200))).strftime("%a %b %d %H:%M:%S %Y"), rip()), "sshout")])
        self.write([("sesión simulada · 'help' muestra comandos · 'privesc' escala a root · 'exit' vuelve", "dim")])
        self.app.add_xp(8, "ssh")

    def _mk_fs(self, user, host, os_name):
        home = "/root" if user == "root" else "/home/" + user
        us = random.sample(FAKE_USERS[:12], 4)
        passwd = "root:x:0:0:root:/root:/bin/bash\ndaemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin\nwww-data:x:33:33:www-data:/var/www:/usr/sbin/nologin\n"
        passwd += "\n".join("%s:x:%d:%d::/home/%s:/bin/bash" % (u, 1000 + i, 1000 + i, u) for i, u in enumerate(set([user] + us) - {"root"}))
        shadow = "\n".join("%s:$6$%s$%s:19800:0:99999:7:::" % (u, rhex(4), base64.b64encode(os.urandom(30)).decode()[:60].replace("+", ".")) for u in ["root"] + us[:3])
        auth = "\n".join("%s %s sshd[%d]: %s" % ("Nov %2d" % random.randint(1, 13), host, random.randint(900, 9999),
                                                 random.choice(["Accepted publickey for %s from %s port %d ssh2" % (random.choice(us), rip(), random.randint(30000, 60000)),
                                                                "Failed password for invalid user %s from %s port %d ssh2" % (random.choice(["oracle", "test", "pi", "admin"]), rip(), random.randint(30000, 60000)),
                                                                "pam_unix(sshd:session): session opened for user %s" % random.choice(us)])) for _ in range(9))
        key = "-----BEGIN OPENSSH PRIVATE KEY-----\n" + "\n".join(base64.b64encode(os.urandom(48)).decode() for _ in range(5)) + "\n-----END OPENSSH PRIVATE KEY-----"
        f = {
            "/etc/hostname": host, "/etc/os-release": 'PRETTY_NAME="%s"\nNAME="%s"\nVERSION_ID="22.04"' % (os_name, os_name.split()[0]),
            "/etc/passwd": passwd, "/etc/shadow": shadow, "/etc/hosts": "127.0.0.1 localhost\n127.0.1.1 %s\n10.0.%d.%d db-internal\n" % (host, random.randint(0, 9), random.randint(2, 200)),
            "/var/log/auth.log": auth, "/var/log/syslog": "\n".join("Nov 13 %02d:%02d:%02d %s CRON[%d]: (root) CMD (/opt/app/backup.sh)" % (random.randint(0, 23), random.randint(0, 59), random.randint(0, 59), host, random.randint(1000, 9999)) for _ in range(6)),
            "/srv/www/html/config.php": "<?php\n$db_host = 'db-internal';\n$db_user = 'webapp';\n$db_pass = '%s';\n$api_key = '%s';" % (rpass(14), rhex(16)),
            "/opt/app/.env": "SECRET_KEY=%s\nSTRIPE_KEY=sk_live_%s\nDATABASE_URL=postgres://app:%s@db-internal/prod" % (rhex(20), rhex(12), rpass(12)),
            "/opt/app/backup.sh": "#!/bin/bash\n# backup nocturno\ntar czf /tmp/bk.tgz /srv/www /opt/app\nscp /tmp/bk.tgz backup@db-internal:/vault/",
            home + "/notes.txt": "TODO: rotar claves del servidor\nTODO: borrar cuenta de %s\nOJO: la clave del backup está en .env" % random.choice(FAKE_USERS[:8]),
            home + "/backup.sql": "-- dump de la base de datos 'prod'\nINSERT INTO users VALUES (1,'%s','%s');\n-- (%d filas más)" % (random.choice(FAKE_USERS), md5(rpass(6)), random.randint(900, 99999)),
            home + "/.bash_history": "ls -la\ncd /opt/app\ncat .env\nsudo systemctl restart nginx\nssh backup@db-internal\nhistory -c",
            home + "/.ssh/id_rsa": key, home + "/.ssh/authorized_keys": "ssh-ed25519 AAAA%s admin@laptop" % base64.b64encode(os.urandom(30)).decode()[:40],
            "/tmp/readme.tmp": "temporal",
        }
        return f

    def _ssh_abs(self, p):
        import posixpath
        s = self.ssh
        p = (p or "").strip()
        if p in ("", "~"):
            p = "/root" if s["user"] == "root" else "/home/" + s["user"]
        elif p.startswith("~/"):
            p = ("/root" if s["user"] == "root" else "/home/" + s["user"]) + p[1:]
        if not p.startswith("/"):
            p = posixpath.join(s["cwd"], p)
        return posixpath.normpath(p)

    def _ssh_dirs(self):
        d = {"/", "/bin", "/etc", "/home", "/var", "/var/log", "/tmp", "/opt", "/root", "/srv", "/usr"}
        for p in self.ssh["files"]:
            q = p.rsplit("/", 1)[0]
            while q:
                d.add(q)
                q = q.rsplit("/", 1)[0]
        return d

    def _ssh_names(self, path):
        pre = path.rstrip("/") + "/"
        names = set()
        for p in list(self.ssh["files"]) + list(self._ssh_dirs()):
            if p.startswith(pre) and p != path:
                names.add(p[len(pre):].split("/")[0] + ("/" if (pre + p[len(pre):].split("/")[0]) in self._ssh_dirs() else ""))
        return sorted(n for n in names if n != "/")

    def _ssh_denied(self, p):
        return self.ssh["user"] != "root" and (p == "/etc/shadow" or p.startswith("/root/") or p == "/root")

    def _ssh_exec(self, line):
        s = self.ssh
        if s is None:
            self.set_mode("nexus", quiet=True)
            return
        parts = line.split()
        c, a = parts[0], parts[1:]
        T_ = "sshout"
        W = lambda t, tag=T_: self.write([(t, tag)])
        if c in ("exit", "logout", "quit", "nexus"):
            self.write([("logout", T_)])
            self.write([("Connection to %s closed." % s["host"], T_)])
            self.set_mode("nexus", quiet=True)
            return
        if c == "pwd":
            W(s["cwd"])
        elif c == "cd":
            tgt = self._ssh_abs(a[0] if a else "~")
            if self._ssh_denied(tgt):
                W("bash: cd: %s: Permission denied" % (a[0] if a else tgt), "err")
            elif tgt in self._ssh_dirs():
                s["cwd"] = tgt
                self._prompt_over = None
            else:
                W("bash: cd: %s: No such file or directory" % (a[0] if a else tgt), "err")
        elif c == "ls" or c == "ll":
            flags = "".join(x[1:] for x in a if x.startswith("-")) + ("l" if c == "ll" else "")
            tgt = self._ssh_abs(next((x for x in a if not x.startswith("-")), "."))
            if self._ssh_denied(tgt):
                W("ls: cannot open directory '%s': Permission denied" % tgt, "err")
            elif tgt in s["files"]:
                W(tgt.rsplit("/", 1)[1])
            elif tgt not in self._ssh_dirs():
                W("ls: cannot access '%s': No such file or directory" % tgt, "err")
            else:
                names = self._ssh_names(tgt)
                names = [n for n in names if "a" in flags or not n.startswith(".")]
                if "a" in flags:
                    names = [".", ".."] + names
                if "l" in flags:
                    W("total %d" % (len(names) * 4))
                    for n in names:
                        isd = n.endswith("/") or n in (".", "..")
                        full = tgt.rstrip("/") + "/" + n.rstrip("/")
                        sz = 4096 if isd else len(s["files"].get(full, "")) + 40
                        own = "root" if full.startswith(("/etc", "/var", "/root")) else s["user"]
                        self.write([("%s 1 %-8s %-8s %6d %s " % ("drwxr-xr-x" if isd else "-rw-r--r--", own, own, sz, "Nov %2d %02d:%02d" % (random.randint(1, 13), random.randint(0, 23), random.randint(0, 59))), T_),
                                    (n.rstrip("/"), "info" if isd else "out")])
                else:
                    self.write([(n.rstrip("/") + "  ", "info" if n.endswith("/") or n in (".", "..") else "out") for n in names] or [("", T_)])
        elif c in ("cat", "head", "tail", "less", "more"):
            if not a:
                W("%s: falta el archivo" % c, "err")
            for f in a:
                p = self._ssh_abs(f)
                if p in self._ssh_dirs():
                    W("%s: %s: Is a directory" % (c, f), "err")
                elif self._ssh_denied(p):
                    W("%s: %s: Permission denied" % (c, f), "err")
                    W("  (¿no eres root? prueba 'privesc')", "dim")
                elif p in s["files"]:
                    lines = s["files"][p].split("\n")
                    if c == "head":
                        lines = lines[:10]
                    elif c == "tail":
                        lines = lines[-10:]
                    for ln in lines:
                        W(ln)
                        yield 0.02
                    if any(k in p for k in ("shadow", "id_rsa", ".env", "config.php")) and p not in s["got"]:
                        s["got"].add(p)
                        self.app.add_xp(6, "loot")
                        W("  [+] credenciales útiles encontradas (XP +6)", "ok")
                else:
                    W("%s: %s: No such file or directory" % (c, f), "err")
        elif c == "whoami":
            W(s["user"])
        elif c == "id":
            W("uid=0(root) gid=0(root) groups=0(root)" if s["user"] == "root" else "uid=1000(%s) gid=1000(%s) groups=1000(%s),27(sudo)" % ((s["user"],) * 3))
        elif c == "hostname":
            W(s["short"])
        elif c == "uname":
            W("Linux %s 5.15.0-%d-generic #%d-Ubuntu SMP x86_64 GNU/Linux" % (s["short"], random.randint(70, 120), random.randint(70, 140)) if "-a" in a else "Linux")
        elif c == "uptime":
            W(" %s up %d days, %02d:%02d,  1 user,  load average: %.2f, %.2f, %.2f" % (time.strftime("%H:%M:%S"), random.randint(3, 200), random.randint(0, 23), random.randint(0, 59), random.random(), random.random(), random.random()))
        elif c == "date":
            W(time.strftime("%a %b %d %H:%M:%S UTC %Y"))
        elif c == "echo":
            W(" ".join(a))
        elif c == "env":
            for k in ("USER=" + s["user"], "HOME=" + self._ssh_abs("~"), "SHELL=/bin/bash", "LANG=en_US.UTF-8", "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin", "SSH_CONNECTION=%s 51234 %s 22" % (rip(), s["ip"])):
                W(k)
        elif c == "ps":
            W("    PID TTY          TIME CMD")
            for pid, n in ((1, "systemd"), (random.randint(300, 900), "sshd"), (random.randint(900, 2000), "nginx"), (random.randint(2000, 4000), "postgres"), (random.randint(4000, 9000), "bash"), (random.randint(9000, 20000), "ps")):
                W("%7d ?        00:%02d:%02d %s" % (pid, random.randint(0, 9), random.randint(0, 59), n))
        elif c in ("ss", "netstat"):
            W("State    Recv-Q Send-Q  Local Address:Port   Peer Address:Port  Process")
            for lp, n in ((22, "sshd"), (80, "nginx"), (443, "nginx"), (5432, "postgres")):
                W("LISTEN   0      128         0.0.0.0:%-6d      0.0.0.0:*      users:((\"%s\",pid=%d))" % (lp, n, random.randint(300, 4000)))
            W("ESTAB    0      0         %s:22   %s:%d  users:((\"sshd\",pid=%d))" % (s["ip"], rip(), random.randint(30000, 60000), random.randint(5000, 9000)))
        elif c in ("ip", "ifconfig"):
            W("1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536")
            W("    inet 127.0.0.1/8 scope host lo")
            W("2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500")
            W("    link/ether %s brd ff:ff:ff:ff:ff:ff" % ":".join(rhex(1) for _ in range(6)))
            W("    inet %s/24 brd 10.0.0.255 scope global eth0" % s["ip"])
        elif c == "df":
            W("Filesystem      Size  Used Avail Use% Mounted on")
            used = random.randint(20, 60)
            W("/dev/sda1        80G   %dG   %dG  %d%% /" % (used, 80 - used, int(used / 0.8)))
            W("tmpfs           7.8G     0  7.8G   0% /dev/shm")
        elif c == "free":
            W("               total        used        free      shared  buff/cache   available")
            W("Mem:        16318420     %d     %d      1204     %d     %d" % (random.randint(3000000, 9000000), random.randint(1000000, 5000000), random.randint(2000000, 6000000), random.randint(4000000, 9000000)))
        elif c in ("w", "who"):
            W(" %s up 12 days,  1 user" % time.strftime("%H:%M:%S"))
            W("USER     TTY      FROM             LOGIN@   IDLE")
            W("%-8s pts/0    %-16s %s   0.00s" % (s["user"], rip(), time.strftime("%H:%M")))
        elif c == "last":
            for _ in range(5):
                W("%-8s pts/0        %-16s Nov %2d %02d:%02d   still logged in" % (random.choice(FAKE_USERS[:6]), rip(), random.randint(1, 13), random.randint(0, 23), random.randint(0, 59)))
        elif c == "history":
            for i, ln in enumerate(s["files"].get(self._ssh_abs("~/.bash_history"), "").split("\n"), 1):
                W("%5d  %s" % (i, ln))
        elif c == "grep":
            if len(a) >= 2:
                pat, p = a[0].strip("'\""), self._ssh_abs(a[-1])
                if p in s["files"] and not self._ssh_denied(p):
                    for ln in s["files"][p].split("\n"):
                        if pat.lower() in ln.lower():
                            W(ln)
                else:
                    W("grep: %s: No such file or directory" % a[-1], "err")
            else:
                W("uso: grep patrón archivo", "dim")
        elif c == "find":
            pat = a[-1].strip("'\"*") if a else ""
            for p in sorted(s["files"]):
                if pat in p and not self._ssh_denied(p):
                    W(p)
        elif c in ("wget", "curl"):
            W("--%s--  %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), a[-1] if a else "?"))
            W("(simulado: sin salida a internet desde esta sesión)", "dim")
        elif c == "sudo":
            if a[:1] == ["-l"]:
                W("User %s may run the following commands on %s:" % (s["user"], s["short"]))
                W("    (ALL : ALL) NOPASSWD: /usr/bin/find, /usr/bin/vim")
                W("  ↑ find con sudo sin contraseña: vector clásico. Prueba 'privesc'", "warn")
            elif a[:1] in (["su"], ["-i"], ["bash"]):
                yield from self._ssh_privesc()
            else:
                W("[sudo] password for %s: " % s["user"])
                W("Sorry, try again.", "err")
        elif c == "su":
            yield from self._ssh_privesc()
        elif c == "privesc":
            yield from self._ssh_privesc()
        elif c in ("download", "get", "scp"):
            p = self._ssh_abs(a[0] if a else "")
            if p in s["files"] and not self._ssh_denied(p):
                total = len(s["files"][p]) + random.randint(2000, 90000)
                yield from self.progress("descargando %s" % p.rsplit("/", 1)[1], 16, 0.04)
                W("%d bytes recibidos · guardado en el botín" % total, "ok")
                self.loot = (self.loot or []) + [p.rsplit("/", 1)[1]]
                self.app.add_xp(10, "download")
            else:
                W("download: archivo no disponible (%s)" % (a[0] if a else "falta nombre"), "err")
        elif c in ("clear", "cls"):
            self.cmd_clear([])
        elif c in ("help", "?"):
            for ln in ("ls [-la] · cd · cat/head/tail · pwd · whoami · id · uname -a · ps · ss · ip · df · free · w · last · history · env · grep · find",
                       "privesc / su / sudo -l  → conviértete en root     download <archivo>  → exfiltra al botín",
                       "pistas: lee .env, config.php, id_rsa, notes.txt · como root: /etc/shadow · exit vuelve a NEXUS"):
                W(ln, "dim")
        else:
            W("bash: %s: command not found" % c, "err")

    def _ssh_privesc(self):
        s = self.ssh
        if s["user"] == "root":
            self.write([("ya eres root.", "sshout")])
            return
        for ln in ("[*] buscando binarios SUID...", "[*] sudo -l: find permitido sin contraseña", "[*] sudo find . -exec /bin/sh \\; -quit"):
            self.write([(ln, "sshout")])
            yield 0.35
        yield from self.progress("escalando", 14, 0.04)
        s["user"] = "root"
        s["cwd"] = "/root"
        self._prompt_over = None
        self.write([("# uid=0(root) gid=0(root)", "ok")])
        self.app.mission.trace = min(99, self.app.mission.trace + 6)
        self.app.add_xp(20, "privesc")
        self.app.banner("ROOT", "%s@%s" % ("root", s["host"]), "ok", 2.5)

    # ───────── nuevos comandos de hacking [SIM] ─────────
    def _sim(self, tag="SIM"):
        self.write([("[%s] teatro: no se envía ni se toca nada." % tag, "dim")])

    def cmd_nikto(self, a):
        self._sim()
        tgt = self._tgt(a)
        srv = random.choice(["nginx/1.18.0 (Ubuntu)", "Apache/2.4.41 (Ubuntu)", "Microsoft-IIS/10.0", "nginx/1.14.2", "Apache/2.2.34"])
        self.write([("- NIKTO-NX 2.5  objetivo %s  puerto %d" % (tgt, random.choice([80, 443, 8080, 8443])), "head")])
        self.write([("+ Servidor: %s" % srv, "info")])
        yield 0.4
        pool = ["/admin/: panel de administración accesible sin restricción de IP", "/backup.zip: copia de seguridad descargable", "Cabecera X-Frame-Options ausente (clickjacking)",
                "Cabecera X-Content-Type-Options ausente", "/phpinfo.php: phpinfo() expuesto", "Método TRACE habilitado (XST)", "/.git/HEAD: repositorio git expuesto",
                "Cookie de sesión sin atributo HttpOnly", "Listado de directorios habilitado en /uploads/", "/server-status: accesible", "Cabecera Server revela versión exacta",
                "/robots.txt contiene 6 rutas interesantes", "/config.php.bak: copia de configuración", "Certificado TLS caduca en %d días" % random.randint(1, 20)]
        for f in random.sample(pool, random.randint(5, 8)):
            yield from self.spin("probando", random.uniform(0.2, 0.5))
            self.write([("+ NX-%05d: " % random.randint(1, 99999), "warn"), (f, "out")])
        self.good("%d comprobaciones, %d hallazgos (inventados)" % (random.randint(6000, 7500), random.randint(5, 9)))

    def cmd_payload(self, a):
        self._sim()
        kind = (a[0] if a else random.choice(["reverse_tcp", "bind_tcp", "dropper", "macro_doc", "powershell_stager"]))
        arch = random.choice(["x64", "x86", "arm64"])
        self.info("tipo %s · arquitectura %s · LHOST %s LPORT %d" % (kind, arch, rip(), random.choice([4444, 8443, 31337, 1337])))
        for enc in random.sample(["xor-dynamic (3 iteraciones)", "base64+gzip", "polimórfico mutate-v2", "AES-CTR envoltorio", "padding aleatorio 512B"], 3):
            yield from self.progress("encoder: %s" % enc[:14], 10, 0.025)
            self.write([("    ✓ " + enc, "dim")])
        for _ in range(4):
            off = random.randint(0, 0xfff0)
            self.write([("%08x  " % off, "dim"), (" ".join(rhex(1) for _ in range(12)), "out")])
            yield 0.05
        size = random.randint(180, 9000)
        self.good("payload_%s.bin  %d bytes (NO se ha escrito en disco)" % (rhex(2), size))
        self.write([("  evasión AV: %d/68 detecciones (cifra inventada)" % random.choice([0, 0, 1, 2]), "ok")])

    def cmd_pivot(self, a):
        self._sim()
        host = self._tgt(a)
        m = self.app.mission
        self.info("sesión en %s como %s" % (host, random.choice(["svc_web", "www-data", "jenkins"])))
        for ln in ("enumerando interfaces: eth0 %s · eth1 10.%d.%d.4 (interna)" % (rip(), random.randint(0, 250), random.randint(0, 250)),
                   "levantando túnel SOCKS5 en 127.0.0.1:%d" % random.choice([1080, 9050, 1081]),
                   "añadiendo ruta 10.%d.0.0/16 a través de la sesión" % random.randint(0, 250)):
            self.write([("  " + ln, "dim")])
            yield 0.3
        yield from self.progress("barrido de la red interna", 20, 0.03)
        for i in range(random.randint(3, 6)):
            self.write([("  10.%d.%d.%-3d " % (random.randint(0, 250), random.randint(0, 9), random.randint(2, 250)), "ok"),
                        (random.choice(["DC01 (Windows Server)", "fileserver", "db-prod", "jenkins-ci", "printer", "vpn-gw", "backup-nas"]), "out")])
            yield 0.15
        try:
            self.app.topo.infect()
        except Exception:
            pass
        m.trace = min(99, m.trace + random.uniform(3, 8))
        self.good("movimiento lateral completado")

    def cmd_privesc(self, a):
        self._sim()
        self.info("enumeración local (estilo linpeas)")
        checks = [("kernel y parches", "5.15.0-%d (vulnerable a un CVE local)" % random.randint(70, 90)), ("binarios SUID", "/usr/bin/find /usr/bin/pkexec"),
                  ("sudo -l", "NOPASSWD: /usr/bin/vim"), ("tareas cron escribibles", "/opt/app/backup.sh (666)"), ("capabilities", "cap_setuid+ep /usr/bin/python3"),
                  ("contenedores", "usuario en el grupo docker")]
        for k, v in random.sample(checks, 4):
            yield from self.spin(k, 0.3)
            self.write([("  %-24s" % k, "dim"), (v, "warn")])
        vec = random.choice(["sudo vim -c ':!/bin/sh'", "cron hijack en backup.sh", "python3 -c 'import os;os.setuid(0)'", "docker run -v /:/mnt alpine chroot /mnt"])
        self.info("vector elegido: %s" % vec)
        yield from self.progress("escalando", 16, 0.035)
        self.good(random.choice(["uid=0(root) gid=0(root)", "NT AUTHORITY\\SYSTEM", "euid=0 vía cap_setuid"]))
        self.app.mission.trace = min(99, self.app.mission.trace + random.uniform(4, 9))

    def cmd_tor(self, a):
        self._sim()
        cities = [c for c in CITIES if c != "HAV"]
        hops = random.sample(cities, 3)
        names = ["Entry", "Middle", "Exit"]
        prev = "HAV"
        for i, h in enumerate(hops):
            yield from self.spin("circuito salto %d" % (i + 1), 0.5)
            self.write([("  %-7s " % names[i], "dim"), ("%-16s" % ("%s%s" % (random.choice(["Quiet", "Iron", "Moon", "Delta", "Nyx", "Orbit"]), random.randint(10, 99))), "info"),
                        ("%-14s" % CITIES[h][2][:13], "out"), ("%s" % rhex(5).upper(), "dim")])
            try:
                self.app.globe.add_arc(prev, h, "trace")
            except Exception:
                pass
            prev = h
        m = self.app.mission
        m.trace = max(0, m.trace - random.uniform(12, 28))
        m.stealth = min(99, m.stealth + 8)
        self.good("circuito construido. TRACE %d%%  STEALTH %d%%  (latencia +%dms)" % (m.trace, m.stealth, random.randint(200, 900)))

    def cmd_zeroday(self, a):
        self._sim()
        self.write([("RESERVA DE ZERO-DAYS", "head")])
        items = [("NX-ZD-%04d" % random.randint(1, 9999), random.choice(["VPN appliance", "mail gateway", "hypervisor", "router OS", "PDF reader", "kernel"]),
                  "%.1f" % random.uniform(7.8, 10)) for _ in range(3)]
        for i, (n, t, s) in enumerate(items):
            self.write([("  [%d] %s  " % (i + 1, n), "info"), ("%-14s" % t, "out"), ("CVSS %s" % s, "warn")])
            yield 0.15
        n, t, s = random.choice(items)
        self.info("usando %s contra %s" % (n, self._tgt(a)))
        yield from self.progress("armando", 14, 0.035)
        yield from self.progress("disparando", 14, 0.04)
        self.good("explotación exitosa. El día cero se ha 'quemado' (-1 en la reserva)")
        self.app.mission.trace = min(99, self.app.mission.trace + random.uniform(5, 12))
        self.app.add_xp(15, "zeroday")

    def cmd_neural(self, a):
        self._sim()
        self.info("entrenando NEXUS-GAN (generador de exploits) en %d muestras" % random.randint(8000, 90000))
        loss, acc = 2.4, 0.31
        for ep in range(1, 13):
            loss *= random.uniform(0.6, 0.85)
            acc = min(0.99, acc + random.uniform(0.04, 0.09))
            self.replace_line([("  época %2d/12  " % ep, "dim"), ("loss %.4f  " % loss, "warn"), ("acc %5.1f%%  " % (acc * 100), "ok"), ("█" * int(acc * 20), "info")])
            yield 0.2
        self.write([("", "out")])
        self.good("modelo convergido. Generando candidatos...")
        for _ in range(3):
            self.write([("  candidato NX-AI-%04d  prob. de éxito %.1f%%" % (random.randint(1, 9999), random.uniform(55, 97)), "out")])
            yield 0.2

    def cmd_exfil(self, a):
        self._sim()
        tgt = self._tgt(a)
        self.info("exfiltrando de %s por %s" % (tgt, random.choice(["túnel DNS", "HTTPS camuflado", "ICMP", "canal ADS", "WebSocket cifrado"])))
        files = self.loot or random.sample(LOOT_ITEMS, 3)
        st = self.app.stats
        for f in files:
            mb = random.uniform(2, 400)
            steps = 14
            for i in range(steps + 1):
                st.net_out.append(random.uniform(40, 120))
                self.replace_line([("  %-22s" % f[:21], "info"), ("█" * i + "░" * (steps - i), "ok"), ("  %5.1f MB  %5.1f MB/s" % (mb * i / steps, random.uniform(3, 40)), "dim")])
                yield 0.04
            self.write([("", "out")])
        self.app.mission.trace = min(99, self.app.mission.trace + random.uniform(6, 14))
        self.good("%d archivos exfiltrados · hash de verificación %s" % (len(files), rhex(8)))
        self.app.add_xp(10, "exfil")

    def cmd_sniff(self, a):
        self._sim()
        ifc = a[0] if a else random.choice(["eth0", "wlan0", "Ethernet", "Wi-Fi"])
        self.info("capturando en %s (filtro: any)  ·  Ctrl+C para parar" % ifc)
        protos = [("TCP", "[SYN] seq=0 win=64240"), ("TLS", "Client Hello  SNI=%s" % random.choice(TARGETS)), ("DNS", "Standard query A %s" % random.choice(TARGETS)),
                  ("HTTP", "GET /index.html HTTP/1.1"), ("ARP", "Who has %s? Tell %s" % (rip(), rip())), ("UDP", "len=%d" % random.randint(30, 600))]
        for i in range(random.randint(16, 24)):
            p, info = random.choice(protos)
            self.write([("%7.3f  " % (i * 0.137), "dim"), ("%-15s > %-15s " % (rip(), rip()), "out"), ("%-5s" % p, "info"), (info, "dim")])
            if random.random() < 0.1:
                self.write([("         ⚠ credenciales en claro: user=%s pass=%s (inventado)" % (random.choice(FAKE_USERS), rpass(7)), "err")])
            yield random.uniform(0.04, 0.14)
        self.good("%d paquetes capturados · captura_%s.pcap (no escrita)" % (random.randint(400, 9000), rhex(2)))

    def cmd_fuzz(self, a):
        self._sim()
        tgt = self._tgt(a)
        self.info("fuzzing de %s (mutación + cobertura)" % tgt)
        crash = random.randint(180, 900)
        for it in range(0, crash, random.randint(40, 70)):
            self.replace_line([("  iteración %6d  " % (it * 37), "dim"), ("cobertura %2d%%  " % min(95, it // 9 + 12), "ok"), ("entrada %d bytes" % (it + 16), "out")])
            yield 0.07
        self.write([("", "out")])
        self.bad("CRASH: SIGSEGV en 0x%08x  (entrada de %d bytes)" % (random.randint(0x400000, 0x7fffffff), crash))
        self.write([("    EIP/RIP controlado: %s" % random.choice(["sí (offset %d)" % random.randint(100, 800), "parcialmente"]), "warn")])
        self.good("candidato a vulnerabilidad guardado: crash_%s.bin" % rhex(2))

    def cmd_honeypot(self, a):
        self._sim()
        ip = a[0] if a else rip()
        self.info("analizando %s en busca de señales de trampa" % ip)
        for k in ("latencia constante sospechosa", "banner SSH idéntico a Cowrie", "puertos abiertos 'demasiado perfectos'", "sin tráfico real de fondo", "TTL inconsistente"):
            yield from self.spin(k, 0.25)
            self.write([("  %-38s" % k, "dim"), (random.choice(["normal", "normal", "SOSPECHOSO"]), "warn")])
        if random.random() < 0.45:
            self.warn("%s es un HONEYPOT (Cowrie/T-Pot). Aborta: te están observando." % ip)
            self.app.mission.trace = min(99, self.app.mission.trace + 5)
        else:
            self.good("%s parece un sistema real. Vía libre." % ip)

    def cmd_stego(self, a):
        self._sim()
        txt = " ".join(a) or "mensaje secreto"
        self.info("ocultando %d bytes en imagen_%s.png (LSB)" % (len(txt.encode()), rhex(2)))
        yield from self.progress("incrustando bits", 18, 0.03)
        bits = "".join(format(b, "08b") for b in txt.encode()[:6])
        self.write([("  primeros bits: %s..." % bits, "dim")])
        self.good("imagen idéntica a simple vista. Diferencia media: 0.%03d%%" % random.randint(1, 40))

    def cmd_bluetooth(self, a):
        self._sim()
        devs = ["Galaxy Buds de Laura", "JBL Flip 6", "Tesla Model Y", "MiBand 7", "AirPods de Marco", "Smart TV Samsung", "Cerradura-Puerta", "Auriculares-Sony", "Beacon-%s" % rhex(2),
                "Reloj Fit", "Impresora BT", "Teclado K380"]
        self.info("escaneo BLE (dispositivos inventados)")
        for d in random.sample(devs, 7):
            rssi = -random.randint(38, 92)
            self.write([("  %s  " % ":".join(rhex(1).upper() for _ in range(6)), "dim"), ("%-24s" % d, "out"), ("%4d dBm " % rssi, "info"),
                        ("▮" * max(1, (100 + rssi) // 10), "ok")])
            yield 0.12
        self.good("7 dispositivos en rango")

    def cmd_rfid(self, a):
        self._sim()
        self.info("acerca la tarjeta al lector... (simulado)")
        yield from self.spin("esperando tarjeta", 1.0)
        uid = ":".join(rhex(1).upper() for _ in range(4))
        self.write([("  UID %s · MIFARE Classic 1K · SAK 08" % uid, "ok")])
        for s in range(0, 16, 3):
            self.write([("  sector %2d  clave A %s  ✓" % (s, rhex(6).upper()), "dim")])
            yield 0.15
        yield from self.progress("clonando en tarjeta mágica", 14, 0.04)
        self.good("tarjeta clonada (ficticia). Abre %s." % random.choice(["la puerta del laboratorio", "el garaje", "la sala de servidores"]))

    def cmd_gps(self, a):
        self._sim()
        key = (a[0].upper() if a else random.choice([c for c in CITIES if c != "HAV"]))
        if key not in CITIES:
            key = next((k for k, v in CITIES.items() if v[2].lower().startswith((a[0] if a else "").lower())), random.choice(list(CITIES)))
        lat, lon, name = CITIES[key]
        self.info("generando señal GPS falsa en L1 (1575.42 MHz)")
        yield from self.progress("sincronizando satélites", 14, 0.04)
        self.good("posición falseada: %s  (%.4f, %.4f)" % (name, lat, lon))
        try:
            self.app.globe.add_arc("HAV", key, "out")
        except Exception:
            pass

    def cmd_firmware(self, a):
        self._sim()
        self.info("analizando firmware_%s.bin" % random.choice(["tp_router", "cam_hd", "nas_x2", "iot_hub"]))
        for off, d in ((64, "cabecera uImage"), (0x2000, "kernel Linux 3.%d" % random.randint(4, 18)), (0x1c0000, "sistema de archivos SquashFS (xz)"), (0x7e0000, "partición de configuración JFFS2")):
            self.write([("  0x%08x  " % off, "dim"), (d, "out")])
            yield 0.2
        yield from self.progress("extrayendo squashfs", 14, 0.03)
        self.write([("  /etc/passwd: ", "dim"), ("admin:$1$%s:0:0" % rhex(4), "warn")])
        self.write([("  /usr/sbin/telnetd -l /bin/sh -p 31337  (puerta trasera)", "err")])
        self.good("credencial por defecto y puerta trasera localizadas (firmware ficticio)")

    def cmd_radio(self, a):
        self._sim()
        self.info("escáner SDR 24-1766 MHz")
        bands = [("98.%d MHz" % random.randint(1, 9), "FM comercial"), ("1090 MHz", "ADS-B aviones"), ("162.55 MHz", "NOAA meteo"), ("433.92 MHz", "sensores ISM"),
                 ("156.8 MHz", "VHF marina"), ("868 MHz", "LoRa"), ("1575.42 MHz", "GPS L1"), ("121.5 MHz", "emergencia aérea")]
        for f, d in random.sample(bands, 6):
            self.write([("  %-12s" % f, "info"), ("%-18s" % d, "out"), ("▮" * random.randint(2, 10), "ok"), ("  %d dBm" % -random.randint(40, 110), "dim")])
            yield 0.18
        self.good("6 señales identificadas")

    def cmd_scada(self, a):
        self._sim("SIM · planta ficticia")
        self.info("conectando a PLC de 'Aurora Grid' (central eléctrica FICTICIA)")
        yield from self.progress("handshake Modbus/TCP", 12, 0.04)
        for k, v, u, lim in (("Turbina 1", random.randint(2800, 3100), "rpm", 3200), ("Presión caldera", random.randint(80, 140), "bar", 150), ("Temperatura núcleo", random.randint(300, 520), "°C", 550), ("Carga de red", random.randint(55, 95), "%", 100)):
            ratio = v / float(lim)
            self.write([("  %-20s" % k, "dim"), ("%5d %-4s " % (v, u), "out"), ("█" * int(ratio * 24), "ok" if ratio < 0.85 else "warn"), ("░" * (24 - int(ratio * 24)), "dim")])
            yield 0.2
        self.warn("modo de laboratorio: no controlas nada real. Todo inventado.")

    # ───────── comandos REALES nuevos ─────────
    def _syscmd(self, args, timeout=20):
        def job(b):
            r = subprocess.run(args, capture_output=True, timeout=timeout, creationflags=NOWIN)
            return r.stdout.decode(oem_encoding(), "replace") + r.stderr.decode(oem_encoding(), "replace")
        return self.bg(job)

    def cmd_hostinfo(self, a):
        r = REAL
        m = r.mem()
        up = r.uptime()
        art = ["   ▄▄▄▄▄▄▄   ", "  ██▀▀▀▀▀██  ", "  ██ ◉ ◉ ██  ", "  ██  ▽  ██  ", "  ▀███████▀  ", "   ▀▀   ▀▀   "]
        bat = r.battery()
        n = self.app.net
        info = [("USUARIO", "%s@%s" % (self.user, socket.gethostname())), ("SO", "%s %s" % (platform.system(), platform.release())),
                ("CPU", "%s (%d hilos)" % (r.cpu_name()[:34], os.cpu_count() or 0)), ("RAM", "%.1f GB · %d%% en uso" % (m[1] / 2.0 ** 30, m[0]) if m else "?"),
                ("ENCENDIDO", self._human(up) if up else "?"), ("BATERÍA", ("%d%% %s" % (bat[0], "(cargando)" if bat[1] else "")) if bat else "sin batería"),
                ("IP LOCAL", n.local), ("IP PÚBLICA", (n.pub or {}).get("ip", "?")), ("PYTHON", platform.python_version()),
                ("PANTALLA", "%dx%d" % (self.app.root.winfo_screenwidth(), self.app.root.winfo_screenheight())), ("TEMA", T.name)]
        for i in range(max(len(art), len(info))):
            self.write([(art[i] if i < len(art) else " " * 13, "info"), ("%-11s" % (info[i][0] if i < len(info) else ""), "dim"), (info[i][1] if i < len(info) else "", "out")])
            yield 0.05

    cmd_sysinfo = cmd_hostinfo

    def cmd_uptime(self, a):
        up = REAL.uptime()
        sess = int(time.time() - self.app.start)
        if up:
            self.write([("equipo encendido hace ", "dim"), (self._human(up), "ok")])
        self.write([("sesión NEXUS: %02d:%02d:%02d" % (sess // 3600, sess % 3600 // 60, sess % 60), "out")])

    def cmd_battery(self, a):
        b = REAL.battery()
        if not b:
            self.info("este equipo no tiene batería (o no se puede leer)")
            return
        pct, ac = b
        bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
        self.write([("batería ", "dim"), ("[%s] %d%%" % (bar, pct), "ok" if pct > 30 else "err"), ("  %s" % ("conectada al cargador" if ac else "usando batería"), "info")])

    def cmd_disks(self, a):
        roots = []
        if os.name == "nt":
            mask = ctypes.windll.kernel32.GetLogicalDrives()
            roots = ["%s:\\" % chr(65 + i) for i in range(26) if mask & (1 << i)]
        else:
            roots = ["/"] + [p for p in ("/home", "/mnt", "/media") if os.path.ismount(p)]
        self.write([("UNIDAD   TOTAL      LIBRE      USO", "head")])
        for r in roots:
            try:
                t, u, f = shutil.disk_usage(r)
            except Exception:
                continue
            pct = 100.0 * u / t if t else 0
            self.write([("%-8s " % r, "info"), ("%8.1f GB %8.1f GB  " % (t / 2.0 ** 30, f / 2.0 ** 30), "out"),
                        ("█" * int(pct / 5) + "░" * (20 - int(pct / 5)), "ok" if pct < 85 else "err"), (" %d%%" % pct, "dim")])
            yield 0.05

    def cmd_procs(self, a):
        self.info("procesos reales (por memoria)")
        if os.name == "nt":
            box = self._syscmd(["tasklist", "/fo", "csv", "/nh"])
        else:
            box = self._syscmd(["ps", "-eo", "pid=,comm=,rss="])
        yield from self.wait(box, "leyendo procesos")
        rows = []
        for ln in (box["res"] or "").splitlines():
            try:
                if os.name == "nt":
                    c = [x.strip('"') for x in re.split(r'","', ln.strip())]
                    rows.append((c[0].strip('"'), int(c[1]), int(re.sub(r"\D", "", c[4]) or 0) / 1024.0))
                else:
                    p = ln.split(None, 2)
                    rows.append((p[1], int(p[0]), int(p[2]) / 1024.0))
            except Exception:
                continue
        if not rows:
            self._net_fail(box["err"])
            return
        self.write([("%-28s %7s  %9s" % ("NOMBRE", "PID", "MEMORIA"), "head")])
        for n, pid, mb in sorted(rows, key=lambda r: -r[2])[:14]:
            self.write([("%-28s %7d  %7.1f MB" % (n[:28], pid, mb), "warn" if n.lower() in ("cmd.exe", "powershell.exe") else "out")])
            yield 0.03
        self.good("%d procesos en total" % len(rows))

    def cmd_conns(self, a):
        self.info("conexiones TCP reales de tu equipo")
        box = self._syscmd(["netstat", "-ano"] if os.name == "nt" else ["ss", "-tn"])
        yield from self.wait(box, "leyendo")
        names = {}
        if os.name == "nt":
            tb = self._syscmd(["tasklist", "/fo", "csv", "/nh"])
            yield from self.wait(tb, "nombres de proceso")
            for ln in (tb["res"] or "").splitlines():
                c = [x.strip('"') for x in re.split(r'","', ln.strip())]
                if len(c) > 1 and c[1].isdigit():
                    names[c[1]] = c[0].strip('"')
        est, lst = [], 0
        for ln in (box["res"] or "").splitlines():
            p = ln.split()
            if os.name == "nt" and len(p) >= 5 and p[0] == "TCP":
                if p[3].upper() == "ESTABLISHED":
                    est.append((p[1], p[2], names.get(p[4], p[4])))
                elif p[3].upper() == "LISTENING":
                    lst += 1
            elif os.name != "nt" and len(p) >= 5 and p[0].lower().startswith("estab"):
                est.append((p[3], p[4], ""))
        if not box["res"]:
            self._net_fail(box["err"])
            return
        self.write([("%-24s %-24s %s" % ("LOCAL", "REMOTO", "PROCESO"), "head")])
        for l, r, n in est[:16]:
            self.write([("%-24s %-24s " % (l[:23], r[:23]), "out"), (n, "info")])
            yield 0.03
        self.good("%d establecidas · %d escuchando" % (len(est), lst))

    def cmd_netcfg(self, a):
        box = self._syscmd(["ipconfig", "/all"] if os.name == "nt" else ["ip", "addr"])
        yield from self.wait(box, "leyendo adaptadores")
        if not box["res"]:
            self._net_fail(box["err"])
            return
        n = 0
        for ln in box["res"].splitlines():
            if not ln.strip():
                continue
            head = not ln.startswith(" ") and ln.rstrip().endswith(":")
            self.write([(ln.rstrip()[:110], "head" if head else "out")])
            n += 1
            if n % 6 == 0:
                yield 0.01
            if n > 90:
                self.write([("  ... (recortado)", "dim")])
                break

    def cmd_lan(self, a):
        sweep = bool(a and a[0].lower().startswith("sw"))
        loc = self.app.net.local
        parts = loc.split(".")
        if sweep and len(parts) == 4:
            self.info("barrido ping de %s.%s.%s.1-254 (tu red local, solo ICMP)" % tuple(parts[:3]))
            hosts = ["%s.%s.%s.%d" % (parts[0], parts[1], parts[2], i) for i in range(1, 255)]
            alive = []

            def one(h):
                args = ["ping", "-n", "1", "-w", "400", h] if os.name == "nt" else ["ping", "-c", "1", "-W", "1", h]
                try:
                    r = subprocess.run(args, capture_output=True, timeout=3, creationflags=NOWIN)
                    if b"ttl=" in r.stdout.lower():
                        alive.append(h)
                except Exception:
                    pass

            def job(b):
                sem = threading.Semaphore(48)
                ths = []

                def w(h):
                    with sem:
                        one(h)
                        b["prog"] = b["prog"] + 1 if b["prog"] else 1
                for h in hosts:
                    t = threading.Thread(target=w, args=(h,), daemon=True)
                    t.start()
                    ths.append(t)
                for t in ths:
                    t.join(30)
            box = self.bg(job)
            try:
                while not box["done"]:
                    self.replace_line([("  sondeando ", "dim"), ("%d/254  " % (box["prog"] or 0), "out"), ("%d vivos" % len(alive), "ok")])
                    yield 0.2
            finally:
                if not box["done"]:
                    box["cancel"] = True
            self.write([("", "out")])
        box = self._syscmd(["arp", "-a"] if os.name == "nt" else ["ip", "neigh"])
        yield from self.wait(box, "tabla ARP")
        rx = re.compile(r"(\d+\.\d+\.\d+\.\d+)\)?\s+(?:at\s+|dev\s+\S+\s+lladdr\s+)?((?:[0-9a-fA-F]{2}[-:]){5}[0-9a-fA-F]{2})")
        seen = {}
        for ln in (box["res"] or "").splitlines():
            m = rx.search(ln)
            if not m:
                continue
            ip, mac = m.group(1), m.group(2).lower().replace("-", ":")
            if mac.startswith(("ff:ff", "01:00:5e", "33:33")) or ip.endswith(".255") or int(ip.split(".")[0]) >= 224:
                continue
            seen[ip] = mac
        if not seen:
            self.warn("no hay vecinos en la tabla ARP todavía. Prueba 'lan sweep'.")
            return
        self.write([("%-16s %-18s %s" % ("IP", "MAC", "FABRICANTE / NOTA"), "head")])
        for ip in sorted(seen, key=lambda x: tuple(int(p) for p in x.split("."))):
            mac = seen[ip]
            note = OUI.get(mac[:8], "")
            if not note and int(mac[:2], 16) & 2:
                note = "MAC aleatoria/privada (móvil moderno)"
            if ip == loc:
                note = "← tu equipo"
            elif ip.endswith(".1"):
                note = (note + " puerta de enlace probable").strip()
            self.write([("%-16s " % ip, "ok"), ("%-18s " % mac, "out"), (note, "dim")])
            yield 0.05
        self.good("%d dispositivos vistos en tu red%s" % (len(seen), "" if sweep else "  (usa 'lan sweep' para buscar más)"))

    def cmd_wifiscan(self, a):
        self.info("redes WiFi REALES cercanas (lectura pasiva de tu adaptador)")
        if os.name == "nt":
            box = self._syscmd(["netsh", "wlan", "show", "networks", "mode=bssid"])
        else:
            box = self._syscmd(["nmcli", "-t", "-f", "SSID,SIGNAL,SECURITY", "dev", "wifi"])
        yield from self.wait(box, "escaneando")
        nets = []
        txt = box["res"] or ""
        if os.name == "nt":
            cur = None
            for ln in txt.splitlines():
                m = re.match(r"^\s*SSID\s+\d+\s*:\s*(.*)$", ln)
                if m:
                    cur = dict(ssid=m.group(1).strip() or "<oculta>", sig=0, auth="?", n=0)
                    nets.append(cur)
                    continue
                if cur is None:
                    continue
                if ":" in ln:
                    cur["n"] += 1
                    v = ln.split(":", 1)[1].strip()
                    if cur["n"] == 2:
                        cur["auth"] = v
                    pm = re.fullmatch(r"(\d{1,3})%", v)
                    if pm:
                        cur["sig"] = max(cur["sig"], int(pm.group(1)))
        else:
            for ln in txt.splitlines():
                p = ln.split(":")
                if len(p) >= 3 and p[0]:
                    nets.append(dict(ssid=p[0], sig=int(p[1] or 0), auth=p[2] or "abierta"))
        if not nets:
            self.warn("no se obtuvieron redes. ¿Tienes adaptador WiFi y la ubicación activada en Windows?")
            self.write([("  (Windows 11 24H2+ exige permiso de ubicación para listar redes)", "dim")])
            return
        self.write([("%-28s %-8s %s" % ("SSID", "SEÑAL", "SEGURIDAD"), "head")])
        for n in sorted(nets, key=lambda x: -x["sig"])[:20]:
            weak = any(k in n["auth"].upper() for k in ("OPEN", "ABIERT", "WEP")) or n["auth"] in ("", "abierta")
            self.write([("%-28s " % n["ssid"][:27], "out"), ("%3d%% " % n["sig"], "ok" if n["sig"] > 60 else "warn"), ("▮" * (n["sig"] // 10), "info"),
                        ("  %s" % n["auth"], "err" if weak else "dim")])
            yield 0.04
        self.good("%d redes visibles" % len(nets))

    def cmd_portcheck(self, a):
        if len(a) < 2:
            self.bad("uso: portcheck <host> <puerto> [puerto...]   (ej: portcheck localhost 80 443 3389)")
            return
        host = a[0]
        for p in a[1:12]:
            if not p.isdigit() or not (0 < int(p) < 65536):
                self.bad("puerto inválido: %s" % p)
                continue
            box = self.bg(lambda b, h=host, pp=int(p): tcp_ms(h, pp, 3.0))
            while not box["done"]:
                yield 0.05
            ms = box["res"]
            self.write([("  %s:%-6s " % (host, p), "out"), ("ABIERTO  %.0f ms" % ms if ms is not None else "cerrado/filtrado", "ok" if ms is not None else "dim")])

    def cmd_subdomains(self, a):
        if not a:
            self.bad("uso: subdomains <dominio>   (ej: subdomains example.com)")
            return
        dom = a[0].lower().strip(".")
        words = "www mail api dev test staging vpn admin portal ftp blog shop cdn static app beta git ns1 ns2 smtp imap webmail remote intranet docs support status auth login sso grafana jenkins db m".split()
        self.info("resolviendo %d subdominios comunes de %s por DNS (consultas públicas)" % (len(words), dom))
        found = []

        def job(b):
            sem = threading.Semaphore(16)
            ths = []

            def w(s):
                with sem:
                    try:
                        found.append((s, socket.gethostbyname("%s.%s" % (s, dom))))
                    except Exception:
                        pass
                    b["prog"] = (b["prog"] or 0) + 1
            for s in words:
                t = threading.Thread(target=w, args=(s,), daemon=True)
                t.start()
                ths.append(t)
            for t in ths:
                t.join(12)
        box = self.bg(job)
        try:
            while not box["done"]:
                self.replace_line([("  consultando ", "dim"), ("%d/%d" % (box["prog"] or 0, len(words)), "out"), ("  encontrados %d" % len(found), "ok")])
                yield 0.15
        finally:
            if not box["done"]:
                box["cancel"] = True
        self.write([("", "out")])
        for s, ip in sorted(found):
            self.write([("  %-10s" % s, "info"), ("%s.%s" % (s, dom) + " " * 2, "out"), (ip, "ok")])
            yield 0.04
        self.good("%d subdominios resuelven" % len(found) if found else "ningún subdominio común resolvió (o no hay internet)")

    def cmd_hashfile(self, a):
        if not a:
            self.bad("uso: hashfile <ruta>")
            return
        p = os.path.expanduser(" ".join(a).strip('"'))
        if not os.path.isfile(p):
            self.bad("no existe el archivo: %s" % p)
            return
        h5, h2 = hashlib.md5(), hashlib.sha256()
        size, done = os.path.getsize(p), 0
        try:
            with open(p, "rb") as f:
                while True:
                    b = f.read(4 * 1024 * 1024)
                    if not b:
                        break
                    h5.update(b)
                    h2.update(b)
                    done += len(b)
                    self.replace_line([("  leyendo ", "dim"), ("%d%%" % (100 * done // max(1, size)), "out")])
                    yield 0.001
        except Exception as e:
            self.bad("no se pudo leer: %s" % e)
            return
        self.write([("", "out")])
        self.write([("tamaño  ", "dim"), ("%s bytes" % format(size, ","), "out")])
        self.write([("md5     ", "dim"), (h5.hexdigest(), "out")])
        self.write([("sha256  ", "dim"), (h2.hexdigest(), "out")])

    # ───────── extras creativos ─────────
    def cmd_matrix(self, a):
        n = self.app.nova.name.upper()
        self.app.matrix_w.start(10.0, ["DESPIERTA, %s." % n, "LA RED ESTÁ VIVA.", "TÚ ERES LA SEÑAL."])
        self.info("entrando en la matriz (cualquier tecla sale)")
        yield 0

    def cmd_glitch(self, a):
        self.app.glitch()
        self.warn("interferencia detectada")
        yield 0

    def cmd_rank(self, a):
        app = self.app
        idx, name, nxt = rank_info(app.xp)
        self.write([("PERFIL DE OPERADOR", "head")])
        self.write([("  operador   ", "dim"), (app.nova.name, "out")])
        self.write([("  rango      ", "dim"), ("%s  (nivel %d/%d)" % (name, idx + 1, len(RANKS)), "ok")])
        if nxt:
            base = RANKS[idx][0]
            pct = (app.xp - base) / float(nxt - base)
            self.write([("  XP         ", "dim"), ("%d / %d  " % (app.xp, nxt), "out"), ("█" * int(pct * 24) + "░" * (24 - int(pct * 24)), "info")])
        else:
            self.write([("  XP         ", "dim"), ("%d  (rango máximo)" % app.xp, "ok")])
        self.write([("  comandos   ", "dim"), ("%d esta sesión" % app.cmd_count, "out")])
        c = app.contract
        if c:
            self.write([("  contrato   ", "dim"), ("%s  [%d/%d]  +%d XP" % (c["desc"], c["got"], c["n"], c["xp"]), "warn")])
        yield 0

    cmd_perfil = cmd_rank

    def cmd_briefing(self, a):
        app = self.app
        if app.contract and a and a[0] in ("nuevo", "new", "cambiar"):
            app.contract = None
        if not app.contract:
            desc, cmds, n, xp = random.choice(CONTRACTS)
            app.contract = dict(desc=desc, cmds=cmds, n=n, got=0, xp=xp)
            yield from self.typeline("NUEVO CONTRATO", "head")
        else:
            self.write([("CONTRATO ACTIVO", "head")])
        c = app.contract
        self.write([("  misión     ", "dim"), (c["desc"], "warn")])
        self.write([("  progreso   ", "dim"), ("%d/%d" % (c["got"], c["n"]), "out")])
        self.write([("  recompensa ", "dim"), ("+%d XP" % c["xp"], "ok")])
        self.write([("  cliente    ", "dim"), (random.choice(["Aurora Corp (anónimo)", "un periodista", "desconocido vía tor", "tu antiguo mentor"]), "out")])
        self.write([("  ('briefing nuevo' cambia de contrato)", "dim")])

    cmd_contract = cmd_briefing


class Terminal(ExtraCmds2, ExtraCmds, tk.Frame):
    def __init__(self, master, app):
        super().__init__(master, bg=T.bg, highlightthickness=1, highlightbackground=T.dim, bd=0)
        self.app = app
        self.bar = tk.Canvas(self, height=22, bg=T.bg, highlightthickness=0)
        self.bar.pack(fill="x")
        self.text = tk.Text(self, bg=T.bg, fg=T.fg, font=UI.fm, bd=0, highlightthickness=0, wrap="word",
                            padx=8, pady=2, cursor="arrow", state="disabled", insertwidth=0, takefocus=0,
                            width=10, height=5)
        self.text.pack(fill="both", expand=True)
        self.text.bindtags((str(self.text), str(self.winfo_toplevel()), "all"))
        self.text.bind("<MouseWheel>", lambda e: self.text.yview_scroll(-1 if e.delta > 0 else 1, "units"))
        self.text.bind("<Button-4>", lambda e: self.text.yview_scroll(-3, "units"))
        self.text.bind("<Button-5>", lambda e: self.text.yview_scroll(3, "units"))
        self.text.mark_set("inp", "1.0")
        self.text.mark_gravity("inp", "left")
        self.buf = ""
        self.hist = []
        self.hpos = 0
        self.busy = False
        self.line_open = False
        self.cursor_on = True
        self.runner = Runner(self)
        self._init_modes()
        self.user = (os.environ.get("USER") or os.environ.get("USERNAME") or "ghost")[:10]
        self.prompt = "%s@nexus:~# " % self.user
        self.apply_theme()
        T.subs.append(self.apply_theme)
        self._blink()

    # ---- aspecto ----
    def apply_theme(self):
        self.configure(bg=T.bg, highlightbackground=self._border())
        self.text.configure(bg=T.bg, fg=T.fg)
        self.bar.configure(bg=T.bg)
        for tag, col in (("out", T.fg), ("dim", T.dim), ("info", T.acc), ("ok", T.hi), ("warn", T.warn),
                         ("err", T.bad), ("prompt", T.acc), ("input", T.hi), ("head", T.hi), ("logo", T.fg)):
            self.text.tag_configure(tag, foreground=col)
        self.text.tag_configure("head", font=UI.fb)
        self.text.tag_configure("cursor", foreground=T.fg)
        self._mode_tags()
        self._draw_bar()

    def _draw_bar(self):
        self.bar.delete("all")
        w = max(100, self.bar.winfo_width())
        col = T.fg if self.mode == "nexus" else self.mode_color()
        self.bar.create_rectangle(8, 6, 14, 12, fill=col, outline="")
        self.bar.create_text(20, 9, text=self.bar_title(), anchor="w", fill=col, font=UI.fsb)
        self.bar.create_text(w - 8, 9, text=self.bar_sub(), anchor="e", fill=T.dim, font=UI.fs)
        try:
            if self.app.voice.enabled:
                self.bar.create_text(w // 2, 9, text="◉ NOVA %s" % ("HABLANDO" if self.app.voice.speaking else "VOZ"), fill="#ff8ad8", font=UI.fsb)
        except Exception:
            pass
        self.bar.create_line(8, 20, w - 8, 20, fill=T.faint)

    def _blink(self):
        self.cursor_on = not self.cursor_on
        try:
            self.text.tag_configure("cursor", foreground=T.fg if self.cursor_on else T.bg)
            if self.winfo_exists():
                self._draw_bar()
                self.after(530, self._blink)
        except tk.TclError:
            pass

    # ---- escritura ----
    def _unlock(self):
        self.text.configure(state="normal")

    def _lock(self):
        self.text.configure(state="disabled")

    def _render_prompt(self):
        self._unlock()
        self.text.delete("inp", "end-1c")
        self.text.insert("end-1c", self.prompt, self.ptag)
        self.text.insert("end-1c", self.buf, self.itag)
        self.text.insert("end-1c", "█", "cursor")
        self._lock()
        self.text.see("end")

    def write(self, segs, nl=True):
        self._unlock()
        if not self.busy:
            self.text.delete("inp", "end-1c")
        for s, tag in segs:
            self.text.insert("end-1c", s, tag)
        if nl:
            self.text.insert("end-1c", "\n")
            self.line_open = False
        else:
            self.line_open = True
        if not self.busy:
            self.text.mark_set("inp", "end-1c")
        self._lock()
        if not self.busy:
            self._render_prompt()
        self.text.see("end")

    def out(self, s="", tag="out"):
        self.write([(s, tag)])

    def part(self, s, tag="out"):
        self.write([(s, tag)], nl=False)

    def replace_line(self, segs):
        self._unlock()
        if self.line_open:
            self.text.delete("end-1c linestart", "end-1c")
        for s, tag in segs:
            self.text.insert("end-1c", s, tag)
        self.line_open = True
        self._lock()
        self.text.see("end")

    def info(self, s):
        self.write([("[*] ", "info"), (s, "out")])

    def good(self, s):
        self.write([("[+] ", "ok"), (s, "out")])

    def warn(self, s):
        self.write([("[!] ", "warn"), (s, "warn")])

    def bad(self, s):
        self.write([("[-] ", "err"), (s, "err")])

    def typeline(self, s, tag="out", step=2, delay=0.012):
        i = 0
        while i < len(s):
            self.part(s[i:i + step], tag)
            i += step
            yield delay
        self.write([("", tag)])

    def progress(self, label, steps=22, delay=0.03, width=24):
        for i in range(steps + 1):
            pct = i / float(steps)
            n = int(pct * width)
            self.replace_line([("%-22s" % label, "out"), ("[", "dim"), ("█" * n, "ok"), ("░" * (width - n), "dim"),
                               ("]", "dim"), (" %3d%%" % int(pct * 100), "info")])
            self.app.stats.load = min(1.0, self.app.stats.load + 0.03)
            yield delay
        self.write([("", "out")])

    # ---- entrada ----
    def on_key(self, e):
        ks = e.keysym
        if e.state & 0x4:  # Ctrl
            if ks.lower() == "c":
                self.interrupt()
            elif ks.lower() == "l":
                self.cmd_clear([])
                self._render_prompt() if not self.busy else None
            return "break"
        if ks == "Return":
            self.submit()
        elif ks == "BackSpace":
            if not self.busy:
                self.buf = self.buf[:-1]
                self._render_prompt()
        elif ks == "Up" and not self.busy and self.hist:
            self.hpos = max(0, self.hpos - 1)
            self.buf = self.hist[self.hpos]
            self._render_prompt()
        elif ks == "Down" and not self.busy and self.hist:
            self.hpos = min(len(self.hist), self.hpos + 1)
            self.buf = self.hist[self.hpos] if self.hpos < len(self.hist) else ""
            self._render_prompt()
        elif ks == "Tab" and not self.busy:
            self._tab()
            return "break"
        elif e.char and len(e.char) == 1 and ord(e.char) >= 32 and ord(e.char) != 127 and not self.busy:
            self.buf += e.char
            self._render_prompt()

    def interrupt(self):
        if self.game is not None:
            self.abort_game()
            return
        self.pending = None
        if self.busy:
            self.runner.cancel()
            self.app.crack_job = None
            self.warn("^C interrumpido")
            self._finish()
        elif self.buf:
            self.buf = ""
            self._render_prompt()

    def submit(self):
        if self.busy:
            return
        line = self.buf.strip()
        self._unlock()
        self.text.delete("inp", "end-1c")
        self.text.insert("end-1c", self.prompt, self.ptag)
        self.text.insert("end-1c", self.buf + "\n", self.itag)
        self.text.mark_set("inp", "end-1c")
        self._lock()
        self.buf = ""
        if not line:
            self._render_prompt()
            return
        if self.game is not None:
            self.game_input(line)
            return
        self.hist.append(line)
        self.hpos = len(self.hist)
        self.execute(line)

    def _exec_nexus(self, line):
        parts = line.split()
        cmd, args = parts[0].lower(), parts[1:]
        fn = getattr(self, "cmd_" + cmd.replace("-", "_"), None)
        self.busy = True
        self.app.stats.load = min(1.0, self.app.stats.load + 0.25)
        if fn is None:
            self.bad("%s: comando no encontrado. Escribe 'help'." % cmd)
            if cmd in WIN_HINT:
                self.write([("    ¿es un comando de Windows? Escribe 'win' (o F6) para el modo Windows, o 'win %s' para ejecutarlo una vez." % line[:40], "dim")])
            self._finish()
            return
        self._note_cmd(cmd, args)
        try:
            res = fn(args)
        except Exception:
            self.bad("error interno: " + traceback.format_exc().splitlines()[-1])
            self._finish()
            return
        if inspect.isgenerator(res):
            self.runner.start(self._safe(res), self._finish)
        else:
            self._finish()

    def _safe(self, gen):
        try:
            yield from gen
        except Exception:
            self.bad("error interno: " + traceback.format_exc().splitlines()[-1])

    def _finish(self):
        self.busy = False
        if self.line_open:
            self._unlock()
            self.text.insert("end-1c", "\n")
            self._lock()
            self.line_open = False
        self.text.mark_set("inp", "end-1c")
        self._trim()
        self._render_prompt()

    def run_line(self, line):  # usado por F4 / F1 / selftest
        if self.busy:
            return False
        self.buf = line
        self.submit()
        return True

    # ---- comandos ----
    def intro(self):
        for row in _logo():
            self.out(row, "logo")
            yield 0.04
        self.out("")
        yield from self.typeline("GHOSTWIRE TERMINAL v%s  -  sesión cifrada" % VERSION, "info")
        yield from self.typeline("Comandos [SIM] = teatro. Comandos de RED REAL = usan tu internet (solo lectura).", "dim")
        yield from self.typeline("Escribe 'help'. Prueba: hack, ddos, exploit, myip, breach, privesc, tor, lan.", "dim")
        yield from self.typeline("NUEVO: 'win' (F6) = comandos REALES de Windows, aparte de los de NEXUS · 'voz on' (F7) = Nova habla · 'nova' = charla · 'rank'", "info")
        self.out("")

    def cmd_clear(self, a):
        self._unlock()
        self.text.delete("1.0", "end-1c")
        self.text.mark_set("inp", "1.0")
        self._lock()
        self.line_open = False

    def cmd_fullscreen(self, a):
        self.app.toggle_fullscreen()

    def cmd_exit(self, a):
        yield from self.typeline("borrando huellas...", "warn")
        yield from self.progress("wipe /var/log", 12, 0.04)
        yield from self.typeline("hasta la vista.", "ok")
        yield 0.5
        self.app.root.destroy()

    def cmd_whoami(self, a):
        self.out("root  (probablemente)  -  %s@%s" % (self.user, socket.gethostname()))

    def cmd_date(self, a):
        self.out(datetime.datetime.now().strftime("%A %d %B %Y  %H:%M:%S"))

    def cmd_echo(self, a):
        self.out(" ".join(a))

    def cmd_sudo(self, a):
        self.warn("buen intento. Aquí no hay sudo: ya eres root.")

    def cmd_coffee(self, a):
        for ln in ("      ( (", "       ) )", "    ........", "    |      |]", "    \\      /", "     `----'"):
            self.out(ln, "warn")
            yield 0.08
        self.info("cafeína inyectada. Productividad +42%")

    def cmd_theme(self, a):
        if self.app.alarm_on:
            self.warn("no puedes cambiar el tema durante una alarma")
            return
        if not a:
            self.info("temas: " + " ".join(n.lower() for n in THEME_ORDER) + "   (actual: %s)" % T.name.lower())
            return
        n = {"cyber": "CYBER", "cyberblue": "CYBER"}.get(a[0].lower(), a[0].upper())
        if n in THEME_ORDER and T.set(n):
            self.good("tema -> %s" % n)
        else:
            self.bad("tema desconocido")

    def cmd_lockdown(self, a):
        self.warn("ACTIVANDO PROTOCOLO DE ALARMA")
        self.app.alarm("INTRUSION DETECTED", "LOCKDOWN INITIATED // TRACE ACTIVE")
        yield 0.2

    def cmd_status(self, a):
        m = self.app.mission
        self.write([("OPERACIÓN  ", "dim"), (m.op, "head")])
        self.write([("OBJETIVO   ", "dim"), ("%s [%s]" % (m.target, m.ip), "out")])
        self.write([("FASE       ", "dim"), (PHASES[m.active], "info")])
        self.write([("TRACE      ", "dim"), ("%d%%" % m.trace, "err" if m.trace > 60 else "out")])
        self.write([("STEALTH    ", "dim"), ("%d%%" % m.stealth, "out")])
        yield 0

    def cmd_vpn(self, a):
        hops = random.sample(list(CITIES), 4)
        self.info("reconfigurando cadena de proxies")
        for i in range(len(hops) - 1):
            self.app.globe.add_arc(hops[i], hops[i + 1], "trace")
            self.write([("   hop %d: " % (i + 1), "dim"), ("%s > %s" % (CITIES[hops[i]][2], CITIES[hops[i + 1]][2]), "out")])
            yield 0.25
        m = self.app.mission
        m.trace = max(0, m.trace - random.uniform(20, 35))
        self.good("rastro reducido. TRACE %d%%" % m.trace)

    def cmd_ghost(self, a):
        yield from self.typeline("entrando en modo fantasma...", "info")
        yield from self.progress("spoof MAC/UA/TTL", 14, 0.04)
        m = self.app.mission
        m.trace = max(0, m.trace - 15)
        m.stealth = min(99, m.stealth + 12)
        self.good("stealth %d%%  trace %d%%" % (m.stealth, m.trace))

    def cmd_hash(self, a):
        if not a:
            self.bad("uso: hash <texto>")
            return
        s = " ".join(a).encode()
        self.write([("md5     ", "dim"), (hashlib.md5(s).hexdigest(), "out")])
        self.write([("sha1    ", "dim"), (hashlib.sha1(s).hexdigest(), "out")])
        self.write([("sha256  ", "dim"), (hashlib.sha256(s).hexdigest(), "out")])

    def cmd_encrypt(self, a):
        if not a:
            self.bad("uso: encrypt <texto>")
            return
        s = " ".join(a).encode()
        key = hashlib.sha256(b"nexus" + os.urandom(4)).digest()
        ct = bytes(b ^ key[i % 32] for i, b in enumerate(s))
        yield from self.progress("cifrando", 10, 0.03)
        self.write([("cipher ", "dim"), (base64.b64encode(ct).decode(), "ok")])
        self.write([("key    ", "dim"), (key.hex()[:32] + "...", "out")])
        self.write([("(XOR + base64: demostración, no uses esto para algo serio)", "dim")])

    def cmd_ls(self, a):
        for n, c in FILES.items():
            self.write([("-rw-------  root  %5d  " % (len(c) * 3 + 120), "dim"), (n, "info")])
        yield 0

    def cmd_cat(self, a):
        if not a or a[0] not in FILES:
            self.bad("cat: archivo no encontrado (prueba 'ls')")
            return
        for ln in FILES[a[0]].split("\n"):
            self.out(ln)
            yield 0.05

    def cmd_decrypt(self, a):
        f = a[0] if a else "vault.enc"
        if f not in FILES:
            self.bad("archivo no encontrado")
            return
        self.info("iniciando descifrado de %s" % f)
        yield from self.progress("extrayendo cabecera", 10, 0.03)
        yield from self.progress("fuerza bruta de clave", 30, 0.05)
        yield from self.progress("verificando HMAC", 10, 0.03)
        self.good("clave recuperada: %s" % rpass(16))
        for ln in ("", "  >> vault.enc <<", "  Nadie estuvo aquí. Tú tampoco.", "  Las mejores intrusiones no dejan ruido.", ""):
            self.out(ln, "ok")
            yield 0.1
        self.app.banner("DECRYPTED", f, "ok", 2.5)

    def cmd_netstat(self, a):
        self.write([("Proto  Local               Foreign               State", "head")])
        sts = ["ESTABLISHED", "ESTABLISHED", "LISTEN", "TIME_WAIT", "SYN_SENT"]
        for _ in range(8):
            st = random.choice(sts)
            self.write([("tcp    %-19s %-21s " % ("0.0.0.0:%d" % random.choice([22, 443, 8080, 9050, 31337, 4444]),
                                                    "%s:%d" % (rip(), random.randint(1024, 65000))), "out"),
                        (st, "ok" if st == "ESTABLISHED" else "dim")])
            yield 0.06

    def cmd_nmap(self, a):
        return self.cmd_scan(a)

    def cmd_crack(self, a):
        if not a:
            self.bad("uso: crack <md5>   (ej: 'hash abc' y luego crack <ese md5>)")
            return
        target = a[0].lower()
        if len(target) != 32 or any(c not in "0123456789abcdef" for c in target):
            self.bad("eso no parece un hash md5 (32 hex)")
            return
        job = dict(hash=target, attempts=0, cand="", found=None)
        self.app.crack_job = job
        self.info("objetivo MD5 %s" % target)
        self.info("fase 1: diccionario (%d palabras)" % len(DICT_WORDS))
        for w in DICT_WORDS:
            job["attempts"] += 1
            job["cand"] = w
            if md5(w) == target:
                yield from self._cracked(job, w)
                return
            yield 0.02
        self.info("fase 2: fuerza bruta a-z0-9, longitud 1-4")
        cs = string.ascii_lowercase + string.digits
        for L in range(1, 5):
            it = itertools.product(cs, repeat=L)
            while True:
                chunk = list(itertools.islice(it, 25000))
                if not chunk:
                    break
                for c in chunk:
                    s = "".join(c)
                    if md5(s) == target:
                        job["attempts"] += 1
                        yield from self._cracked(job, s)
                        return
                job["attempts"] += len(chunk)
                job["cand"] = "".join(chunk[-1])
                self.replace_line([("  longitud %d  " % L, "dim"), ("%s candidatos" % format(job["attempts"], ","), "out")])
                yield 0.001
            self.write([("", "out")])
        self.bad("keyspace agotado: no está en el diccionario ni es ≤4 chars a-z0-9")
        self.app.crack_job = None

    def _cracked(self, job, w):
        job["found"] = w
        self.write([("", "out")])
        self.good("CLAVE ENCONTRADA: '%s'  (%s intentos)" % (w, format(job["attempts"], ",")))
        self.app.banner("CRACKED", "'%s'" % w, "ok", 2.5)
        self.app.log("OK", "md5 cracked: %s" % w)
        self.app.root.after(8000, lambda: setattr(self.app, "crack_job", None) if self.app.crack_job is job else None)
        yield 0


ALL_CMDS = sorted({n[4:].replace('_', '-') for n in dir(Terminal) if n.startswith('cmd_')})


# ════════════════════════════════════════════════════════════════════
#  PANTALLA DE ARRANQUE
# ════════════════════════════════════════════════════════════════════
class Boot(tk.Frame):
    def __init__(self, app):
        super().__init__(app.root, bg="#000000")
        self.app = app
        self.text = tk.Text(self, bg="#000000", fg=T.fg, font=UI.fm, bd=0, highlightthickness=0, wrap="none",
                            padx=24, pady=18, cursor="arrow", state="disabled", insertwidth=0, takefocus=0)
        self.text.pack(fill="both", expand=True)
        self.text.bindtags((str(self.text), str(self.winfo_toplevel()), "all"))
        for tag, col in (("ok", T.fg), ("dim", T.dim), ("hi", T.hi), ("warn", T.warn), ("acc", T.acc)):
            self.text.tag_configure(tag, foreground=col)
        self.place(x=0, y=0, relwidth=1, relheight=1)
        self.lift()
        self.runner = Runner(self)
        self.done = False
        self.runner.start(self.script(), self.finish)
        self.text.bind("<Button-1>", lambda e: self.finish())

    def put(self, s, tag="ok", nl=True):
        self.text.configure(state="normal")
        self.text.insert("end", s + ("\n" if nl else ""), tag)
        self.text.configure(state="disabled")
        self.text.see("end")

    def script(self):
        for ln in boot_lines(self.app):
            tag = "warn" if ln.startswith("WARNING") else ("hi" if ln.startswith("NEXUS") else "ok")
            self.put(ln, tag)
            yield random.choice([0.02, 0.03, 0.05, 0.09, 0.16])
        yield 0.3
        self.put("")
        for row in _logo():
            self.put("   " + row, "acc")
            yield 0.05
        self.put("")
        self.put("   ESTABLISHING SECURE UPLINK", "hi")
        for i in range(31):
            n = i
            self.text.configure(state="normal")
            self.text.delete("end-1c linestart", "end-1c")
            self.text.insert("end-1c", "   [" + "█" * n + "░" * (30 - n) + "] %3d%%" % int(i / 30.0 * 100), "ok")
            self.text.configure(state="disabled")
            yield 0.04
        self.put("")
        self.put("")
        self.put("   LOGIN: ghost", "ok")
        self.put("   PASSPHRASE: ", "ok", nl=False)
        for _ in range(14):
            self.put("*", "hi", nl=False)
            yield 0.07
        self.put("")
        yield 0.5
        self.put("")
        self.put("   >>> ACCESS GRANTED <<<", "hi")
        yield 0.9

    def finish(self):
        if self.done:
            return
        self.done = True
        self.runner.cancel()
        self.place_forget()
        self.app.boot_done()


# ════════════════════════════════════════════════════════════════════
#  APLICACIÓN
# ════════════════════════════════════════════════════════════════════
class App:
    def __init__(self, root, selftest=False):
        self.root = root
        self.selftest = selftest
        self.start = time.time()
        self.paused = True
        self.alarm_on = False
        self.fullscreen = False
        self.muted = False
        self.crack_job = None
        self.event_count = 0
        self.events = collections.deque(maxlen=300)
        self.errors = []
        self._err_seen = set()
        init_ui(root)
        self.stats = Stats()
        self.mission = Mission(self)
        self.net = NetIntel(self, enabled=not (selftest or '--offline' in sys.argv))
        self.cfg = Config(None if selftest else CFG_PATH)
        self.xp = int(self.cfg.get("xp") or 0)
        self.cmd_count = 0
        self.contract = None
        self._last_cmd = ("", 0.0)
        self._flags = dict(trace_hi=False, bat=False, up=None, err="", bat_t=0.0)
        self.next_event = time.time() + random.uniform(40, 90)
        self.voice = Voice(self, self.cfg)
        self.nova = Nova(self, self.voice, self.cfg)
        root.title("NEXUS // GHOSTWIRE")
        root.configure(bg=T.bg)
        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        w, h = int(sw * 0.92), int(sh * 0.9)
        root.geometry("%dx%d+%d+%d" % (w, h, (sw - w) // 2, (sh - h) // 2 - 10))
        root.minsize(900, 600)
        self.build()
        self.banner_w = Banner(root)
        self.matrix_w = MatrixOverlay(root)
        T.subs.append(lambda: root.configure(bg=T.bg))
        root.bind("<F11>", lambda e: self.toggle_fullscreen())
        root.bind("<Escape>", lambda e: self.set_fullscreen(False))
        root.bind("<F2>", lambda e: self.cycle_theme())
        root.bind("<F3>", lambda e: self.alarm("INTRUSION DETECTED", "COUNTERMEASURES ACTIVE"))
        root.bind("<F4>", lambda e: self.term.run_line("hack"))
        root.bind("<F1>", lambda e: self.term.run_line("help"))
        root.bind("<F5>", lambda e: self.term.run_line("breach"))
        root.bind("<F6>", lambda e: self.term.run_line("nexus" if self.term.mode == "win" else "win") if self.term.mode in ("nexus", "win") else None)
        root.bind("<F7>", lambda e: self.term.run_line("voz off" if self.voice.enabled else "voz on") if self.term.mode == "nexus" else self.toggle_voice())
        root.bind("<F8>", lambda e: self.matrix_w.start(8.0, []))
        root.bind("<Key>", self.on_key)
        root.protocol("WM_DELETE_WINDOW", self.quit)
        self.boot = None
        for _ in range(6):
            self.log(random.choice(["INFO", "OK", "INFO"]), "System boot sequence logged")
        if selftest:
            self.boot_done()
            root.after(800, self._selftest_step)
        else:
            self.boot = Boot(self)
        self.tick()

    # ---- layout ----
    def build(self):
        r = self.root
        r.grid_rowconfigure(1, weight=1)
        r.grid_columnconfigure(0, weight=1)
        self.header = Header(r, self, "")
        self.header.configure(height=58)
        self.header.grid(row=0, column=0, sticky="ew")
        body = tk.Frame(r, bg=T.bg)
        body.grid(row=1, column=0, sticky="nsew", padx=3, pady=(2, 2))
        foot = Footer(r, self, "")
        foot.configure(height=24)
        foot.grid(row=2, column=0, sticky="ew")
        T.subs.append(lambda: body.configure(bg=T.bg))
        weights = (22, 34, 22, 22)
        cols = []
        for i, wt in enumerate(weights):
            f = tk.Frame(body, bg=T.bg)
            f.grid(row=0, column=i, sticky="nsew", padx=2)
            body.grid_columnconfigure(i, weight=wt, minsize=60)
            T.subs.append(lambda f=f: f.configure(bg=T.bg))
            cols.append(f)
        body.grid_rowconfigure(0, weight=1)

        def stack(frame, items):
            for i, (widget, wt) in enumerate(items):
                widget.grid(row=i, column=0, sticky="nsew", pady=2)
                frame.grid_rowconfigure(i, weight=wt, minsize=40)
            frame.grid_columnconfigure(0, weight=1)

        self.rain = RainPanel(cols[0], self)
        self.hexp = HexPanel(cols[0], self)
        self.crack = CrackPanel(cols[0], self)
        self.cvep = CvePanel(cols[0], self)
        stack(cols[0], [(self.rain, 16), (self.hexp, 16), (self.crack, 26), (self.cvep, 30)])
        self.globe = GlobePanel(cols[1], self)
        self.spec = SpectrumPanel(cols[1], self)
        self.novap = NovaPanel(cols[1], self)
        self.term = Terminal(cols[1], self)
        stack(cols[1], [(self.globe, 46), (self.spec, 11), (self.novap, 12), (self.term, 40)])
        self.radar = RadarPanel(cols[2], self)
        self.topo = TopoPanel(cols[2], self)
        self.core = CorePanel(cols[2], self)
        stack(cols[2], [(self.radar, 30), (self.topo, 30), (self.core, 28)])
        self.sys = SysPanel(cols[3], self)
        self.netp = NetPanel(cols[3], self)
        self.proc = ProcPanel(cols[3], self)
        self.logp = LogPanel(cols[3], self)
        self.missp = MissionPanel(cols[3], self)
        stack(cols[3], [(self.sys, 20), (self.netp, 26), (self.proc, 15), (self.logp, 19), (self.missp, 22)])

    def boot_done(self):
        self.paused = False
        self.term.runner.start(self._intro_job(), self.term._finish)
        try:
            if self.voice.enabled:
                self.voice.say(self.nova.boot_text(), 2)
        except Exception:
            pass

    def _intro_job(self):
        self.term.busy = True
        yield from self.term.intro()

    # ---- bucle ----
    def tick(self):
        if not self.paused:
            for step in (self._tick_net, self.stats.update, self.mission.update,
                         lambda: self.auto_log() if random.random() < 0.28 else None,
                         self._tick_events, self._tick_watch):
                try:
                    step()
                except Exception:
                    key = ("tick", traceback.format_exc().splitlines()[-1])
                    if key not in self._err_seen:
                        self._err_seen.add(key)
                        self.errors.append(key)
                        traceback.print_exc()
        try:
            self.root.after(100, self.tick)
        except tk.TclError:
            pass

    def _tick_net(self):
        if self.net.pub_new:
            self.net.pub_new = False
            self.apply_home()

    def _tick_events(self):
        now = time.time()
        if now < self.next_event:
            return
        self.next_event = now + random.uniform(45, 110)
        lvl, tpl, dtr, narr = random.choice(EVENTS)
        d = dict(ip=rip(), host=random.choice(TARGETS), n=random.randint(1000, 9999), hx=rhex(4))
        self.log(lvl, tpl.format(**d))
        self.mission.trace = max(0, min(99, self.mission.trace + dtr))
        if narr:
            self.nova.narrate("event", prio=1, text=narr.format(**d))

    def _tick_watch(self):
        m, f, now = self.mission, self._flags, time.time()
        if m.trace > 72 and not f["trace_hi"]:
            f["trace_hi"] = True
            self.nova.narrate("trace_high", prio=2)
        elif m.trace < 50:
            f["trace_hi"] = False
        o = self.net.online
        if f["up"] is not None and o is not None and o != f["up"]:
            self.nova.narrate("uplink_back" if o else "uplink_lost", prio=2)
        if o is not None:
            f["up"] = o
        if now - f["bat_t"] > 30:
            f["bat_t"] = now
            b = REAL.battery()
            if b and not b[1] and b[0] <= 20:
                if not f["bat"]:
                    f["bat"] = True
                    self.log("WARN", "Battery low: %d%%" % b[0])
                    self.nova.narrate("battery_low", prio=2, pct=b[0])
            else:
                f["bat"] = False
        v = self.voice
        if v.err != f["err"]:
            f["err"] = v.err
            if v.err:
                self.log("WARN", "Voice: %s" % v.err[:60])
                v.sub_text, v.sub_t = "Error de voz: " + v.err[:90], time.time()
        self.nova.tick()

    def rank_label(self):
        return "RANK %s %d XP%s" % (rank_info(self.xp)[1], self.xp, "  NOVA ON" if self.voice.enabled else "")

    def add_xp(self, n, why=None):
        if n <= 0:
            return
        old = rank_info(self.xp)[0]
        self.xp += int(n)
        self.cfg.set("xp", self.xp)
        idx, name, _ = rank_info(self.xp)
        if idx > old:
            self.banner("RANK UP", name, "ok", 3.5)
            self.log("OK", "Rank up: %s" % name)
            self.nova.narrate("rank_up", prio=2, rank=name)

    def note_command(self, cmd):
        now = time.time()
        self.cmd_count += 1
        last, t = self._last_cmd
        quiet = {"help", "clear", "theme", "status", "rank", "perfil", "voz", "voice", "nova", "win", "nexus", "briefing", "contract", "echo"}
        if (cmd != last or now - t > 20) and cmd not in quiet:
            self.add_xp(3)
        self._last_cmd = (cmd, now)
        c = self.contract
        if c and cmd in c["cmds"]:
            c["got"] += 1
            if c["got"] >= c["n"]:
                self.contract = None
                self.add_xp(c["xp"])
                self.banner("CONTRACT COMPLETE", "+%d XP  ::  %s" % (c["xp"], c["desc"]), "ok", 3.5)
                self.log("OK", "Contract fulfilled: %s" % c["desc"])
                self.nova.narrate("contract", prio=2)

    def toggle_voice(self):
        self.voice.set_enabled(not self.voice.enabled)
        self.log("INFO", "Nova voice %s" % ("ON" if self.voice.enabled else "OFF"))
        if self.voice.enabled:
            self.voice.say("Voz activada. Aquí estoy, %s." % self.nova.name, 2)

    def glitch(self, n=10):
        if self.alarm_on:
            return
        base = T.name
        seq = [random.choice(THEME_ORDER + ["BLOOD"]) for _ in range(n)]

        def step(i=0):
            if self.alarm_on:
                return
            if i >= len(seq):
                T.set(base)
                return
            T.set(seq[i])
            self.root.after(random.randint(40, 95), step, i + 1)
        step()

    def quit(self):
        try:
            self.cfg.save()
            self.voice.shutdown()
        except Exception:
            pass
        self.root.destroy()

    def apply_home(self):
        p = self.net.pub
        if p and p.get("lat") is not None:
            CITIES["HAV"] = (p["lat"], p["lon"], p.get("city") or "Home")
            self.globe.cv["HAV"] = vec(p["lat"], p["lon"])
            self.log("OK", "Geolocated home: %s, %s" % (p.get("city", "?"), p.get("country", "?")))

    def auto_log(self):
        lvl, tpl = random.choice(LOG_TEMPLATES)
        cs = random.sample(list(CITIES.values()), 3)
        msg = tpl.format(ip=rip(), ip2=rip(), p=random.choice([22, 443, 3389, 8080]), host=random.choice(TARGETS),
                         city=cs[0][2], city2=cs[1][2], city3=cs[2][2], n=random.randint(10, 9999), hx=rhex(6))
        self.log(lvl, msg)
        if lvl == "CRIT":
            self.mission.trace = min(99, self.mission.trace + random.uniform(0.5, 2))

    def log(self, lvl, msg):
        self.events.append((datetime.datetime.now().strftime("%H:%M:%S"), lvl, msg))
        self.event_count += 1

    # ---- efectos ----
    def banner(self, title, sub, tone="ok", secs=4.0):
        try:
            self.banner_w.show(title, sub, tone, secs)
        except Exception:
            pass
        self.beep([880, 1320] if tone == "ok" else [440, 330])

    def alarm(self, text="INTRUSION DETECTED", sub="COUNTERMEASURES ACTIVE", secs=7):
        if self.alarm_on:
            return
        try:
            self.nova.narrate("burned" if text.startswith("TRACE") else "alarm", prio=2)
        except Exception:
            pass
        self.alarm_on = True
        self.prev_theme = T.name
        T.set("BLOOD")
        self.banner_w.show(text, sub, "bad", secs)
        self.log("CRIT", "ALARM: %s" % text)
        self.beep([900, 600, 900, 600, 900, 600])
        self.root.after(int(secs * 1000), self._end_alarm)

    def _end_alarm(self):
        T.set(self.prev_theme if self.prev_theme in THEMES else "MATRIX")
        self.alarm_on = False
        self.log("OK", "Alarm cleared. Systems nominal.")

    def beep(self, freqs):
        if self.muted or self.selftest:
            return

        def play():
            try:
                import winsound
                for f in freqs:
                    winsound.Beep(f, 110)
            except Exception:
                pass
        try:
            import winsound  # noqa
            threading.Thread(target=play, daemon=True).start()
        except ImportError:
            try:
                self.root.bell()
            except tk.TclError:
                pass

    def cycle_theme(self):
        if self.alarm_on:
            return
        i = THEME_ORDER.index(T.name) if T.name in THEME_ORDER else -1
        T.set(THEME_ORDER[(i + 1) % len(THEME_ORDER)])

    def set_fullscreen(self, v):
        self.fullscreen = v
        self.root.attributes("-fullscreen", v)

    def toggle_fullscreen(self):
        self.set_fullscreen(not self.fullscreen)

    def toggle_matrix_off(self):
        if self.matrix_w.active:
            self.matrix_w.stop()
            return True
        return False

    def on_key(self, e):
        if self.boot and not self.boot.done:
            self.boot.finish()
            return
        if self.toggle_matrix_off():
            return "break"
        return self.term.on_key(e)

    def report_error(self, panel):
        key = (panel.__class__.__name__, traceback.format_exc().splitlines()[-1])
        if key not in self._err_seen:
            self._err_seen.add(key)
            self.errors.append(key)
            traceback.print_exc()

    # ---- autoprueba ----
    def _selftest_step(self):
        if not hasattr(self, "_st"):
            self._st = iter(["help", "scan", "trace", "hack", "hash abc", "crack " + md5("abc"), "crack " + md5("x9k2"),
                             "sysinfo", "netstat", "ls", "cat shadow.bak", "decrypt vault.enc", "vpn", "ghost",
                             "theme amber", "status", "lockdown", "clear", "coffee", "encrypt hola", "nikto", "tor", "hostinfo", "rank", "briefing",
                             "win cd", "disks", "voz estado"])
            self._st_t0 = time.time()
        if self.term.busy:
            if time.time() - self._st_t0 < 90:
                self.root.after(300, self._selftest_step)
                return
        cmd = next(self._st, None)
        if cmd is None:
            self.root.after(3000, self._selftest_end)
            return
        self.term.run_line(cmd)
        self.root.after(300, self._selftest_step)

    def _selftest_end(self):
        print("SELFTEST ERRORS:", self.errors if self.errors else "none")
        self.root.destroy()


def main():
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    root = tk.Tk()
    app = App(root, selftest="--selftest" in sys.argv)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass
    return 1 if (app.errors and app.selftest) else 0


if __name__ == "__main__":
    sys.exit(main())
