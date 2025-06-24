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

### Clean and validate data

Apply data quality checks and transformations
🧹

#### Data validation capability

Ensures data meets quality standards
In testing, release candidate
https://github.com/org/data-validate

### Enrich data with metadata

Add business and technical metadata to datasets
🏷️

#### Metadata enrichment

Tags datasets for discoverability
In development
https://github.com/org/metadata-enrich

### Publish data product

Make curated datasets available for downstream users
🚀

#### Data catalog integration

Registers data product in catalog
Not started
https://github.com/org/data-catalog

#### Access control

Manages permissions for data product usage
Not started
https://github.com/org/data-access

### Notify ML team

Alert ML engineers that new data products are ready for use in Databricks
🔔

#### Notification service

Sends automated alerts to ML team
In production
https://github.com/org/notify-ml
