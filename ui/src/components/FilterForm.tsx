import type { Filter } from '../types'

interface FilterFormProps {
  filter: Filter
  onChange: (filter: Filter) => void
}

export function FilterForm({ filter, onChange }: FilterFormProps) {
  const updateCriteria = (field: string, value: string) => {
    onChange({
      ...filter,
      criteria: { ...filter.criteria, [field]: value || undefined },
    })
  }

  const updateActions = (field: string, value: string | boolean | undefined) => {
    onChange({
      ...filter,
      actions: { ...filter.actions, [field]: value },
    })
  }

  const toggleAction = (field: string) => {
    const current = filter.actions[field as keyof typeof filter.actions] as boolean | undefined
    // Cycle: undefined -> true -> false -> undefined
    const next = current === undefined ? true : current === true ? false : undefined
    updateActions(field, next)
  }

  return (
    <div className="filter-form">
      <div className="form-row">
        <label>Name</label>
        <input
          type="text"
          value={filter.name || ''}
          onChange={(e) => onChange({ ...filter, name: e.target.value || undefined })}
          placeholder="Auto-generated if empty"
        />
      </div>

      <fieldset>
        <legend>Criteria</legend>
        <div className="form-row">
          <label>From</label>
          <input
            type="text"
            value={filter.criteria.from || ''}
            onChange={(e) => updateCriteria('from', e.target.value)}
            placeholder="sender@example.com"
          />
        </div>
        <div className="form-row">
          <label>To</label>
          <input
            type="text"
            value={filter.criteria.to || ''}
            onChange={(e) => updateCriteria('to', e.target.value)}
            placeholder="recipient@example.com"
          />
        </div>
        <div className="form-row">
          <label>Subject</label>
          <textarea
            value={filter.criteria.subject || ''}
            onChange={(e) => updateCriteria('subject', e.target.value)}
            placeholder='"exact phrase" or keyword'
            rows={2}
          />
        </div>
        <div className="form-row">
          <label>Has the word</label>
          <textarea
            value={filter.criteria.has_the_word || ''}
            onChange={(e) => updateCriteria('has_the_word', e.target.value)}
            placeholder='"word1" AND "word2"'
            rows={2}
          />
        </div>
      </fieldset>

      <fieldset>
        <legend>Actions</legend>
        <div className="form-row">
          <label>Label</label>
          <input
            type="text"
            value={filter.actions.label || ''}
            onChange={(e) => updateActions('label', e.target.value || undefined)}
            placeholder="Category/Subcategory"
          />
        </div>
        <div className="checkbox-row">
          {([
            ['should_mark_as_read', 'Mark as read'],
            ['should_archive', 'Archive'],
            ['should_star', 'Star'],
            ['should_trash', 'Trash'],
            ['should_never_spam', 'Never spam'],
          ] as const).map(([field, label]) => {
            const value = filter.actions[field]
            return (
              <button
                key={field}
                type="button"
                className={`toggle-btn ${value === true ? 'on' : value === false ? 'off' : 'unset'}`}
                onClick={() => toggleAction(field)}
                title={value === undefined ? 'Unset (click to enable)' : value ? 'Enabled (click to disable)' : 'Disabled (click to unset)'}
              >
                {label}
                <span className="toggle-state">
                  {value === true ? ' \u2713' : value === false ? ' \u2717' : ''}
                </span>
              </button>
            )
          })}
        </div>
      </fieldset>
    </div>
  )
}
