import re
import sys
import os
from pathlib import Path
import argparse
import json

TEMPLATE_HTML = """
<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>User Journey</title>
    <script src=\"https://cdn.jsdelivr.net/npm/mermaid@10.9.0/dist/mermaid.min.js\"></script>
    <link href=\"https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap\" rel=\"stylesheet\">
    <link rel=\"stylesheet\" href=\"https://unpkg.com/material-components-web@latest/dist/material-components-web.min.css\">
    <script src=\"https://unpkg.com/material-components-web@latest/dist/material-components-web.min.js\"></script>
    <style>
        body {{ font-family: 'Roboto', sans-serif; margin: 0; padding: 0; background-color: #121212; color: #ffffff; }}
        .container {{ max-width: 1100px; margin: 2rem auto; background: #1e1e1e; border-radius: 8px; padding: 2rem; box-shadow: 0 8px 16px rgba(0,0,0,0.3); }}
        h1 {{ text-align: center; color: #ffffff; font-weight: 500; }}
        .persona {{ font-size: 1.5rem; font-weight: bold; margin-bottom: 1.5rem; text-align: center; color: #bb86fc; }}
        #download-container {{ text-align: center; margin-top: 2rem; }}
        .mdc-button--raised {{ background-color: #6200ee; }}
        .mermaid-chip {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 16px;
            background-color: #424242;
            color: #ffffff;
            font-size: 0.8em;
            margin-top: 5px;
            white-space: nowrap;
        }}
    </style>
</head>
<body>
    <div class=\"container\">
        <h1>User Journey</h1>
        <div class=\"persona\">Persona: {persona}</div>
        <div class=\"mermaid\" id=\"ujv-diagram\">
{mermaid_code}
        </div>
        <div id=\"download-container\">
            <button class=\"mdc-button mdc-button--raised\" id=\"download-btn\">
                <span class=\"mdc-button__label\">Download as SVG</span>
            </button>
        </div>
    </div>
    <script>
                mermaid.initialize({{ startOnLoad: true, theme: 'dark' }});
        mdc.autoInit();
        document.addEventListener('DOMContentLoaded', function() {{
            const downloadBtn = document.getElementById('download-btn');
            if(downloadBtn) {{
                mdc.ripple.MDCRipple.attachTo(downloadBtn);
                downloadBtn.addEventListener('click', function() {{
                    const svg = document.querySelector('#ujv-diagram svg');
                    if (svg) {{
                        const serializer = new XMLSerializer();
                        const source = serializer.serializeToString(svg);
                        const blob = new Blob([source], {{type: 'image/svg+xml;charset=utf-8'}});
                        const url = URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = 'user_journey.svg';
                        document.body.appendChild(a);
                        a.click();
                        document.body.removeChild(a);
                        URL.revokeObjectURL(url);
                    }}
                }});
            }}
        }});
    </script>
</body>
</html>
"""

# Color mapping for capability states
STATE_COLORS = {
    'Not started':                  {'fill': '#CF6679', 'color': '#000000'},
    'In development':               {'fill': '#FFD54F', 'color': '#000000'},
    'In testing, release candidate':{'fill': '#81C784', 'color': '#000000'},
    'In production':                {'fill': '#64B5F6', 'color': '#000000'},
}


def parse_markdown(md_text):
    """
    Parses the markdown file and returns a dict with persona, events, and capabilities.
    """
    lines = md_text.splitlines()
    persona = None
    events = []
    current_event = None
    current_cap = None
    mode = None
    for line in lines:
        line = line.strip()
        if line.startswith('## Persona'):
            mode = 'persona'
            continue
        if line.startswith('## Events'):
            mode = 'events'
            continue
        if line.startswith('### '):
            if current_event:
                events.append(current_event)
            current_event = {
                'title': line[4:].strip(),
                'description': '',
                'icon': None,
                'capabilities': []
            }
            mode = 'event_desc'
            continue
        if line.startswith('#### '):
            if current_cap:
                current_event['capabilities'].append(current_cap)
            current_cap = {
                'title': line[5:].strip(),
                'description': '',
                'state': '',
                'link': '',
                'edge_text': ''
            }
            mode = 'cap_desc'
            continue
        # Data lines
        if mode == 'persona' and line:
            persona = line
            mode = None
        elif mode == 'event_desc' and line:
            if not current_event['description']:
                current_event['description'] = line
            elif not current_event['icon']:
                current_event['icon'] = line
            # else: ignore extra lines
        elif mode == 'cap_desc' and line:
            if not current_cap['description']:
                current_cap['description'] = line
            elif not current_cap['state']:
                current_cap['state'] = line
            elif not current_cap['link']:
                current_cap['link'] = line
            elif not current_cap['edge_text']:
                current_cap['edge_text'] = line
    # Flush last event/capability
    if current_cap and current_event:
        current_event['capabilities'].append(current_cap)
    if current_event:
        events.append(current_event)
    return {
        'persona': persona,
        'events': events
    }

