"""Data models for filters."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(kw_only=True)
class Author:
    name: str
    email: str


@dataclass(kw_only=True)
class Metadata:
    title: str | None = None
    author: Author | None = None
    id: str | None = None
    updated_time: str | None = None

    def __post_init__(self) -> None:
        if self.updated_time:
            self._validate_iso8601(self.updated_time)

    @staticmethod
    def _validate_iso8601(timestamp: str) -> None:
        try:
            datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError(f'Invalid ISO 8601 timestamp: {timestamp}')


@dataclass(kw_only=True)
class FilterCriteria:
    from_: str | None = None
    to: str | None = None
    subject: str | None = None
    has_the_word: str | None = None


@dataclass(kw_only=True)
class FilterActions:
    label: str | None = None
    should_mark_as_read: bool | None = None
    should_archive: bool | None = None
    should_star: bool | None = None
    should_trash: bool | None = None
    should_never_spam: bool | None = None


@dataclass(kw_only=True)
class Filter:
    name: str | None = None
    criteria: FilterCriteria = field(default_factory=FilterCriteria)
    actions: FilterActions = field(default_factory=FilterActions)
    id: str | None = None
    updated_time: str | None = None

    def __post_init__(self) -> None:
        if self.updated_time:
            Metadata._validate_iso8601(self.updated_time)
        if not self._has_any_property():
            raise ValueError('Filter must have at least one criteria or action property')

    def get_name(self) -> str:
        if self.name:
            return self.name
        from .name_generator import generate_filter_name
        return generate_filter_name(self.criteria, self.actions)

    def _has_any_property(self) -> bool:
        return any(
            (
                self.criteria.from_,
                self.criteria.to,
                self.criteria.subject,
                self.criteria.has_the_word,
                self.actions.label,
                self.actions.should_mark_as_read,
                self.actions.should_archive,
                self.actions.should_star,
                self.actions.should_trash,
                self.actions.should_never_spam,
            ),
        )


@dataclass(kw_only=True)
class GmailFilterCollection:
    metadata: Metadata
    filters: list[Filter] = field(default_factory=list)


@dataclass(kw_only=True)
class FilterGroup:
    name: str
    filters: list[Filter] = field(default_factory=list)


@dataclass(kw_only=True)
class GroupedFilterCollection:
    metadata: Metadata
    groups: list[FilterGroup] = field(default_factory=list)
