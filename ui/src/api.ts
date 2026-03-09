import type { FilterGroup, GroupedFilterCollection, Filter } from './types'

let nextId = 0
function genId(): string {
  return `_${++nextId}_${Date.now()}`
}

export function assignIds(collection: GroupedFilterCollection): GroupedFilterCollection {
  return {
    ...collection,
    groups: collection.groups.map((g: Omit<FilterGroup, 'id'> & { id?: string }) => ({
      ...g,
      id: g.id || genId(),
      filters: g.filters.map((f: Omit<Filter, 'id'> & { id?: string }) => ({
        ...f,
        id: f.id || genId(),
      })),
    })),
  }
}

export function stripIds(collection: GroupedFilterCollection): unknown {
  return {
    metadata: collection.metadata,
    groups: collection.groups.map((g) => ({
      name: g.name,
      filters: g.filters.map(({ id: _id, ...rest }) => rest),
    })),
  }
}

export async function fetchFiles(): Promise<string[]> {
  const res = await fetch('/api/files')
  return res.json()
}

export async function fetchFile(filename: string): Promise<GroupedFilterCollection> {
  const res = await fetch(`/api/file/${encodeURIComponent(filename)}`)
  if (!res.ok) throw new Error(`Failed to load ${filename}`)
  const data = await res.json()
  return assignIds(data)
}

export async function saveFile(filename: string, collection: GroupedFilterCollection): Promise<void> {
  const res = await fetch(`/api/file/${encodeURIComponent(filename)}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(stripIds(collection)),
  })
  if (!res.ok) throw new Error(`Failed to save ${filename}`)
}