CAPABILITIES_DIR = Path("capabilities")

def expand_capability_references(md_text: str) -> str:
    """
    Expands [capability:filename_stem] references in markdown text
    by reading content from the capabilities directory.
    """
    expanded_md = []
    for line in md_text.splitlines():
        match = re.search(r'\[capability:([a-zA-Z0-9_-]+)\]', line)
        if match:
            capability_stem = match.group(1)
            capability_filepath = CAPABILITIES_DIR / f"{capability_stem}.md"
            if capability_filepath.exists():
                with open(capability_filepath, 'r', encoding='utf-8') as f:
                    expanded_md.append(f.read())
            else:
                expanded_md.append(f"[ERROR: Capability '{capability_stem}' not found]")
        else:
            expanded_md.append(line)
    return '\n'.join(expanded_md)

def escape_mermaid(text):
    return text.replace('"', '\"').replace("'", "\'").replace("[", "\\[").replace("]", "\\]")

def build_mermaid(parsed):
    """
    Build a Mermaid flowchart from parsed data.
    """
    events = parsed['events']
    nodes = []
    edges = []
    cap_nodes = []
    cap_edges = []
    mermaid_styles = []
    mermaid_links = []

    for idx, event in enumerate(events):
        eid = f"E{idx}"
        desc = escape_mermaid(event['description'])
        label = f"<b><span style='font-size: 20px;'>{event['title']}</span></b><br>{desc}"
        if event['icon']:
            label = f"{event['icon']} {label}"
        nodes.append(f'{eid}(["{label}"]):::event_card')
        if idx > 0:
            edges.append(f"E{idx-1} --> {eid}")
        for cidx, cap in enumerate(event['capabilities']):
            cid = f"{eid}_C{cidx}"
            state = cap.get('state', '')
            cap_label = f"<b>Capability</b><br>{cap['title']}<br>{escape_mermaid(cap['description'])}"
            if cap.get('link'):
                cap_label += f"<br><div class='mermaid-chip'>{cap['link']}</div>"
            
            cap_nodes.append(f'{cid}(["{cap_label}"])')
            edge_text = cap.get('edge_text', '').strip()
            if edge_text:
                cap_edges.append(f'{eid} -- "{edge_text}" --- {cid}')
            else:
                cap_edges.append(f'{eid} --- {cid}')

            if cap.get('link'):
                link_url = cap['link']
                mermaid_links.append(f'click {cid} "{link_url}"')


            if state in STATE_COLORS:
                colors = STATE_COLORS[state]
                fill_color = colors['fill']
                text_color = colors['color']
                mermaid_styles.append(f"style {cid} fill:{fill_color},stroke:#333,color:{text_color},stroke-width:2px,rx:8px,ry:8px,font-size:18px")

    # Mermaid code
    mermaid = ["flowchart TD"]
    mermaid.extend(nodes)
    mermaid.extend(edges)
    mermaid.extend(cap_nodes)
    mermaid.extend(cap_edges)
    mermaid.extend(mermaid_styles)
    mermaid.extend(mermaid_links)
    mermaid.append("classDef event_card fill:#2D2D2D,stroke:#444,stroke-width:2px,rx:8px,ry:8px,font-size:18px;")
    return '\n'.join(mermaid)

def main():
    parser = argparse.ArgumentParser(description='User Journey Visualiser: Markdown to Flowchart HTML')
    parser.add_argument('input_md', help='Input markdown file describing user journey')
    args = parser.parse_args()

    OUTPUT_DIR = Path("output")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    input_path = Path(args.input_md)
    output_filename = input_path.stem + ".html"
    output_filepath = OUTPUT_DIR / output_filename

    with open(args.input_md, 'r', encoding='utf-8') as f:
        md = f.read()

    expanded_md = expand_capability_references(md)
    parsed = parse_markdown(expanded_md)
    mermaid_code = build_mermaid(parsed)
    html = TEMPLATE_HTML.format(persona=parsed['persona'] or '', mermaid_code=mermaid_code)

    with open(output_filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"User journey visualisation written to {output_filepath}")

if __name__ == '__main__':
    main()
