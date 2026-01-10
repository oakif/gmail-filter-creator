"""Serialize filter data models to YAML format."""

from pathlib import Path

import yaml

from .models import FilterActions, FilterCriteria, GmailFilterCollection


def serialize_filters_to_yaml(
    filter_collection: GmailFilterCollection,
    output_path: str | Path,
) -> None:
    data = _convert_to_dict(filter_collection)
    yaml.dump(
        data,
        open(output_path, 'w'),
        default_flow_style=False,
        sort_keys=False,
    )


def _convert_to_dict(filter_collection: GmailFilterCollection) -> dict:
    return {
        'metadata': {
            'title': filter_collection.metadata.title,
            'author': {
                'name': filter_collection.metadata.author.name,
                'email': filter_collection.metadata.author.email,
            },
            'id': filter_collection.metadata.id,
            'updated_time': filter_collection.metadata.updated_time,
        },
        'filters': [_filter_to_dict(f) for f in filter_collection.filters],
    }


def _filter_to_dict(filter_obj) -> dict:
    result = {
        'id': filter_obj.id,
        'updated_time': filter_obj.updated_time,
    }

    criteria_dict = _filter_criteria_to_dict(filter_obj.criteria)
    if criteria_dict:
        result['criteria'] = criteria_dict

    actions_dict = _filter_actions_to_dict(filter_obj.actions)
    if actions_dict:
        result['actions'] = actions_dict

    return result


def _filter_criteria_to_dict(criteria: FilterCriteria) -> dict:
    result = {}
    if criteria.from_ is not None:
        result['from'] = criteria.from_
    if criteria.to is not None:
        result['to'] = criteria.to
    if criteria.subject is not None:
        result['subject'] = criteria.subject
    if criteria.has_the_word is not None:
        result['has_the_word'] = criteria.has_the_word
    return result


def _filter_actions_to_dict(actions: FilterActions) -> dict:
    result = {}
    if actions.label is not None:
        result['label'] = actions.label
    if actions.should_mark_as_read is not None:
        result['should_mark_as_read'] = actions.should_mark_as_read
    if actions.should_archive is not None:
        result['should_archive'] = actions.should_archive
    if actions.should_star is not None:
        result['should_star'] = actions.should_star
    if actions.should_trash is not None:
        result['should_trash'] = actions.should_trash
    if actions.should_never_spam is not None:
        result['should_never_spam'] = actions.should_never_spam
    return result
