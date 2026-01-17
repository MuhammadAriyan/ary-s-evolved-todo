---
name: validate-todo
description: Validates todo operations for correctness and completeness. Use after implementing any todo CRUD operation to verify input validation, output formatting, and edge cases.
---

# Skill: validate-todo

Validates todo operations for correctness and completeness.

## When to use

After implementing any todo operation, use this skill to verify:
- CRUD operations work correctly
- Input validation catches all edge cases
- Output formatting matches specifications
- Sorting and filtering produce expected results

## Validation checklist

### For add operation
- [ ] Title validation: non-empty, 1-200 chars
- [ ] Priority normalization: H/h/High → "High", etc.
- [ ] Date validation: YYYY-MM-DD format
- [ ] Tags parsing: split by comma, strip, filter empty
- [ ] Auto-increment ID assigned correctly

### For delete operation
- [ ] Takes task_id as parameter
- [ ] Returns True on success, False if not found
- [ ] Task removed from tasks list

### For update operation
- [ ] Takes task_id and **updates kwargs
- [ ] Updates only provided fields
- [ ] Validation applies to updated values

### For list operations
- [ ] list_all() returns all tasks
- [ ] list_pending() returns only incomplete
- [ ] list_completed() returns only complete
- [ ] Tasks are sorted by priority (H→M→L), then ID

### For complete operation
- [ ] Takes task_id parameter
- [ ] Toggles completed status
- [ ] Returns True on success, False if not found

### For search operation
- [ ] Case-insensitive search in title and description
- [ ] Returns list of matching tasks
- [ ] Returns empty list if no matches

### For filter operations
- [ ] filter_by_priority() matches priority level
- [ ] filter_by_tag() case-insensitive exact match
- [ ] Both return sorted lists
