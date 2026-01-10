"""Parse Gmail filter XML export format into data models."""

import xml.etree.ElementTree as ET
from pathlib import Path

from .fields import (
    OptionalField,
    XmlField,
    get_xml_fields_to_strip,
)
from .models import (
    Author,
    Filter,
    FilterActions,
    FilterCriteria,
    GmailFilterCollection,
    Metadata,
)
from .name_generator import generate_filter_name


APPS_NAMESPACE = 'http://schemas.google.com/apps/2006'


def parse_xml_to_filter_collection(
    xml_path: str | Path,
    strip_fields: set[OptionalField] | None = None,
    generate_names: bool = True,
) -> GmailFilterCollection:
    tree = ET.parse(xml_path)
    root = tree.getroot()

    namespaces = {
        'atom': 'http://www.w3.org/2005/Atom',
        'apps': APPS_NAMESPACE,
    }

    xml_fields_to_strip = get_xml_fields_to_strip(strip_fields) if strip_fields else set()

    title = None
    if XmlField.METADATA_TITLE not in xml_fields_to_strip:
        title = _extract_optional_text(root, 'atom:title', namespaces)

    feed_id = None
    if XmlField.METADATA_ID not in xml_fields_to_strip:
        feed_id = _extract_optional_text(root, 'atom:id', namespaces)

    updated_time = None
    if XmlField.METADATA_UPDATED not in xml_fields_to_strip:
        updated_time = _extract_optional_text(root, 'atom:updated', namespaces)

    author_elem = root.find('atom:author', namespaces)
    author = None
    if (
        author_elem is not None
        and XmlField.METADATA_AUTHOR_NAME not in xml_fields_to_strip
        and XmlField.METADATA_AUTHOR_EMAIL not in xml_fields_to_strip
    ):
        author = _parse_author(author_elem, namespaces)

    metadata = Metadata(
        title=title,
        author=author,
        id=feed_id,
        updated_time=updated_time,
    )

    filters = []
    for entry in root.findall('atom:entry', namespaces):
        filter_obj = _parse_filter_entry(entry, namespaces, xml_fields_to_strip, generate_names)
        filters.append(filter_obj)

    return GmailFilterCollection(metadata=metadata, filters=filters)


def _extract_text(element: ET.Element, path: str, namespaces: dict) -> str:
    elem = element.find(path, namespaces)
    if elem is None or elem.text is None:
        raise ValueError(f'Missing required element: {path}')
    return elem.text


def _extract_optional_text(element: ET.Element, path: str, namespaces: dict) -> str | None:
    elem = element.find(path, namespaces)
    if elem is None or elem.text is None:
        return None
    return elem.text


def _parse_author(author_elem: ET.Element | None, namespaces: dict) -> Author:
    if author_elem is None:
        raise ValueError('Missing author element')

    name = _extract_text(author_elem, 'atom:name', namespaces)
    email = _extract_text(author_elem, 'atom:email', namespaces)

    return Author(name=name, email=email)


def _parse_filter_entry(
    entry: ET.Element,
    namespaces: dict,
    xml_fields_to_strip: set[XmlField],
    generate_names: bool,
) -> Filter:
    filter_id = None
    if XmlField.FILTER_ID not in xml_fields_to_strip:
        filter_id = _extract_optional_text(entry, 'atom:id', namespaces)

    updated_time = None
    if XmlField.FILTER_UPDATED not in xml_fields_to_strip:
        updated_time = _extract_optional_text(entry, 'atom:updated', namespaces)

    properties = {}
    for prop in entry.findall('apps:property', namespaces):
        name = prop.get('name')
        value = prop.get('value')
        if name and value is not None:
            properties[name] = value

    criteria = _extract_criteria(properties)
    actions = _extract_actions(properties)

    name = None
    if generate_names:
        name = generate_filter_name(criteria, actions)

    return Filter(
        id=filter_id,
        updated_time=updated_time,
        criteria=criteria,
        actions=actions,
        name=name,
    )


def _extract_criteria(properties: dict[str, str]) -> FilterCriteria:
    return FilterCriteria(
        from_=properties.get('from'),
        to=properties.get('to'),
        subject=properties.get('subject'),
        has_the_word=properties.get('hasTheWord'),
    )


def _extract_actions(properties: dict[str, str]) -> FilterActions:
    return FilterActions(
        label=properties.get('label'),
        should_mark_as_read=_parse_bool(properties.get('shouldMarkAsRead')),
        should_archive=_parse_bool(properties.get('shouldArchive')),
        should_star=_parse_bool(properties.get('shouldStar')),
        should_trash=_parse_bool(properties.get('shouldTrash')),
        should_never_spam=_parse_bool(properties.get('shouldNeverSpam')),
    )


def _parse_bool(value: str | None) -> bool | None:
    if value is None:
        return None
    return value.lower() == 'true'
