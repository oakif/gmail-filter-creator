import yaml
from pathlib import Path
from tempfile import NamedTemporaryFile

from gmail_filter_converter.fields import (
    ALL_OPTIONAL_FIELDS,
    UNNECESSARY_METADATA,
    OptionalField,
    OPTIONAL_FIELD_TO_XML,
    OPTIONAL_FIELD_TO_YAML,
    XML_TO_YAML_FIELD_MAP,
    XmlField,
    YamlField,
    get_xml_fields_to_strip,
    get_yaml_fields_to_strip,
)
from gmail_filter_converter.xml_parser import parse_xml_to_filters
from gmail_filter_converter.yaml_serializer import serialize_filters_to_yaml


def test_optional_field_enum_values():
    expected_fields = {
        'METADATA_TITLE',
        'METADATA_ID',
        'METADATA_UPDATED_TIME',
        'METADATA_AUTHOR',
        'FILTER_ID',
        'FILTER_UPDATED_TIME',
    }
    actual_fields = {f.name for f in OptionalField}
    assert actual_fields == expected_fields


def test_xml_field_enum_values():
    expected_count = 18
    assert len(list(XmlField)) == expected_count


def test_yaml_field_enum_values():
    expected_count = 18
    assert len(list(YamlField)) == expected_count


def test_xml_to_yaml_bidirectional_mapping():
    for xml_field, yaml_field in XML_TO_YAML_FIELD_MAP.items():
        assert yaml_field in OPTIONAL_FIELD_TO_YAML.values() or yaml_field.value.startswith(
            'filters[].',
        )


def test_optional_field_to_xml_mapping_completeness():
    for opt_field in OptionalField:
        assert opt_field in OPTIONAL_FIELD_TO_XML
        assert len(OPTIONAL_FIELD_TO_XML[opt_field]) > 0


def test_optional_field_to_yaml_mapping_completeness():
    for opt_field in OptionalField:
        assert opt_field in OPTIONAL_FIELD_TO_YAML
        assert len(OPTIONAL_FIELD_TO_YAML[opt_field]) > 0


def test_metadata_author_maps_to_both_name_and_email():
    author_xml_fields = OPTIONAL_FIELD_TO_XML[OptionalField.METADATA_AUTHOR]
    assert XmlField.METADATA_AUTHOR_NAME in author_xml_fields
    assert XmlField.METADATA_AUTHOR_EMAIL in author_xml_fields

    author_yaml_fields = OPTIONAL_FIELD_TO_YAML[OptionalField.METADATA_AUTHOR]
    assert YamlField.METADATA_AUTHOR_NAME in author_yaml_fields
    assert YamlField.METADATA_AUTHOR_EMAIL in author_yaml_fields


def test_get_xml_fields_to_strip():
    strip_set = {OptionalField.FILTER_ID, OptionalField.METADATA_ID}
    xml_fields = get_xml_fields_to_strip(strip_set)

    assert XmlField.FILTER_ID in xml_fields
    assert XmlField.METADATA_ID in xml_fields
    assert len(xml_fields) == 2


def test_get_yaml_fields_to_strip():
    strip_set = {OptionalField.FILTER_ID, OptionalField.METADATA_ID}
    yaml_fields = get_yaml_fields_to_strip(strip_set)

    assert YamlField.FILTER_ID in yaml_fields
    assert YamlField.METADATA_ID in yaml_fields
    assert len(yaml_fields) == 2


def test_metadata_author_groups_both_fields():
    strip_set = {OptionalField.METADATA_AUTHOR}
    xml_fields = get_xml_fields_to_strip(strip_set)

    assert XmlField.METADATA_AUTHOR_NAME in xml_fields
    assert XmlField.METADATA_AUTHOR_EMAIL in xml_fields


def test_unnecessary_metadata_preset():
    assert OptionalField.FILTER_ID in UNNECESSARY_METADATA
    assert OptionalField.FILTER_UPDATED_TIME in UNNECESSARY_METADATA
    assert OptionalField.METADATA_ID in UNNECESSARY_METADATA
    assert OptionalField.METADATA_UPDATED_TIME in UNNECESSARY_METADATA


def test_all_optional_fields_preset():
    assert len(ALL_OPTIONAL_FIELDS) == len(list(OptionalField))


