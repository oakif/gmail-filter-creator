"""Tests for XML to YAML conversion."""

import tempfile
from pathlib import Path

import pytest
import yaml

from gmail_filter_converter.xml_parser import parse_xml_to_filters
from gmail_filter_converter.yaml_serializer import serialize_filters_to_yaml


@pytest.fixture
def example_xml_path() -> Path:
    return Path(__file__).parent / 'example_filters.xml'


@pytest.fixture
def temp_yaml_file():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        path = Path(f.name)
    yield path
    path.unlink()


def test_parse_example_xml(example_xml_path: Path) -> None:
    collection = parse_xml_to_filters(example_xml_path)

    assert collection.metadata.title == 'Mail Filters'
    assert collection.metadata.author.name == 'Test User'
    assert collection.metadata.author.email == 'user@example.com'
    assert len(collection.filters) == 3


def test_parse_filters_have_required_fields(example_xml_path: Path) -> None:
    collection = parse_xml_to_filters(example_xml_path)

    for filter_obj in collection.filters:
        assert filter_obj.id
        assert filter_obj.updated_time


def test_parse_first_filter_has_criteria_and_actions(example_xml_path: Path) -> None:
    collection = parse_xml_to_filters(example_xml_path)
    first_filter = collection.filters[0]

    assert first_filter.criteria.from_ == 'transactional@mail.burgerking.com'
    assert first_filter.criteria.subject == 'Your Burger King Receipt'
    assert first_filter.criteria.has_the_word == 'Thanks for ordering from Burger King'
    assert first_filter.actions.label == 'Receipts/Burger King'
    assert first_filter.actions.should_mark_as_read is True
    assert first_filter.actions.should_archive is True


def test_parse_handles_quoted_values(example_xml_path: Path) -> None:
    collection = parse_xml_to_filters(example_xml_path)
    second_filter = collection.filters[1]

    assert second_filter.criteria.subject is not None
    assert '"' in second_filter.criteria.subject


def test_serialize_to_yaml(example_xml_path: Path, temp_yaml_file: Path) -> None:
    collection = parse_xml_to_filters(example_xml_path)
    serialize_filters_to_yaml(collection, temp_yaml_file)

    assert temp_yaml_file.exists()

    with open(temp_yaml_file) as f:
        data = yaml.safe_load(f)

    assert data['metadata']['title'] == 'Mail Filters'
    assert len(data['filters']) == 3


def test_yaml_has_correct_structure(example_xml_path: Path, temp_yaml_file: Path) -> None:
    collection = parse_xml_to_filters(example_xml_path)
    serialize_filters_to_yaml(collection, temp_yaml_file)

    with open(temp_yaml_file) as f:
        data = yaml.safe_load(f)

    first_filter = data['filters'][0]
    assert 'id' in first_filter
    assert 'updated_time' in first_filter
    assert 'criteria' in first_filter
    assert 'actions' in first_filter

    assert first_filter['criteria']['from'] == 'transactional@mail.burgerking.com'
    assert first_filter['actions']['label'] == 'Receipts/Burger King'
    assert first_filter['actions']['should_mark_as_read'] is True


def test_yaml_has_metadata(example_xml_path: Path, temp_yaml_file: Path) -> None:
    collection = parse_xml_to_filters(example_xml_path)
    serialize_filters_to_yaml(collection, temp_yaml_file)

    with open(temp_yaml_file) as f:
        data = yaml.safe_load(f)

    assert 'metadata' in data
    assert 'title' in data['metadata']
    assert 'author' in data['metadata']
    assert 'id' in data['metadata']
    assert 'updated_time' in data['metadata']


def test_boolean_conversion_to_yaml(example_xml_path: Path, temp_yaml_file: Path) -> None:
    collection = parse_xml_to_filters(example_xml_path)
    serialize_filters_to_yaml(collection, temp_yaml_file)

    with open(temp_yaml_file) as f:
        data = yaml.safe_load(f)

    for filter_data in data['filters']:
        if 'should_mark_as_read' in filter_data['actions']:
            assert isinstance(filter_data['actions']['should_mark_as_read'], bool)
        if 'should_archive' in filter_data['actions']:
            assert isinstance(filter_data['actions']['should_archive'], bool)


def test_property_name_snake_case(example_xml_path: Path, temp_yaml_file: Path) -> None:
    collection = parse_xml_to_filters(example_xml_path)
    serialize_filters_to_yaml(collection, temp_yaml_file)

    with open(temp_yaml_file) as f:
        content = f.read()

    assert 'should_mark_as_read' in content
    assert 'should_archive' in content
    assert 'has_the_word' in content
    assert 'shouldMarkAsRead' not in content
    assert 'shouldArchive' not in content
    assert 'hasTheWord' not in content


def test_round_trip_xml_to_yaml_preserves_data(example_xml_path: Path, temp_yaml_file: Path) -> None:
    original = parse_xml_to_filters(example_xml_path)
    serialize_filters_to_yaml(original, temp_yaml_file)

    with open(temp_yaml_file) as f:
        data = yaml.safe_load(f)

    assert data['metadata']['title'] == original.metadata.title
    assert len(data['filters']) == len(original.filters)

    for yaml_filter, original_filter in zip(data['filters'], original.filters):
        assert yaml_filter['id'] == original_filter.id
        assert yaml_filter['updated_time'] == original_filter.updated_time
