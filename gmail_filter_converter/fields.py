from enum import Enum


class XmlField(str, Enum):
    # Metadata fields
    METADATA_TITLE = 'title'
    METADATA_ID = 'id'
    METADATA_UPDATED = 'updated'
    METADATA_AUTHOR_NAME = 'author.name'
    METADATA_AUTHOR_EMAIL = 'author.email'

    # Filter-level fields
    FILTER_ID = 'id'
    FILTER_UPDATED = 'updated'

    # Criteria fields
    FROM = 'from'
    TO = 'to'
    SUBJECT = 'subject'
    HAS_THE_WORD = 'hasTheWord'

    # Action fields
    LABEL = 'label'
    SHOULD_MARK_AS_READ = 'shouldMarkAsRead'
    SHOULD_ARCHIVE = 'shouldArchive'
    SHOULD_STAR = 'shouldStar'
    SHOULD_TRASH = 'shouldTrash'
    SHOULD_NEVER_SPAM = 'shouldNeverSpam'


class YamlField(str, Enum):
    # Metadata fields
    METADATA_TITLE = 'metadata.title'
    METADATA_ID = 'metadata.id'
    METADATA_UPDATED_TIME = 'metadata.updated_time'
    METADATA_AUTHOR_NAME = 'metadata.author.name'
    METADATA_AUTHOR_EMAIL = 'metadata.author.email'

    # Filter-level fields
    FILTER_ID = 'filters[].id'
    FILTER_UPDATED_TIME = 'filters[].updated_time'

    # Criteria fields
    FROM = 'filters[].criteria.from'
    TO = 'filters[].criteria.to'
    SUBJECT = 'filters[].criteria.subject'
    HAS_THE_WORD = 'filters[].criteria.has_the_word'

    # Action fields
    LABEL = 'filters[].actions.label'
    SHOULD_MARK_AS_READ = 'filters[].actions.should_mark_as_read'
    SHOULD_ARCHIVE = 'filters[].actions.should_archive'
    SHOULD_STAR = 'filters[].actions.should_star'
    SHOULD_TRASH = 'filters[].actions.should_trash'
    SHOULD_NEVER_SPAM = 'filters[].actions.should_never_spam'


class OptionalField(str, Enum):
    """Fields that can be optionally stripped from output.

    These represent logical groupings of related fields that can be
    stripped together (e.g., METADATA_AUTHOR strips both name and email).
    """

    # Metadata fields
    METADATA_TITLE = 'METADATA_TITLE'
    METADATA_ID = 'METADATA_ID'
    METADATA_UPDATED_TIME = 'METADATA_UPDATED_TIME'
    METADATA_AUTHOR = 'METADATA_AUTHOR'

    # Filter-level fields
    FILTER_ID = 'FILTER_ID'
    FILTER_UPDATED_TIME = 'FILTER_UPDATED_TIME'


XML_TO_YAML_FIELD_MAP: dict[XmlField, YamlField] = {
    # Metadata fields
    XmlField.METADATA_TITLE: YamlField.METADATA_TITLE,
    XmlField.METADATA_ID: YamlField.METADATA_ID,
    XmlField.METADATA_UPDATED: YamlField.METADATA_UPDATED_TIME,
    XmlField.METADATA_AUTHOR_NAME: YamlField.METADATA_AUTHOR_NAME,
    XmlField.METADATA_AUTHOR_EMAIL: YamlField.METADATA_AUTHOR_EMAIL,
    # Filter-level fields
    XmlField.FILTER_ID: YamlField.FILTER_ID,
    XmlField.FILTER_UPDATED: YamlField.FILTER_UPDATED_TIME,
    # Criteria fields
    XmlField.FROM: YamlField.FROM,
    XmlField.TO: YamlField.TO,
    XmlField.SUBJECT: YamlField.SUBJECT,
    XmlField.HAS_THE_WORD: YamlField.HAS_THE_WORD,
    # Action fields
    XmlField.LABEL: YamlField.LABEL,
    XmlField.SHOULD_MARK_AS_READ: YamlField.SHOULD_MARK_AS_READ,
    XmlField.SHOULD_ARCHIVE: YamlField.SHOULD_ARCHIVE,
    XmlField.SHOULD_STAR: YamlField.SHOULD_STAR,
    XmlField.SHOULD_TRASH: YamlField.SHOULD_TRASH,
    XmlField.SHOULD_NEVER_SPAM: YamlField.SHOULD_NEVER_SPAM,
}

YAML_TO_XML_FIELD_MAP: dict[YamlField, XmlField] = {
    v: k for k, v in XML_TO_YAML_FIELD_MAP.items()
}

OPTIONAL_FIELD_TO_XML: dict[OptionalField, set[XmlField]] = {
    OptionalField.METADATA_TITLE: {XmlField.METADATA_TITLE},
    OptionalField.METADATA_ID: {XmlField.METADATA_ID},
    OptionalField.METADATA_UPDATED_TIME: {XmlField.METADATA_UPDATED},
    OptionalField.METADATA_AUTHOR: {
        XmlField.METADATA_AUTHOR_NAME,
        XmlField.METADATA_AUTHOR_EMAIL,
    },
    OptionalField.FILTER_ID: {XmlField.FILTER_ID},
    OptionalField.FILTER_UPDATED_TIME: {XmlField.FILTER_UPDATED},
}

OPTIONAL_FIELD_TO_YAML: dict[OptionalField, set[YamlField]] = {
    OptionalField.METADATA_TITLE: {YamlField.METADATA_TITLE},
    OptionalField.METADATA_ID: {YamlField.METADATA_ID},
    OptionalField.METADATA_UPDATED_TIME: {YamlField.METADATA_UPDATED_TIME},
    OptionalField.METADATA_AUTHOR: {
        YamlField.METADATA_AUTHOR_NAME,
        YamlField.METADATA_AUTHOR_EMAIL,
    },
    OptionalField.FILTER_ID: {YamlField.FILTER_ID},
    OptionalField.FILTER_UPDATED_TIME: {YamlField.FILTER_UPDATED_TIME},
}

# Common preset: fields that are not necessary for Gmail import
UNNECESSARY_METADATA: set[OptionalField] = {
    OptionalField.FILTER_ID,
    OptionalField.FILTER_UPDATED_TIME,
    OptionalField.METADATA_ID,
    OptionalField.METADATA_UPDATED_TIME,
}

# All optional fields combined
ALL_OPTIONAL_FIELDS: set[OptionalField] = set(OptionalField)


def get_xml_fields_to_strip(
    strip_fields: set[OptionalField],
) -> set[XmlField]:
    """Convert OptionalField set to the corresponding XmlField set."""
    xml_fields = set()
    for optional_field in strip_fields:
        xml_fields.update(OPTIONAL_FIELD_TO_XML[optional_field])
    return xml_fields


def get_yaml_fields_to_strip(
    strip_fields: set[OptionalField],
) -> set[YamlField]:
    """Convert OptionalField set to the corresponding YamlField set."""
    yaml_fields = set()
    for optional_field in strip_fields:
        yaml_fields.update(OPTIONAL_FIELD_TO_YAML[optional_field])
    return yaml_fields
