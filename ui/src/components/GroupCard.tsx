import { useState } from 'react'
import { useDroppable } from '@dnd-kit/core'
import { SortableContext, verticalListSortingStrategy, useSortable } from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import type { Filter, FilterGroup } from '../types'
import { FilterCard } from './FilterCard'

interface GroupCardProps {
  group: FilterGroup
  onUpdateGroup: (group: FilterGroup) => void
  onDeleteGroup: () => void
  onAddFilter: () => void
}

function SortableFilterCard({
  filter,
  onChange,
  onDelete,
}: {
  filter: Filter
  onChange: (f: Filter) => void
  onDelete: () => void
}) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: filter.id,
    data: { type: 'filter' },
  })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.4 : 1,
  }

  return (
    <div ref={setNodeRef} style={style} {...attributes}>
      <FilterCard
        filter={filter}
        onChange={onChange}
        onDelete={onDelete}
        dragHandleProps={listeners}
      />
    </div>
  )
}

export function GroupCard({ group, onUpdateGroup, onDeleteGroup, onAddFilter }: GroupCardProps) {
  const [collapsed, setCollapsed] = useState(false)
  const [editingName, setEditingName] = useState(false)

  const { setNodeRef } = useDroppable({
    id: `group-drop-${group.id}`,
    data: { type: 'group', groupId: group.id },
  })

  const updateFilter = (index: number, updated: Filter) => {
    const newFilters = [...group.filters]
    newFilters[index] = updated
    onUpdateGroup({ ...group, filters: newFilters })
  }

  const deleteFilter = (index: number) => {
    const newFilters = group.filters.filter((_, i) => i !== index)
    onUpdateGroup({ ...group, filters: newFilters })
  }

  const filterIds = group.filters.map((f) => f.id)

  return (
    <div className="group-card">
      <div className="group-header">
        <button className="btn-icon collapse-btn" onClick={() => setCollapsed(!collapsed)}>
          {collapsed ? '\u25b6' : '\u25bc'}
        </button>
        {editingName ? (
          <input
            className="group-name-input"
            value={group.name}
            onChange={(e) => onUpdateGroup({ ...group, name: e.target.value })}
            onBlur={() => setEditingName(false)}
            onKeyDown={(e) => e.key === 'Enter' && setEditingName(false)}
            autoFocus
          />
        ) : (
          <h3
            className="group-name"
            onClick={() => setEditingName(true)}
            title="Click to rename"
          >
            {group.name || '(unnamed group)'}
          </h3>
        )}
        <span className="group-count">{group.filters.length}</span>
        <button
          className="btn-icon delete-btn"
          onClick={onDeleteGroup}
          title="Delete group"
        >
          \u00d7
        </button>
      </div>

      {!collapsed && (
        <div className="group-body" ref={setNodeRef}>
          <SortableContext items={filterIds} strategy={verticalListSortingStrategy}>
            {group.filters.map((filter, i) => (
              <SortableFilterCard
                key={filter.id}
                filter={filter}
                onChange={(f) => updateFilter(i, f)}
                onDelete={() => deleteFilter(i)}
              />
            ))}
          </SortableContext>
          <button className="btn add-filter-btn" onClick={onAddFilter}>
            + Add filter
          </button>
        </div>
      )}
    </div>
  )
}
