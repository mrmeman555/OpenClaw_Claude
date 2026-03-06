#!/usr/bin/env python3
"""
Transcript Processor for Mimir's Workspace

Takes a Cowork/Claude Code transcript export (zip or directory) and produces:
1. A clean markdown transcript (human-readable conversation)
2. A metadata header with session info
3. Files it into .context/transcripts/ with a date-based name

Usage:
    python process_transcript.py <path_to_zip_or_dir> [--output-dir <dir>]

If --output-dir is not specified, outputs to .context/transcripts/ relative to
the script's grandparent directory (assumes script lives in .context/tools/).
"""

import json
import sys
import os
import zipfile
import tempfile
import re
from datetime import datetime, timezone
from pathlib import Path


def find_files(source_path):
    """Find the JSONL and metadata files from a zip or directory."""
    source = Path(source_path)

    if source.suffix == '.zip':
        tmpdir = tempfile.mkdtemp()
        with zipfile.ZipFile(source, 'r') as z:
            z.extractall(tmpdir)
        source = Path(tmpdir)

    # Find metadata.json
    metadata_file = None
    jsonl_file = None

    for f in source.rglob('metadata.json'):
        metadata_file = f
        break

    for f in source.rglob('*.jsonl'):
        jsonl_file = f
        break

    return jsonl_file, metadata_file


def parse_metadata(metadata_file):
    """Extract useful session metadata."""
    with open(metadata_file) as f:
        meta = json.load(f)

    created = meta.get('createdAt', 0)
    last_activity = meta.get('lastActivityAt', 0)

    # Convert epoch ms to datetime
    created_dt = datetime.fromtimestamp(created / 1000, tz=timezone.utc) if created else None
    last_dt = datetime.fromtimestamp(last_activity / 1000, tz=timezone.utc) if last_activity else None

    return {
        'session_id': meta.get('cliSessionId', 'unknown'),
        'title': meta.get('title', 'Untitled Session'),
        'model': meta.get('model', 'unknown'),
        'created': created_dt,
        'last_activity': last_dt,
        'process': meta.get('processName', ''),
    }


def extract_text_content(content):
    """Extract readable text from message content (handles both string and array formats)."""
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict):
                if block.get('type') == 'text':
                    parts.append(block.get('text', ''))
                elif block.get('type') == 'tool_use':
                    tool_name = block.get('name', 'unknown_tool')
                    tool_input = block.get('input', {})
                    # Summarize tool use concisely
                    if 'command' in tool_input:
                        parts.append(f"*[Tool: {tool_name} — `{tool_input['command'][:100]}`]*")
                    elif 'file_path' in tool_input:
                        parts.append(f"*[Tool: {tool_name} — `{tool_input['file_path']}`]*")
                    elif 'pattern' in tool_input:
                        parts.append(f"*[Tool: {tool_name} — `{tool_input['pattern']}`]*")
                    else:
                        parts.append(f"*[Tool: {tool_name}]*")
                elif block.get('type') == 'tool_result':
                    # Skip tool results in the readable transcript
                    pass
                elif block.get('type') == 'thinking':
                    # Skip thinking blocks — they're internal
                    pass
            elif isinstance(block, str):
                parts.append(block)
        return '\n'.join(parts)

    return str(content)


def parse_conversation(jsonl_file):
    """Parse JSONL into a list of conversation turns."""
    turns = []

    with open(jsonl_file) as f:
        for line in f:
            entry = json.loads(line.strip())

            # Skip queue operations
            if entry.get('type') == 'queue-operation':
                continue

            msg = entry.get('message', {})
            if not isinstance(msg, dict):
                continue

            role = msg.get('role', '')
            if role not in ('user', 'assistant'):
                continue

            content = msg.get('content', '')
            text = extract_text_content(content)

            # Skip empty turns
            if not text.strip():
                continue

            timestamp = entry.get('timestamp', '')

            turns.append({
                'role': role,
                'text': text,
                'timestamp': timestamp,
            })

    return turns


def generate_markdown(metadata, turns):
    """Generate a clean markdown transcript."""
    lines = []

    # Header
    title = metadata['title']
    lines.append(f"# Transcript: {title}")
    lines.append("")

    if metadata['created']:
        lines.append(f"**Date:** {metadata['created'].strftime('%Y-%m-%d')}")
    lines.append(f"**Model:** {metadata['model']}")
    lines.append(f"**Session ID:** {metadata['session_id']}")
    if metadata['created'] and metadata['last_activity']:
        duration = metadata['last_activity'] - metadata['created']
        minutes = int(duration.total_seconds() / 60)
        lines.append(f"**Duration:** ~{minutes} minutes")
    lines.append(f"**Turns:** {len(turns)} ({sum(1 for t in turns if t['role'] == 'user')} user, {sum(1 for t in turns if t['role'] == 'assistant')} assistant)")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Conversation
    for i, turn in enumerate(turns):
        speaker = "**Mimir:**" if turn['role'] == 'user' else "**Claude:**"
        lines.append(speaker)
        lines.append("")
        lines.append(turn['text'])
        lines.append("")
        lines.append("---")
        lines.append("")

    return '\n'.join(lines)


def generate_filename(metadata):
    """Generate a descriptive filename from metadata."""
    date_str = metadata['created'].strftime('%Y-%m-%d') if metadata['created'] else 'undated'
    # Slugify the title
    title = metadata.get('title', 'untitled')
    slug = re.sub(r'[^a-z0-9]+', '_', title.lower()).strip('_')[:50]
    return f"{date_str}_{slug}.md"


def main():
    if len(sys.argv) < 2:
        print("Usage: python process_transcript.py <path_to_zip_or_dir> [--output-dir <dir>]")
        sys.exit(1)

    source = sys.argv[1]
    output_dir = None

    if '--output-dir' in sys.argv:
        idx = sys.argv.index('--output-dir')
        output_dir = sys.argv[idx + 1]
    else:
        # Default: .context/transcripts/ relative to repo root
        script_dir = Path(__file__).parent
        output_dir = script_dir.parent / 'transcripts'

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Find and parse files
    jsonl_file, metadata_file = find_files(source)

    if not jsonl_file:
        print(f"Error: No .jsonl file found in {source}")
        sys.exit(1)

    if not metadata_file:
        print(f"Error: No metadata.json found in {source}")
        sys.exit(1)

    metadata = parse_metadata(metadata_file)
    turns = parse_conversation(jsonl_file)

    print(f"Session: {metadata['title']}")
    print(f"Date: {metadata['created']}")
    print(f"Turns: {len(turns)}")

    # Generate markdown
    md = generate_markdown(metadata, turns)

    # Write output
    filename = generate_filename(metadata)
    output_path = output_dir / filename

    with open(output_path, 'w') as f:
        f.write(md)

    print(f"Transcript saved to: {output_path}")
    return str(output_path)


if __name__ == '__main__':
    main()