def test_parse_xml_with_no_strip(tmp_path):
    xml_file = Path(__file__).parent / 'example_filters.xml'
    collection = parse_xml_to_filters(xml_file)

    assert collection.metadata.id is not None
    assert collection.metadata.updated_time is not None
    assert len(collection.filters) > 0
    assert collection.filters[0].id is not None
    assert collection.filters[0].updated_time is not None


def test_parse_xml_with_strip_metadata_ids(tmp_path):
    xml_file = Path(__file__).parent / 'example_filters.xml'
    strip_set = {OptionalField.METADATA_ID, OptionalField.FILTER_ID}
    collection = parse_xml_to_filters(xml_file, strip_set)

    assert collection.metadata.id is None
    assert collection.metadata.updated_time is not None
    assert len(collection.filters) > 0
    assert collection.filters[0].id is None
    assert collection.filters[0].updated_time is not None


def test_parse_xml_with_strip_unnecessary_metadata(tmp_path):
    xml_file = Path(__file__).parent / 'example_filters.xml'
    collection = parse_xml_to_filters(xml_file, UNNECESSARY_METADATA)

    assert collection.metadata.id is None
    assert collection.metadata.updated_time is None
    assert len(collection.filters) > 0
    assert collection.filters[0].id is None
    assert collection.filters[0].updated_time is None


def test_serialize_yaml_with_no_strip():
    xml_file = Path(__file__).parent / 'example_filters.xml'
    collection = parse_xml_to_filters(xml_file)

    with NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        output_path = Path(f.name)

    try:
        serialize_filters_to_yaml(collection, output_path)

        with open(output_path) as f:
            data = yaml.safe_load(f)

        assert 'metadata' in data
        assert data['metadata'].get('id') is not None
        assert data['metadata'].get('updated_time') is not None
    finally:
        output_path.unlink()


def test_serialize_yaml_with_strip_ids():
    xml_file = Path(__file__).parent / 'example_filters.xml'
    collection = parse_xml_to_filters(xml_file)

    with NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        output_path = Path(f.name)

    try:
        strip_set = {OptionalField.METADATA_ID, OptionalField.FILTER_ID}
        serialize_filters_to_yaml(collection, output_path, strip_set)

        with open(output_path) as f:
            data = yaml.safe_load(f)

        assert 'metadata' in data
        assert data['metadata'].get('id') is None
        assert data['filters'][0].get('id') is None
    finally:
        output_path.unlink()


def test_serialize_yaml_with_strip_unnecessary_metadata():
    xml_file = Path(__file__).parent / 'example_filters.xml'
    collection = parse_xml_to_filters(xml_file)

    with NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        output_path = Path(f.name)

    try:
        serialize_filters_to_yaml(collection, output_path, UNNECESSARY_METADATA)

        with open(output_path) as f:
            data = yaml.safe_load(f)

        assert 'metadata' in data
        assert data['metadata'].get('id') is None
        assert data['metadata'].get('updated_time') is None
        if 'filters' in data and len(data['filters']) > 0:
            assert data['filters'][0].get('id') is None
            assert data['filters'][0].get('updated_time') is None
    finally:
        output_path.unlink()


def test_round_trip_with_stripped_metadata():
    xml_file = Path(__file__).parent / 'example_filters.xml'

    original = parse_xml_to_filters(xml_file, UNNECESSARY_METADATA)

    with NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        output_path = Path(f.name)

    try:
        serialize_filters_to_yaml(original, output_path, UNNECESSARY_METADATA)

        with open(output_path) as f:
            data = yaml.safe_load(f)

        assert 'filters' in data
        assert len(data['filters']) == len(original.filters)

        for i, filter_data in enumerate(data['filters']):
            original_filter = original.filters[i]
            if original_filter.criteria.from_:
                assert filter_data['criteria']['from'] == original_filter.criteria.from_
            if original_filter.actions.label:
                assert filter_data['actions']['label'] == original_filter.actions.label
    finally:
        output_path.unlink()


def test_backward_compatibility_unchanged_behavior():
    xml_file = Path(__file__).parent / 'example_filters.xml'

    collection_default = parse_xml_to_filters(xml_file)
    collection_explicit_none = parse_xml_to_filters(xml_file, None)

    assert collection_default.metadata.id == collection_explicit_none.metadata.id
    assert collection_default.metadata.updated_time == collection_explicit_none.metadata.updated_time
    assert len(collection_default.filters) == len(collection_explicit_none.filters)

    for f1, f2 in zip(collection_default.filters, collection_explicit_none.filters):
        assert f1.id == f2.id
        assert f1.updated_time == f2.updated_time
