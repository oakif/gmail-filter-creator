"""Data models for filters."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(kw_only=True)
class Author:
    name: str
    email: str


@dataclass(kw_only=True)
class Metadata:
    title: str
    author: Author
    id: str
    updated_time: str

    def __post_init__(self) -> None:
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
    id: str
    updated_time: str
    criteria: FilterCriteria = field(default_factory=FilterCriteria)
    actions: FilterActions = field(default_factory=FilterActions)

    def __post_init__(self) -> None:
        Metadata._validate_iso8601(self.updated_time)
        if not self._has_any_property():
            raise ValueError('Filter must have at least one criteria or action property')

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
