export interface FilterCriteria {
  from?: string
  to?: string
  subject?: string
  has_the_word?: string
}

export interface FilterActions {
  label?: string
  should_mark_as_read?: boolean
  should_archive?: boolean
  should_star?: boolean
  should_trash?: boolean
  should_never_spam?: boolean
}

export interface Filter {
  id: string // client-side UUID for DnD, not persisted
  name?: string
  criteria: FilterCriteria
  actions: FilterActions
}

export interface FilterGroup {
  id: string // client-side UUID for DnD, not persisted
  name: string
  filters: Filter[]
}

export interface Metadata {
  title?: string
  author?: { name: string; email: string }
}

export interface GroupedFilterCollection {
  metadata: Metadata
  groups: FilterGroup[]
}
