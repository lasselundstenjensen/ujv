import argparse
import re
import os
from pathlib import Path

# Define the directory where capability markdown files are expected
CAPABILITIES_DIR = Path("capabilities")

# Define allowed states for capabilities
ALLOWED_CAPABILITY_STATES = {
    "Not started",
    "In development",
    "In testing, release candidate",
    "In production"
}

def validate_capability_file(filepath: Path) -> list[str]:
    """
    Validates the structure and content of a single capability markdown file.
    Checks for:
    - Top-level heading (####)
    - Presence of description, state, and optional link/edge text
    - Valid capability state
    - No unexpected lines
    """
    print('Validating capability file: ' + str(filepath))

    errors = []
    content = filepath.read_text(encoding='utf-8').splitlines()

    if not content:
        errors.append(f"Error in {filepath}: File is empty.")
        return errors

    # Use an iterator to consume lines and skip empty ones
    line_iter = iter(enumerate(content))

    # Line 0: Title (####)
    try:
        idx, line = next(line_iter)
        if not line.strip().startswith("####"):
            errors.append(f"Error in {filepath}: First line must be a level 4 heading (#### Capability Title).")
    except StopIteration:
        errors.append(f"Error in {filepath}: Missing capability title.")
        return errors

    # Find Description (first non-empty line after title)
    description_found = False
    for idx, line in line_iter:
        stripped_line = line.strip()
        if stripped_line:
            description_found = True
            break
    if not description_found:
        errors.append(f"Error in {filepath}: Missing capability description.")
        return errors

    # Find State (first non-empty line after description, starting with '[State:')
    state_found = False
    for idx, line in line_iter:
        stripped_line = line.strip()
        if stripped_line:
            # State is expected as a direct value on a line
            state_value = stripped_line
            if state_value in ALLOWED_CAPABILITY_STATES:
                state_found = True
            else:
                errors.append(f"Error in {filepath}: Invalid capability state '{state_value}'. Allowed states are: {', '.join(ALLOWED_CAPABILITY_STATES)}.")
            break
    if not state_found:
        errors.append(f"Error in {filepath}: Missing capability state.")
        return errors

    # Check for optional Link and Edge Text, and then unexpected content
    # Link (optional, first non-empty line after state, if it's a URL or link format)
    # Edge Text (optional, first non-empty line after link, if it's plain text)
    
    # Collect all remaining non-empty lines
    remaining_non_empty_lines = [line.strip() for idx, line in line_iter if line.strip()]

    # We expect at most 2 more lines (link and edge text)
    if len(remaining_non_empty_lines) > 2:
        errors.append(f"Error in {filepath}: Too many non-empty lines after state. Expected at most 2 additional lines (Link, Edge Text).")
    
    return errors

