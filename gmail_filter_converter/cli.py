"""Command-line interface for filter converter."""

import argparse
import sys
from pathlib import Path

from .fields import (
    UNNECESSARY_METADATA,
    OptionalField,
)
from .xml_parser import parse_xml_to_filters
from .yaml_serializer import serialize_filters_to_yaml


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Convert Gmail filter XML export to YAML format',
    )
    parser.add_argument('input', help='Input XML file from Gmail export')
    parser.add_argument('output', help='Output YAML file')
    parser.add_argument(
        '--strip-unnecessary-metadata',
        action='store_true',
        help='Strip all unnecessary metadata (IDs and timestamps)',
    )
    parser.add_argument(
        '--strip-fields',
        help='Comma-separated list of optional fields to strip (e.g., FILTER_ID,METADATA_AUTHOR)',
    )
    parser.add_argument(
        '--no-names',
        action='store_true',
        help='Do not generate filter names in YAML output',
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        print(f'Error: Input file not found: {input_path}')
        sys.exit(1)

    strip_fields = set()
    if args.strip_unnecessary_metadata:
        strip_fields = set(UNNECESSARY_METADATA)
    elif args.strip_fields:
        try:
            strip_fields = {OptionalField[f.strip()] for f in args.strip_fields.split(',')}
        except KeyError as e:
            print(f'Error: Invalid field name {e}', file=sys.stderr)
            sys.exit(1)

    if args.no_names:
        strip_fields.add(OptionalField.FILTER_NAME)

    strip_fields = strip_fields if strip_fields else None

    try:
        print(f'Parsing {input_path}...')
        filter_collection = parse_xml_to_filters(input_path, strip_fields)

        print(f'Converting to YAML and writing to {output_path}...')
        serialize_filters_to_yaml(filter_collection, output_path, strip_fields)

        print(f'Success! Converted {len(filter_collection.filters)} filters.')
    except Exception as e:
        print(f'Error: {e}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
