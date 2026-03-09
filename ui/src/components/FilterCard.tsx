import { useState } from 'react'
import type { Filter } from '../types'
import { FilterForm } from './FilterForm'

interface FilterCardProps {
  filter: Filter
  onChange: (filter: Filter) => void
  onDelete: () => void
  dragHandleProps?: React.HTMLAttributes<HTMLSpanElement>
}

export function FilterCard({ filter, onChange, onDelete, dragHandleProps }: FilterCardProps) {
  const [expanded, setExpanded] = useState(false)

  const summary = filter.name
    || [filter.criteria.from, filter.actions.label].filter(Boolean).join(' \u2192 ')
    || '(empty filter)'

  const tags: string[] = []
  if (filter.actions.should_mark_as_read) tags.push('read')
  if (filter.actions.should_archive) tags.push('archive')
  if (filter.actions.should_star) tags.push('star')
  if (filter.actions.should_trash) tags.push('trash')
  if (filter.actions.should_never_spam) tags.push('no spam')

  return (
    <div className={`filter-card ${expanded ? 'expanded' : ''}`}>
      <div className="filter-card-header" onClick={() => setExpanded(!expanded)}>
        <span className="drag-handle" {...dragHandleProps}>\u2261</span>
        <span className="filter-summary">{summary}</span>
        <span className="filter-tags">
          {tags.map((t) => (
            <span key={t} className="tag">{t}</span>
          ))}
        </span>
        <button
          className="btn-icon delete-btn"
          onClick={(e) => { e.stopPropagation(); onDelete() }}
          title="Delete filter"
        >
          \u00d7
        </button>
        <span className="expand-indicator">{expanded ? '\u25b4' : '\u25be'}</span>
      </div>
      {expanded && (
        <div className="filter-card-body">
          <FilterForm filter={filter} onChange={onChange} />
        </div>
      )}
    </div>
  )
}
