"""Serialize GroupedFilterCollection to YAML with comment-based group headers."""

from pathlib import Path

import yaml

from .models import FilterGroup, GroupedFilterCollection, Metadata
from .yaml_serializer import (
    LiteralBlockString,
    filter_to_dict,
    literal_string_representer,
)

yaml.add_representer(LiteralBlockString, literal_string_representer)


def serialize_grouped_filter_collection_to_yaml(
    collection: GroupedFilterCollection,
    output_path: str | Path,
) -> None:
    text = _build_yaml_text(collection)
    Path(output_path).write_text(text)


def _build_yaml_text(collection: GroupedFilterCollection) -> str:
    parts = []

    metadata_dict = _metadata_to_dict(collection.metadata)
    metadata_yaml = yaml.dump(
        {'metadata': metadata_dict},
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
    )
    parts.append(metadata_yaml.rstrip())

    parts.append('filters:')

    for group in collection.groups:
        parts.append(_serialize_group(group))

    return '\n'.join(parts) + '\n'


def _metadata_to_dict(metadata: Metadata) -> dict:
    result = {}
    if metadata.title:
        result['title'] = metadata.title
    if metadata.author:
        result['author'] = {
            'name': metadata.author.name,
            'email': metadata.author.email,
        }
    if metadata.id:
        result['id'] = metadata.id
    if metadata.updated_time:
        result['updated_time'] = metadata.updated_time
    return result


def _serialize_group(group: FilterGroup) -> str:
    parts = []

    if group.name:
        parts.append(f'\n\n# {group.name}')

    if group.filters:
        empty_strip = set()
        filter_dicts = [filter_to_dict(f, empty_strip) for f in group.filters]
        filters_yaml = yaml.dump(
            filter_dicts,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
        )
        parts.append('\n' + filters_yaml.rstrip())

    return '\n'.join(parts)