def validate_main_markdown(filepath: Path) -> list[str]:
    """
    Validates the structure and content of the main user journey markdown file.
    Checks for:
    - Overall section order (Persona, Events)
    - Event structure (### heading, description, icon)
    - Capability references ([capability:filename_stem])
    - Existence of referenced capability files
    """
    errors = []
    md_text = filepath.read_text(encoding='utf-8')
    lines = md_text.splitlines()

    current_section = None
    event_count = 0
    
    # State machine for parsing sections
    for i, line in enumerate(lines):
        stripped_line = line.strip()

        if stripped_line.startswith("# User Journey"):
            if current_section is not None:
                errors.append(f"Error in {filepath} (line {i+1}): '# User Journey' heading found out of place.")
            current_section = "journey_title"
            continue
        elif stripped_line.startswith("## Persona"):
            if current_section not in [None, "journey_title"]:
                errors.append(f"Error in {filepath} (line {i+1}): '## Persona' heading found out of order.")
            current_section = "persona"
            continue
        elif stripped_line.startswith("## Events"):
            if current_section not in ["persona"]:
                errors.append(f"Error in {filepath} (line {i+1}): '## Events' heading found out of order (expected after Persona).")
            current_section = "events_section"
            continue
        elif stripped_line.startswith("### "): # Event title
            if current_section != "events_section":
                errors.append(f"Error in {filepath} (line {i+1}): Event heading (###) found outside 'Events' section.")
            event_count += 1
            
            # Validate the content immediately following the event title
            # Expected sequence of non-empty lines: Description, Icon, [capability:reference]
            
            current_line_idx = i + 1
            non_empty_lines_after_event_title = []

            # Collect all non-empty lines until next heading or capability reference
            while current_line_idx < len(lines):
                stripped_line_after_event = lines[current_line_idx].strip()
                if stripped_line_after_event.startswith(tuple(["#"])) or re.search(r'\[capability:([a-zA-Z0-9_-]+)\]', stripped_line_after_event):
                    break
                if stripped_line_after_event:
                    non_empty_lines_after_event_title.append(stripped_line_after_event)
                current_line_idx += 1
            
            # Check for Description
            if not non_empty_lines_after_event_title:
                errors.append(f"Error in {filepath} (line {i+1}): Event '{stripped_line[4:]}' is missing a description.")
            else:
                # Description is the first non-empty line
                description = non_empty_lines_after_event_title[0]
                
                # Description is always the first non-empty line
                description = non_empty_lines_after_event_title[0]

                # Check for Icon and Capability Reference based on the number of non-empty lines
                if len(non_empty_lines_after_event_title) == 1:
                    # Valid: only description is present (icon and capability reference are optional)
                    pass
                elif len(non_empty_lines_after_event_title) == 2:
                    # Could be (description, icon) OR (description, capability_ref)
                    second_line = non_empty_lines_after_event_title[1]
                    is_icon = re.match(r'^[\U0001F000-\U0001F9FF\U00002600-\U000026FF\U00002700-\U000027BF]\U0000FE0F?$', second_line)
                    is_capability_ref = re.search(r'\[capability:([a-zA-Z0-9_-]+)\]', second_line)

                    if is_icon and is_capability_ref:
                        errors.append(f"Error in {filepath} (line {i+1}): Event '{stripped_line[4:]}' has a line that appears to be both an icon and a capability reference. This is unexpected.")
                    elif is_icon:
                        # Valid: description, icon
                        pass
                    elif is_capability_ref:
                        # Valid: description, capability_ref (icon was optional and skipped)
                        pass
                    else:
                        errors.append(f"Error in {filepath} (line {i+1}): Event '{stripped_line[4:]}' has unexpected content after description. Expected an optional icon or capability reference.")
                elif len(non_empty_lines_after_event_title) == 3:
                    # Must be (description, icon, capability_ref)
                    second_line = non_empty_lines_after_event_title[1]
                    third_line = non_empty_lines_after_event_title[2]

                    is_icon = re.match(r'^[\U0001F000-\U0001F9FF\U00002600-\U000026FF\U00002700-\U000027BF]\U0000FE0F?$', second_line)
                    is_capability_ref = re.search(r'\[capability:([a-zA-Z0-9_-]+)\]', third_line)

                    if not is_icon:
                        errors.append(f"Error in {filepath} (line {i+1}): Event '{stripped_line[4:]}' has content where an icon was expected, but it's not a valid icon.")
                    if not is_capability_ref:
                        errors.append(f"Error in {filepath} (line {i+1}): Event '{stripped_line[4:]}' has content where a capability reference was expected, but it's not a valid reference.")
                else:
                    # More than 3 non-empty lines
                    errors.append(f"Error in {filepath} (line {i+1}): Event '{stripped_line[4:]}' has too many non-empty lines. Expected at most 3 (description, optional icon, optional capability reference).")

            continue
        elif stripped_line.startswith("#### "): # This should not appear in main markdown anymore
            errors.append(f"Error in {filepath} (line {i+1}): Direct capability definition (####) found in main markdown. Use [capability:filename_stem] instead.")
            continue
        
        # Check for capability references
        match = re.search(r'\[capability:([a-zA-Z0-9_-]+)\]', stripped_line)
        if match:
            capability_stem = match.group(1)
            capability_filepath = filepath.parent / CAPABILITIES_DIR / f"{capability_stem}.md"
            if not capability_filepath.exists():
                errors.append(f"Error in {filepath} (line {i+1}): Referenced capability file '{capability_filepath}' not found.")
            else:
                # Recursively validate the referenced capability file
                errors.extend(validate_capability_file(capability_filepath))

    if current_section is None:
        errors.append(f"Error in {filepath}: No main sections (Persona, Events) found.")
    elif current_section == "persona" and event_count == 0:
        errors.append(f"Error in {filepath}: 'Events' section is missing or empty after 'Persona'.")

    return errors

def main():
    parser = argparse.ArgumentParser(description="Validate user journey markdown files.")
    parser.add_argument("markdown_file", type=str, help="Path to the main user journey markdown file.")
    args = parser.parse_args()

    markdown_path = Path(args.markdown_file)

    if not markdown_path.exists():
        print(f"Error: File not found at {markdown_path}")
        return

    print(f"Validating {markdown_path}...")
    errors = validate_main_markdown(markdown_path)

    if errors:
        print("\nValidation FAILED with the following issues:")
        for error in errors:
            print(f"- {error}")
    else:
        print("\nValidation SUCCESS: Markdown file structure and referenced capabilities are valid.")

if __name__ == "__main__":
    main()