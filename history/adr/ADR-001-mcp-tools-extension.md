# ADR-001: MCP Tools Extension Beyond Constitution Baseline

- **Status:** Accepted
- **Date:** 2026-01-11
- **Feature:** 005-ai-todo-chatbot
- **Context:** Constitution principle III specifies "Exactly 5 tools for basic todo operations—no more, no less" but the AI Todo Chatbot feature requires 8 tools to fulfill all functional requirements.

## Decision

Extend the MCP tools set from 5 to 8 tools for the AI Todo Chatbot feature:

**Original 5 (Constitution Baseline):**
1. `add_task` - Create a new task
2. `list_tasks` - Retrieve tasks for authenticated user
3. `complete_task` - Mark task as completed
4. `delete_task` - Remove a task
5. `update_task` - Modify task details

**Additional 3 (Feature Extension):**
6. `uncomplete_task` - Reopen a completed task (FR-006)
7. `get_task_analytics` - Return task statistics (FR-007)
8. `search_tasks` - Search tasks by keyword (FR-008)

The additional tools are **additive extensions**, not replacements. The original 5 tools remain unchanged and form the core CRUD operations. The 3 new tools provide enhanced functionality required by the spec.

## Consequences

### Positive

- Enables full feature set specified in spec.md (FR-006, FR-007, FR-008)
- Maintains backward compatibility (original 5 tools unchanged)
- Provides better user experience (undo completions, view stats, search)
- Follows same patterns as baseline tools (stateless, user-isolated)

### Negative

- Deviates from constitution's "exactly 5" constraint
- Sets precedent for future tool additions
- Increases MCP server surface area (more code to maintain)

## Alternatives Considered

**Alternative A: Strict 5-tool compliance**
- Combine `uncomplete_task` into `update_task` with status parameter
- Omit analytics and search features
- **Rejected**: Would reduce feature value and user experience; spec explicitly requires these capabilities

**Alternative B: Amend constitution**
- Change principle III to "5 basic tools + additional as needed"
- **Deferred**: Constitution amendment requires formal process; this ADR documents the justified deviation for this feature

**Alternative C: Accept deviation with documentation (Chosen)**
- Keep 8 tools as implemented
- Document rationale in ADR
- Constitution remains unchanged but deviation is formally justified

## References

- Feature Spec: [spec.md](../../specs/005-ai-todo-chatbot/spec.md) (FR-006, FR-007, FR-008)
- Implementation Plan: [plan.md](../../specs/005-ai-todo-chatbot/plan.md) (L33-36 justification)
- Related ADRs: None
- Evaluator Evidence: [0008-cross-artifact-analysis.misc.prompt.md](../prompts/005-ai-todo-chatbot/0008-cross-artifact-analysis.misc.prompt.md)
