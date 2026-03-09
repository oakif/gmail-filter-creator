"""Parse grouped YAML filter files (with comment-based group headers) back into models."""

import re
from pathlib import Path

import yaml

from .models import (
    Author,
    Filter,
    FilterActions,
    FilterCriteria,
    FilterGroup,
    GroupedFilterCollection,
    Metadata,
)

GROUP_HEADER_PATTERN = re.compile(r'^\s*#\s+(.+)$', re.MULTILINE)


def parse_yaml_to_grouped_filter_collection(yaml_path: str | Path) -> GroupedFilterCollection:
    text = Path(yaml_path).read_text()

    filters_match = re.search(r'^filters:\s*$', text, re.MULTILINE)
    if not filters_match:
        raise ValueError('YAML file must contain a top-level "filters:" key')

    metadata_text = text[:filters_match.start()] + 'filters: []\n'
    filter_zone = text[filters_match.end():]

    raw = yaml.safe_load(metadata_text)
    metadata = _dict_to_metadata(raw.get('metadata', {}))

    parts = GROUP_HEADER_PATTERN.split(filter_zone)

    groups = []

    ungrouped_text = parts[0]
    if ungrouped_text.strip():
        filters = _parse_filter_list_yaml(ungrouped_text)
        if filters:
            groups.append(FilterGroup(name='', filters=filters))

    for i in range(1, len(parts), 2):
        group_name = parts[i].strip()
        filter_text = parts[i + 1] if i + 1 < len(parts) else ''
        filters = _parse_filter_list_yaml(filter_text)
        groups.append(FilterGroup(name=group_name, filters=filters))

    return GroupedFilterCollection(metadata=metadata, groups=groups)


def _parse_filter_list_yaml(text: str) -> list[Filter]:
    stripped = text.strip()
    if not stripped or not stripped.startswith('-'):
        return []

    raw_list = yaml.safe_load(stripped)
    if not isinstance(raw_list, list):
        return []

    return [_dict_to_filter(d) for d in raw_list]


def _dict_to_metadata(d: dict) -> Metadata:
    if not d:
        return Metadata()

    author = None
    if 'author' in d:
        author = Author(
            name=d['author'].get('name', ''),
            email=d['author'].get('email', ''),
        )

    return Metadata(
        title=d.get('title'),
        author=author,
        id=d.get('id'),
        updated_time=d.get('updated_time'),
    )


def _dict_to_filter(d: dict) -> Filter:
    criteria_dict = d.get('criteria', {})
    actions_dict = d.get('actions', {})

    criteria = FilterCriteria(
        from_=criteria_dict.get('from'),
        to=criteria_dict.get('to'),
        subject=criteria_dict.get('subject'),
        has_the_word=criteria_dict.get('has_the_word'),
    )

    actions = FilterActions(
        label=actions_dict.get('label'),
        should_mark_as_read=actions_dict.get('should_mark_as_read'),
        should_archive=actions_dict.get('should_archive'),
        should_star=actions_dict.get('should_star'),
        should_trash=actions_dict.get('should_trash'),
        should_never_spam=actions_dict.get('should_never_spam'),
    )

    return Filter(
        name=d.get('name'),
        criteria=criteria,
        actions=actions,
        id=d.get('id'),
        updated_time=d.get('updated_time'),
    )
