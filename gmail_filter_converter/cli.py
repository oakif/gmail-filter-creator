"""Command-line interface for filter converter."""

import sys
from pathlib import Path

from .xml_parser import parse_xml_to_filters
from .yaml_serializer import serialize_filters_to_yaml


def main() -> None:
    if len(sys.argv) < 3:
        print('Usage: gmail-filter-converter <input.xml> <output.yaml>')
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    if not input_path.exists():
        print(f'Error: Input file not found: {input_path}')
        sys.exit(1)

    try:
        print(f'Parsing {input_path}...')
        filter_collection = parse_xml_to_filters(input_path)

        print(f'Converting to YAML and writing to {output_path}...')
        serialize_filters_to_yaml(filter_collection, output_path)

        print(f'Success! Converted {len(filter_collection.filters)} filters.')
    except Exception as e:
        print(f'Error: {e}', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
