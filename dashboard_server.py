#!/usr/bin/env python3
"""
Novel Pipeline V4 - Dashboard
Web-basiertes Dashboard zum Monitoring der Pipeline
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import glob
import json
from datetime import datetime
from pathlib import Path

class DashboardHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/status':
            self.send_dashboard()
        elif self.path.startswith('/output'):
            super().do_GET()
        else:
            super().do_GET()
    
    def send_dashboard(self):
        html = self.generate_html()
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def generate_html(self):
        # Finde das neueste Output-Verzeichnis
        output_dirs = sorted(glob.glob("output_*"), reverse=True)
        current_output = output_dirs[0] if output_dirs else "output"
        
        # Log lesen
        log_content = ""
        log_file = Path(current_output) / "pipeline.log"
        if log_file.exists():
            log_content = log_file.read_text()
        
        # Dateien auflisten
        files = sorted(glob.glob(f"{current_output}/*.md"))
        kapitel_files = [f for f in files if "kapitel_" in f and "_v" not in f]
        
        # Phase ermitteln
        if "FERTIG!" in log_content:
            phase = "✅ FERTIG!"
            progress = 100
            status_class = "complete"
        elif "PHASE 6" in log_content:
            phase = "Phase 6: Gesamt-Check"
            progress = 95
            status_class = "running"
        elif "PHASE 5" in log_content:
            phase = "Phase 5: Flow-Check"
            progress = 85
            status_class = "running"
        elif "PHASE 3 & 4" in log_content:
            phase = f"Phase 3/4: Schreiben"
            progress = 30 + (len(kapitel_files) * 3)
            status_class = "running"
        elif "PHASE 2.5" in log_content:
            phase = "Phase 2.5: Kapitel-Gliederungen"
            progress = 20
            status_class = "running"
        elif "PHASE 2" in log_content:
            phase = "Phase 2: Akt-Gliederungen"
            progress = 15
            status_class = "running"
        elif "PHASE 1" in log_content:
            phase = "Phase 1: Grob-Gliederung"
            progress = 5
            status_class = "running"
        else:
            phase = "⏳ Warte auf Start..."
            progress = 0
            status_class = "waiting"
        
        # Dateien mit Infos
        file_items = ""
        total_words = 0
        for f in files:
            try:
                content = Path(f).read_text(encoding='utf-8', errors='replace')
                words = len(content.split())
                basename = os.path.basename(f)
                
                # Nur Hauptdateien (keine Versionen)
                if "_v0" in basename:
                    continue
                    
                if "kapitel_" in f and "_v" not in f:
                    total_words += words
                elif "ROMAN_KOMPLETT" in f:
                    total_words = words
                    
                icon = "📖" if "kapitel" in f else "📋" if "akt" in f else "📚" if "ROMAN" in f else "📄"
                file_items += f'''<div class="file-item">
                    <span class="icon">{icon}</span>
                    <a href="/{f}" target="_blank">{basename}</a>
                    <span class="meta">{words:,} Wörter</span>
                </div>'''
            except:
                pass
        
        # Log (letzte Zeilen)
        log_lines = log_content.strip().split('\n')[-30:]
        log_html = '\n'.join(log_lines)
        
        updated = datetime.now().strftime("%H:%M:%S")
        
        return f'''<!DOCTYPE html>
<html><head>
<meta charset="UTF-8">
<title>Novel Pipeline V4</title>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ 
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace;
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    color: #eee;
    min-height: 100vh;
    padding: 20px;
}}
.container {{ max-width: 1200px; margin: 0 auto; }}
h1 {{ 
    color: #e94560;
    font-size: 2em;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 15px;
}}
.badge {{ 
    background: #e94560; 
    padding: 4px 12px; 
    border-radius: 20px; 
    font-size: 0.5em;
    font-weight: normal;
}}
.card {{
    background: rgba(22, 33, 62, 0.8);
    backdrop-filter: blur(10px);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 20px;
    border: 1px solid rgba(233, 69, 96, 0.2);
}}
.status-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}}
.phase {{ font-size: 1.4em; color: #e94560; font-weight: bold; }}
.time {{ color: #888; font-size: 0.9em; }}
.progress-container {{
    background: #0f3460;
    border-radius: 25px;
    height: 40px;
    overflow: hidden;
    position: relative;
}}
.progress-bar {{
    height: 100%;
    border-radius: 25px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    font-size: 1em;
    transition: width 0.5s ease;
    background: linear-gradient(90deg, #4CAF50, #8BC34A);
}}
.progress-bar.running {{
    background: linear-gradient(90deg, #2196F3, #03A9F4);
    animation: pulse 2s infinite;
}}
.progress-bar.waiting {{
    background: #555;
}}
@keyframes pulse {{
    0%, 100% {{ opacity: 1; }}
    50% {{ opacity: 0.7; }}
}}
.stats {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 20px;
    text-align: center;
}}
.stat-box {{
    background: rgba(15, 52, 96, 0.5);
    padding: 20px;
    border-radius: 12px;
}}
.stat-value {{ font-size: 2.5em; color: #4CAF50; font-weight: bold; }}
.stat-label {{ color: #888; font-size: 0.9em; margin-top: 8px; }}
.files-grid {{ 
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 10px;
}}
.file-item {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
    background: rgba(15, 52, 96, 0.3);
    border-radius: 8px;
    transition: background 0.2s;
}}
.file-item:hover {{ background: rgba(15, 52, 96, 0.6); }}
.file-item .icon {{ font-size: 1.3em; }}
.file-item a {{ color: #4CAF50; text-decoration: none; flex: 1; }}
.file-item a:hover {{ text-decoration: underline; }}
.file-item .meta {{ color: #666; font-size: 0.85em; }}
.log-box {{
    background: #0a0a0a;
    border-radius: 10px;
    padding: 20px;
    font-family: "Fira Code", "Monaco", monospace;
    font-size: 0.85em;
    color: #0f0;
    max-height: 400px;
    overflow-y: auto;
    white-space: pre-wrap;
    line-height: 1.6;
}}
h3 {{ color: #e94560; margin-bottom: 20px; font-size: 1.2em; }}
.refresh-note {{ color: #555; font-size: 0.85em; text-align: center; margin-top: 25px; }}
.output-dir {{ color: #888; font-size: 0.9em; margin-bottom: 20px; }}
</style>
<script>
setTimeout(() => location.reload(), 5000);
</script>
</head>
<body>
<div class="container">
<h1>📖 Novel Pipeline <span class="badge">V4</span></h1>
<p class="output-dir">📁 {current_output}</p>

<div class="card">
<div class="status-header">
<span class="phase">{phase}</span>
<span class="time">🕐 {updated}</span>
</div>
<div class="progress-container">
<div class="progress-bar {status_class}" style="width: {min(progress, 100)}%">{progress}%</div>
</div>
</div>

<div class="card">
<div class="stats">
<div class="stat-box">
<div class="stat-value">{len(kapitel_files)}</div>
<div class="stat-label">Kapitel</div>
</div>
<div class="stat-box">
<div class="stat-value">{total_words:,}</div>
<div class="stat-label">Wörter</div>
</div>
<div class="stat-box">
<div class="stat-value">{len(files)}</div>
<div class="stat-label">Dateien</div>
</div>
<div class="stat-box">
<div class="stat-value">{len(output_dirs)}</div>
<div class="stat-label">Runs</div>
</div>
</div>
</div>

<div class="card">
<h3>📁 Dateien</h3>
<div class="files-grid">
{file_items if file_items else '<div class="file-item"><span style="color:#666">Noch keine Dateien...</span></div>'}
</div>
</div>

<div class="card">
<h3>📜 Log</h3>
<div class="log-box">{log_html if log_html else "Warte auf Pipeline-Start..."}</div>
</div>

<p class="refresh-note">Auto-refresh alle 5 Sekunden</p>
</div>
</body></html>'''

if __name__ == '__main__':
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8888
    
    os.chdir(Path(__file__).parent)
    
    print(f"🌐 Dashboard: http://localhost:{port}/")
    print(f"   (oder http://<mac-studio-ip>:{port}/ im Netzwerk)")
    print("   Ctrl+C zum Beenden")
    
    HTTPServer(('0.0.0.0', port), DashboardHandler).serve_forever()
