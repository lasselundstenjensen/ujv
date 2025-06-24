# User Journey Visualiser (UJV)

This tool parses a markdown description of a user journey and generates a beautiful, interactive flowchart visualisation (HTML+SVG) for teams building large platforms.

## Features
- Parse journeys with personas, events, and capabilities from markdown
- Render as a flowchart (using Mermaid.js)
- Each event is a node with title, description, and optional icon
- Capabilities are shown as colored badges (state: Not started, In development, In testing, In production)
- Persona is shown at the top
- Download the SVG visualisation

## Usage

1. Write your user journey in markdown (see format below).
2. Run the parser to generate the HTML visualisation:

```bash
python ujv_parser.py your_journey.md -o user_journey.html
```

```bash
python ujv_parser.py sample_data_engineer_journey.md -o data_engineer_journey.html
```

3. Open `user_journey.html` in your browser. Click the download button to save as SVG.

## Markdown Format Example

```
# User Journey

## Persona

Data Scientist

## Events

### Select dataset

User selects a dataset using Databricks
🗂️

#### Data access capability

Allows reading data from Databricks
Not started
https://github.com/org/data-access

### Train model

User trains the model
🤖

#### Training capability

Enables model training
In development
https://github.com/org/model-train
```

- Icons are optional (use emoji or unicode icons)
- Capabilities can have a link to source code (optional)

## Requirements
- Python 3.7+
- No external dependencies required

## Customisation
- Mermaid.js is loaded from CDN (see HTML template in `ujv_parser.py`)
- You can adjust styles in the HTML template

---
