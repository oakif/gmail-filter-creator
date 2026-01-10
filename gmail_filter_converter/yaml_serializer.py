"""Serialize filter data models to YAML format."""

from pathlib import Path

import yaml

from .fields import (
    OptionalField,
    YamlField,
    YamlFilterNameGenerationMode,
    get_yaml_fields_to_strip,
)
from .models import Filter, FilterActions, FilterCriteria, GmailFilterCollection
from .name_generator import generate_filter_name


class _LiteralBlockString(str):
    """Mark strings to be rendered with literal block style (|) in YAML.

    This produces cleaner YAML output for strings with quotes and special chars.
    Instead of escaped backslashes like \"...\", we get readable multi-line text.
    """
    pass


def _literal_string_representer(dumper: yaml.Dumper, data: _LiteralBlockString) -> yaml.Node:
    """Tell PyYAML to use literal block style (|) for our marked strings.

    Literal block style preserves newlines and quotes without escaping.
    So instead of: has_the_word: "\"Thank you...\""
    We get:       has_the_word: |
                    "Thank you..."
    """
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')


yaml.add_representer(_LiteralBlockString, _literal_string_representer)


def _should_use_literal_block_style(text: str) -> bool:
    return '"' in text or "'" in text


def serialize_filters_to_yaml(
    filter_collection: GmailFilterCollection,
    output_path: str | Path,
    strip_fields: set[OptionalField] | None = None,
    name_mode: YamlFilterNameGenerationMode = YamlFilterNameGenerationMode.GENERATE_MISSING,
) -> None:
    data = _convert_to_dict(filter_collection, strip_fields, name_mode)

    with open(output_path, 'w') as f:
        yaml.dump(
            data,
            f,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
            default_style=None,
        )


def _convert_to_dict(
    filter_collection: GmailFilterCollection,
    strip_fields: set[OptionalField] | None = None,
    name_mode: YamlFilterNameGenerationMode = YamlFilterNameGenerationMode.GENERATE_MISSING,
) -> dict:
    yaml_fields_to_strip = get_yaml_fields_to_strip(strip_fields) if strip_fields else set()

    metadata_dict = {}
    if YamlField.METADATA_TITLE not in yaml_fields_to_strip and filter_collection.metadata.title:
        metadata_dict['title'] = filter_collection.metadata.title

    if (
        YamlField.METADATA_AUTHOR_NAME not in yaml_fields_to_strip
        and YamlField.METADATA_AUTHOR_EMAIL not in yaml_fields_to_strip
        and filter_collection.metadata.author
    ):
        metadata_dict['author'] = {
            'name': filter_collection.metadata.author.name,
            'email': filter_collection.metadata.author.email,
        }

    if YamlField.METADATA_ID not in yaml_fields_to_strip and filter_collection.metadata.id:
        metadata_dict['id'] = filter_collection.metadata.id

    if (
        YamlField.METADATA_UPDATED_TIME not in yaml_fields_to_strip
        and filter_collection.metadata.updated_time
    ):
        metadata_dict['updated_time'] = filter_collection.metadata.updated_time

    return {
        'metadata': metadata_dict,
        'filters': [_filter_to_dict(f, yaml_fields_to_strip, name_mode) for f in filter_collection.filters],
    }


def _filter_to_dict(
    filter_obj: Filter,
    yaml_fields_to_strip: set[YamlField],
    name_mode: YamlFilterNameGenerationMode = YamlFilterNameGenerationMode.GENERATE_MISSING,
) -> dict:
    result = {}

    # Name comes first
    if YamlField.FILTER_NAME not in yaml_fields_to_strip:
        if name_mode == YamlFilterNameGenerationMode.SUPPRESS:
            pass
        elif name_mode == YamlFilterNameGenerationMode.GENERATE_MISSING:
            if filter_obj.name:
                result['name'] = filter_obj.name
            else:
                result['name'] = generate_filter_name(filter_obj.criteria, filter_obj.actions)
        elif name_mode == YamlFilterNameGenerationMode.REGENERATE_ALL:
            result['name'] = generate_filter_name(filter_obj.criteria, filter_obj.actions)

    if YamlField.FILTER_ID not in yaml_fields_to_strip and filter_obj.id:
        result['id'] = filter_obj.id

    if YamlField.FILTER_UPDATED_TIME not in yaml_fields_to_strip and filter_obj.updated_time:
        result['updated_time'] = filter_obj.updated_time

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
        if _should_use_literal_block_style(criteria.subject):
            result['subject'] = _LiteralBlockString(criteria.subject)
        else:
            result['subject'] = criteria.subject
    if criteria.has_the_word is not None:
        if _should_use_literal_block_style(criteria.has_the_word):
            result['has_the_word'] = _LiteralBlockString(criteria.has_the_word)
        else:
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
