"""FastAPI server for the Gmail Filter YAML Editor UI."""

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .grouped_yaml_serializer import serialize_grouped_filter_collection_to_yaml
from .models import (
    Author,
    Filter,
    FilterActions,
    FilterCriteria,
    FilterGroup,
    GroupedFilterCollection,
    Metadata,
)
from .yaml_parser import parse_yaml_to_grouped_filter_collection

DATA_DIR = Path(os.environ.get('GMAIL_FILTER_DATA_DIR', 'data'))

app = FastAPI(title='Gmail Filter Editor')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)


# Pydantic models for JSON API

class AuthorModel(BaseModel):
    name: str = ''
    email: str = ''


class MetadataModel(BaseModel):
    title: str | None = None
    author: AuthorModel | None = None


class CriteriaModel(BaseModel):
    from_field: str | None = Field(None, alias='from')
    to: str | None = None
    subject: str | None = None
    has_the_word: str | None = None

    model_config = {'populate_by_name': True}


class ActionsModel(BaseModel):
    label: str | None = None
    should_mark_as_read: bool | None = None
    should_archive: bool | None = None
    should_star: bool | None = None
    should_trash: bool | None = None
    should_never_spam: bool | None = None


class FilterModel(BaseModel):
    name: str | None = None
    criteria: CriteriaModel = CriteriaModel()
    actions: ActionsModel = ActionsModel()


class GroupModel(BaseModel):
    name: str = ''
    filters: list[FilterModel] = []


class GroupedCollectionModel(BaseModel):
    metadata: MetadataModel = MetadataModel()
    groups: list[GroupModel] = []


# Conversion helpers

def _collection_to_response(collection: GroupedFilterCollection) -> dict:
    metadata = {}
    if collection.metadata.title:
        metadata['title'] = collection.metadata.title
    if collection.metadata.author:
        metadata['author'] = {
            'name': collection.metadata.author.name,
            'email': collection.metadata.author.email,
        }

    groups = []
    for group in collection.groups:
        filters = []
        for f in group.filters:
            filter_dict = {'name': f.name}
            criteria = {}
            if f.criteria.from_:
                criteria['from'] = f.criteria.from_
            if f.criteria.to:
                criteria['to'] = f.criteria.to
            if f.criteria.subject:
                criteria['subject'] = f.criteria.subject
            if f.criteria.has_the_word:
                criteria['has_the_word'] = f.criteria.has_the_word
            filter_dict['criteria'] = criteria

            actions = {}
            if f.actions.label:
                actions['label'] = f.actions.label
            if f.actions.should_mark_as_read is not None:
                actions['should_mark_as_read'] = f.actions.should_mark_as_read
            if f.actions.should_archive is not None:
                actions['should_archive'] = f.actions.should_archive
            if f.actions.should_star is not None:
                actions['should_star'] = f.actions.should_star
            if f.actions.should_trash is not None:
                actions['should_trash'] = f.actions.should_trash
            if f.actions.should_never_spam is not None:
                actions['should_never_spam'] = f.actions.should_never_spam
            filter_dict['actions'] = actions
            filters.append(filter_dict)

        groups.append({'name': group.name, 'filters': filters})

    return {'metadata': metadata, 'groups': groups}


def _request_to_collection(data: GroupedCollectionModel) -> GroupedFilterCollection:
    author = None
    if data.metadata.author:
        author = Author(
            name=data.metadata.author.name,
            email=data.metadata.author.email,
        )

    metadata = Metadata(
        title=data.metadata.title,
        author=author,
    )

    groups = []
    for g in data.groups:
        filters = []
        for f in g.filters:
            criteria = FilterCriteria(
                from_=f.criteria.from_field,
                to=f.criteria.to,
                subject=f.criteria.subject,
                has_the_word=f.criteria.has_the_word,
            )
            actions = FilterActions(
                label=f.actions.label,
                should_mark_as_read=f.actions.should_mark_as_read,
                should_archive=f.actions.should_archive,
                should_star=f.actions.should_star,
                should_trash=f.actions.should_trash,
                should_never_spam=f.actions.should_never_spam,
            )
            filters.append(Filter(
                name=f.name,
                criteria=criteria,
                actions=actions,
            ))
        groups.append(FilterGroup(name=g.name, filters=filters))

    return GroupedFilterCollection(metadata=metadata, groups=groups)


def _validate_filename(filename: str) -> Path:
    if '/' in filename or '\\' in filename or '..' in filename:
        raise HTTPException(status_code=400, detail='Invalid filename')
    path = DATA_DIR / filename
    if not path.suffix == '.yaml':
        raise HTTPException(status_code=400, detail='Only .yaml files are supported')
    return path


# API endpoints

@app.get('/api/files')
def list_files() -> list[str]:
    if not DATA_DIR.exists():
        return []
    return sorted(f.name for f in DATA_DIR.glob('*.yaml'))


@app.get('/api/file/{filename}')
def get_file(filename: str) -> dict:
    path = _validate_filename(filename)
    if not path.exists():
        raise HTTPException(status_code=404, detail='File not found')
    collection = parse_yaml_to_grouped_filter_collection(path)
    return _collection_to_response(collection)


@app.put('/api/file/{filename}')
def save_file(filename: str, data: GroupedCollectionModel) -> dict:
    path = _validate_filename(filename)
    collection = _request_to_collection(data)
    serialize_grouped_filter_collection_to_yaml(collection, path)
    return {'status': 'ok'}


# Serve frontend static files in production
UI_DIST = Path(__file__).parent.parent / 'ui' / 'dist'
if UI_DIST.exists():
    app.mount('/', StaticFiles(directory=str(UI_DIST), html=True), name='ui')
