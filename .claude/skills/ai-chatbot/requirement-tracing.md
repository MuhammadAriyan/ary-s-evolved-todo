# Requirement Tracing Skill

## Purpose
Track implementation progress against spec requirements, map code to functional requirements, and generate coverage reports.

## Traceability Matrix

### 1. Requirement Categories
```markdown
## AI Todo Chatbot Requirements (28 FRs)

### Agent System (FR-001 to FR-010)
| ID | Requirement | Implementation | Tests | Status |
|----|-------------|----------------|-------|--------|
| FR-001 | Main Orchestrator routes by language | orchestrator.py | test_agents.py | ⬜ |
| FR-002 | English Agent (Miyu) handles English | language_agents.py | test_agents.py | ⬜ |
| FR-003 | Urdu Agent (Riven) handles Urdu | language_agents.py | test_agents.py | ⬜ |
| FR-004 | AddTaskAgent (Elara) creates tasks | task_agents.py | test_agents.py | ⬜ |
| FR-005 | ListTasksAgent (Kael) lists tasks | task_agents.py | test_agents.py | ⬜ |
| FR-006 | CompleteTaskAgent (Nyra) completes | task_agents.py | test_agents.py | ⬜ |
| FR-007 | DeleteTaskAgent (Taro) deletes | task_agents.py | test_agents.py | ⬜ |
| FR-008 | UpdateTaskAgent (Lys) updates | task_agents.py | test_agents.py | ⬜ |
| FR-009 | AnalyticsAgent (Orion) shows stats | task_agents.py | test_agents.py | ⬜ |
| FR-010 | SearchAgent (Vera) searches tasks | task_agents.py | test_agents.py | ⬜ |

### MCP Tools (FR-011 to FR-018)
| ID | Requirement | Implementation | Tests | Status |
|----|-------------|----------------|-------|--------|
| FR-011 | add_task creates with user isolation | task_tools.py | test_mcp_tools.py | ⬜ |
| FR-012 | list_tasks queries with filters | task_tools.py | test_mcp_tools.py | ⬜ |
| FR-013 | complete_task marks completed | task_tools.py | test_mcp_tools.py | ⬜ |
| FR-014 | delete_task removes task | task_tools.py | test_mcp_tools.py | ⬜ |
| FR-015 | update_task modifies properties | task_tools.py | test_mcp_tools.py | ⬜ |
| FR-016 | uncomplete_task reopens task | task_tools.py | test_mcp_tools.py | ⬜ |
| FR-017 | get_task_analytics returns stats | task_tools.py | test_mcp_tools.py | ⬜ |
| FR-018 | search_tasks keyword search | task_tools.py | test_mcp_tools.py | ⬜ |

### Chat UI (FR-019 to FR-024)
| ID | Requirement | Implementation | Tests | Status |
|----|-------------|----------------|-------|--------|
| FR-019 | Glass theme chat interface | chat/page.tsx | chat.test.tsx | ⬜ |
| FR-020 | Voice input (English + Urdu) | VoiceInput.tsx | voice.test.tsx | ⬜ |
| FR-021 | Agent icons in messages | AgentMessage.tsx | message.test.tsx | ⬜ |
| FR-022 | Conversation sidebar | ConversationList.tsx | sidebar.test.tsx | ⬜ |
| FR-023 | Max 100 conversations | ConversationList.tsx | limits.test.tsx | ⬜ |
| FR-024 | AI-generated titles | chat.py | title.test.py | ⬜ |

### API & Infrastructure (FR-025 to FR-028)
| ID | Requirement | Implementation | Tests | Status |
|----|-------------|----------------|-------|--------|
| FR-025 | Rate limiting 5/min | rate_limit.py | test_rate_limit.py | ⬜ |
| FR-026 | 1000 char message limit | chat.py | test_chat.py | ⬜ |
| FR-027 | Stateless chat endpoint | chat.py | test_chat.py | ⬜ |
| FR-028 | Conversation persistence | conversation.py | test_db.py | ⬜ |
```

### 2. Status Legend
```
⬜ Not Started
🟡 In Progress
🟢 Implemented
✅ Tested
✅✅ Verified (acceptance criteria passed)
```

### 3. Coverage Report Template
```markdown
# Implementation Coverage Report

**Date**: YYYY-MM-DD
**Feature**: AI Todo Chatbot (005)
**Branch**: 005-ai-todo-chatbot

## Summary
- Total Requirements: 28
- Implemented: X (X%)
- Tested: X (X%)
- Verified: X (X%)

## By Category
| Category | Total | Impl | Tested | Coverage |
|----------|-------|------|--------|----------|
| Agent System | 10 | 0 | 0 | 0% |
| MCP Tools | 8 | 0 | 0 | 0% |
| Chat UI | 6 | 0 | 0 | 0% |
| API/Infra | 4 | 0 | 0 | 0% |

## Blockers
- [ ] None identified

## Next Actions
1. Implement FR-001: Main Orchestrator
2. Implement FR-011: add_task tool
3. Implement FR-019: Chat interface
```

### 4. Acceptance Criteria Checklist
```markdown
## FR-001: Main Orchestrator

### Acceptance Criteria
- [ ] Detects English messages correctly
- [ ] Detects Urdu messages correctly
- [ ] Routes English to Miyu (EnglishAgent)
- [ ] Routes Urdu to Riven (UrduAgent)
- [ ] Returns agent icon (🤖) in metadata
- [ ] Handles mixed-language gracefully

### Test Cases
- [ ] test_routes_english_to_miyu
- [ ] test_routes_urdu_to_riven
- [ ] test_handles_mixed_language
- [ ] test_returns_agent_metadata

### Implementation Files
- [ ] backend/app/services/ai/agents/orchestrator.py
- [ ] backend/tests/unit/test_agents.py
```

### 5. Code-to-Requirement Mapping
```python
# Add to source files for traceability
"""
Implements: FR-001, FR-002, FR-003
Tests: test_agents.py::TestMainOrchestrator
"""

class MainOrchestrator:
    """
    Main orchestrator agent (Aren 🤖)

    Requirements:
    - FR-001: Routes messages to language agents based on detected language
    """
    pass
```

### 6. Automated Tracing Script
```bash
#!/bin/bash
# scripts/trace-requirements.sh

echo "=== Requirement Traceability Report ==="
echo ""

# Count implementations
echo "## Implementation Status"
for fr in FR-{001..028}; do
    count=$(grep -r "$fr" backend/app --include="*.py" | wc -l)
    if [ $count -gt 0 ]; then
        echo "✅ $fr: $count references"
    else
        echo "⬜ $fr: Not implemented"
    fi
done

echo ""
echo "## Test Coverage"
for fr in FR-{001..028}; do
    count=$(grep -r "$fr" backend/tests --include="*.py" | wc -l)
    if [ $count -gt 0 ]; then
        echo "✅ $fr: $count test references"
    else
        echo "⬜ $fr: No tests"
    fi
done
```

## Workflow
1. **Before Implementation**: Review requirement in spec.md
2. **During Implementation**: Add FR-XXX comments to code
3. **After Implementation**: Update traceability matrix
4. **After Testing**: Mark as tested with test file reference
5. **After Verification**: Check all acceptance criteria
