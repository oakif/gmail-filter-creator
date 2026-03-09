import { useCallback, useEffect, useState } from 'react'
import {
  DndContext,
  DragOverlay,
  closestCenter,
  PointerSensor,
  useSensor,
  useSensors,
  type DragEndEvent,
  type DragOverEvent,
  type DragStartEvent,
} from '@dnd-kit/core'
import { GroupCard } from './components/GroupCard'
import { fetchFiles, fetchFile, saveFile } from './api'
import type { Filter, FilterGroup, GroupedFilterCollection } from './types'
import './App.css'

let nextId = 1000
function genId() {
  return `_new_${++nextId}_${Date.now()}`
}

function makeEmptyFilter(): Filter {
  return { id: genId(), criteria: {}, actions: {} }
}

export default function App() {
  const [files, setFiles] = useState<string[]>([])
  const [currentFile, setCurrentFile] = useState<string>('')
  const [data, setData] = useState<GroupedFilterCollection | null>(null)
  const [dirty, setDirty] = useState(false)
  const [saving, setSaving] = useState(false)
  const [activeId, setActiveId] = useState<string | null>(null)

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 5 } }),
  )

  useEffect(() => {
    fetchFiles().then((f) => {
      setFiles(f)
      if (f.length > 0) setCurrentFile(f[0])
    })
  }, [])

  useEffect(() => {
    if (!currentFile) return
    fetchFile(currentFile).then((d) => {
      setData(d)
      setDirty(false)
    })
  }, [currentFile])

  const update = useCallback((fn: (d: GroupedFilterCollection) => GroupedFilterCollection) => {
    setData((prev) => {
      if (!prev) return prev
      setDirty(true)
      return fn(prev)
    })
  }, [])

  const updateGroup = (groupIndex: number, group: FilterGroup) => {
    update((d) => ({
      ...d,
      groups: d.groups.map((g, i) => (i === groupIndex ? group : g)),
    }))
  }

  const deleteGroup = (groupIndex: number) => {
    update((d) => ({
      ...d,
      groups: d.groups.filter((_, i) => i !== groupIndex),
    }))
  }

  const addFilter = (groupIndex: number) => {
    update((d) => ({
      ...d,
      groups: d.groups.map((g, i) =>
        i === groupIndex ? { ...g, filters: [...g.filters, makeEmptyFilter()] } : g,
      ),
    }))
  }

  const addGroup = () => {
    update((d) => ({
      ...d,
      groups: [...d.groups, { id: genId(), name: 'New Group', filters: [] }],
    }))
  }

  const handleSave = async () => {
    if (!data || !currentFile) return
    setSaving(true)
    try {
      await saveFile(currentFile, data)
      setDirty(false)
    } catch (e) {
      alert(`Save failed: ${e}`)
    } finally {
      setSaving(false)
    }
  }

  // DnD helpers
  const findFilterLocation = (filterId: string): { groupIndex: number; filterIndex: number } | null => {
    if (!data) return null
    for (let gi = 0; gi < data.groups.length; gi++) {
      const fi = data.groups[gi].filters.findIndex((f) => f.id === filterId)
      if (fi !== -1) return { groupIndex: gi, filterIndex: fi }
    }
    return null
  }

  const handleDragStart = (event: DragStartEvent) => {
    setActiveId(event.active.id as string)
  }

  const handleDragOver = (event: DragOverEvent) => {
    const { active, over } = event
    if (!over || !data) return

    const activeFilter = findFilterLocation(active.id as string)
    if (!activeFilter) return

    let targetGroupIndex: number | null = null

    const overFilter = findFilterLocation(over.id as string)
    if (overFilter) {
      targetGroupIndex = overFilter.groupIndex
    }

    const overData = over.data?.current
    if (overData?.type === 'group') {
      const gid = overData.groupId
      targetGroupIndex = data.groups.findIndex((g) => g.id === gid)
    }

    if (targetGroupIndex === null || targetGroupIndex === activeFilter.groupIndex) return

    update((d) => {
      const sourceGroup = d.groups[activeFilter.groupIndex]
      const filter = sourceGroup.filters[activeFilter.filterIndex]
      const newSource = { ...sourceGroup, filters: sourceGroup.filters.filter((_, i) => i !== activeFilter.filterIndex) }

      const targetGroup = d.groups[targetGroupIndex!]
      const insertIndex = overFilter ? overFilter.filterIndex : targetGroup.filters.length
      const newTarget = {
        ...targetGroup,
        filters: [...targetGroup.filters.slice(0, insertIndex), filter, ...targetGroup.filters.slice(insertIndex)],
      }

      return {
        ...d,
        groups: d.groups.map((g, i) => {
          if (i === activeFilter.groupIndex) return newSource
          if (i === targetGroupIndex) return newTarget
          return g
        }),
      }
    })
  }

  const handleDragEnd = (event: DragEndEvent) => {
    setActiveId(null)
    const { active, over } = event
    if (!over || !data || active.id === over.id) return

    const activeFilter = findFilterLocation(active.id as string)
    const overFilter = findFilterLocation(over.id as string)
    if (!activeFilter || !overFilter) return
    if (activeFilter.groupIndex !== overFilter.groupIndex) return

    update((d) => {
      const group = d.groups[activeFilter.groupIndex]
      const newFilters = [...group.filters]
      const [moved] = newFilters.splice(activeFilter.filterIndex, 1)
      newFilters.splice(overFilter.filterIndex, 0, moved)
      return {
        ...d,
        groups: d.groups.map((g, i) =>
          i === activeFilter.groupIndex ? { ...g, filters: newFilters } : g,
        ),
      }
    })
  }

  const activeFilter = activeId && data
    ? data.groups.flatMap((g) => g.filters).find((f) => f.id === activeId)
    : null

  if (!data) return <div className="loading">Loading...</div>

  return (
    <div className="app">
      <header className="toolbar">
        <select value={currentFile} onChange={(e) => setCurrentFile(e.target.value)}>
          {files.map((f) => (
            <option key={f} value={f}>{f}</option>
          ))}
        </select>
        <div className="toolbar-right">
          {dirty && <span className="unsaved-badge">Unsaved changes</span>}
          <button className="btn btn-primary" onClick={handleSave} disabled={!dirty || saving}>
            {saving ? 'Saving...' : 'Save'}
          </button>
        </div>
      </header>

      {data.metadata.title && (
        <div className="metadata-bar">
          <span className="metadata-title">{data.metadata.title}</span>
          {data.metadata.author && (
            <span className="metadata-author">
              {data.metadata.author.name} &lt;{data.metadata.author.email}&gt;
            </span>
          )}
        </div>
      )}

      <DndContext
        sensors={sensors}
        collisionDetection={closestCenter}
        onDragStart={handleDragStart}
        onDragOver={handleDragOver}
        onDragEnd={handleDragEnd}
      >
        <div className="groups">
          {data.groups.map((group, gi) => (
            <GroupCard
              key={group.id}
              group={group}
              onUpdateGroup={(g) => updateGroup(gi, g)}
              onDeleteGroup={() => deleteGroup(gi)}
              onAddFilter={() => addFilter(gi)}
            />
          ))}
        </div>

        <DragOverlay>
          {activeFilter && (
            <div className="filter-card dragging">
              <div className="filter-card-header">
                <span className="drag-handle">{'\u2261'}</span>
                <span className="filter-summary">
                  {activeFilter.name || activeFilter.criteria.from || '(filter)'}
                </span>
              </div>
            </div>
          )}
        </DragOverlay>
      </DndContext>

      <div className="add-group-area">
        <button className="btn" onClick={addGroup}>+ Add group</button>
      </div>
    </div>
  )
}
