# User Journey Visualiser (UJV)

This tool generates a visual representation of a user journey from a simple markdown file.

## Markdown Format for User Journeys

The markdown file should be structured into `Persona` and `Events` sections. Each event can contain multiple `Capabilities`.

### 1. Persona

Start with a top-level heading for the persona:

```markdown
## Persona

[Persona Name]
```

Example:

```markdown
## Persona

Data Engineer
```

### 2. Events

Define events using a level 3 heading. Each event can have an optional description and an optional icon.

```markdown
### [Event Title]

[Event Description]
[Optional Icon (e.g., 🚀, 🔔, 🗄️, 🧹, 🏷️)]
```

Example:

```markdown
### Ingest raw data

Collect raw data from multiple sources (APIs, databases, files)
🗄️
```

### 3. Capabilities

Under each event, define capabilities using a level 4 heading. Each capability requires a title, description, and state. It can optionally include a link and an edge text.

```markdown
#### [Capability Title]

[Capability Description]
[State (e.g., Not started, In development, In testing, release candidate, In production)]
[Optional Link (URL)]
[Optional Edge Text (text displayed on the edge connecting event to capability)]
```

Example:

```markdown
#### Data ingestion pipeline

Automates data collection and storage
In production
https://github.com/org/data-ingest
Data Flow
```

- **State**: The state determines the color of the capability node. Supported states are: `Not started`, `In development`, `In testing, release candidate`, `In production`.
- **Link**: If provided, the link will be displayed as a Material 3 chip within the capability node. The capability node will also be clickable, navigating to this URL.
- **Edge Text**: If provided, this text will appear on the edge connecting the event node to the capability node. The edge will be an open line (no arrow).

## Example Markdown Structure

```markdown
# User Journey

## Persona

Data Engineer

## Events

### Ingest raw data

Collect raw data from multiple sources (APIs, databases, files)
🗄️

#### Data ingestion pipeline

Automates data collection and storage
In production
https://github.com/org/data-ingest
Data Flow

### Clean and validate data

Apply data quality checks and transformations
🧹

#### Data validation capability

Ensures data meets quality standards
In testing, release candidate
https://github.com/org/data-validate
Validation Check
```

## Usage

To generate the HTML visualization, run the `ujv_parser.py` script with your markdown file and an output HTML file:

```bash
python ujv_parser.py your_journey.md -o output_journey.html
```

Example:

```bash
python ujv_parser.py sample_data_engineer_journey.md -o data_engineer_journey.html
```

The generated HTML file will include a Mermaid.js flowchart styled with Google Material Web Components, featuring a dark theme, Material 3 card-like nodes, clickable capability links, and custom edge text.
