---
description: Perform bidirectional requirement traceability analysis (CODE ↔ REQUIREMENTS) and optionally fix gaps with specialized agents.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Goal

Perform bidirectional requirement traceability analysis:
- **CODE → REQ**: Verify code files have FR-XXX annotations that map to spec requirements
- **REQ → CODE**: Verify spec requirements have corresponding code implementations

When **CODE → REQ = REQ → CODE**: Output "✅ Requirement Completed"
When gaps exist: Show analysis, ask user approval, invoke appropriate fix agents

## Execution Steps

### 1. Parse Input & Determine Scope

Parse `$ARGUMENTS` to determine tracing scope:

| Input Pattern | Scope Type | Action |
|---------------|------------|--------|
| (empty) | Auto-detect | Get feature from current git branch |
| `all` | All features | Scan all `specs/*/spec.md` |
| `XXX-feature-name` | Single feature | Trace `specs/XXX-feature-name/` |
| `FR-001` | Single requirement | Trace specific FR-XXX |
| `FR-001,FR-005,FR-010` | Multiple requirements | Trace listed FR-XXX |
| Natural language | Semantic search | Match query to FR-XXX descriptions |

**Natural Language Detection:**
If input doesn't match patterns above (not empty, not "all", not feature name, not FR-XXX):
- Treat as natural language query
- Extract keywords
- Search spec.md for matching requirement descriptions
- Report matched FR-XXX with relevance scores

### 2. Locate Spec Files

For the determined scope:

```bash
# Auto-detect from branch
git branch --show-current  # e.g., "005-ai-todo-chatbot"

# Find spec file
SPEC_PATH="specs/${FEATURE}/spec.md"
```

If spec file not found, abort with:
```
❌ Spec file not found: specs/${FEATURE}/spec.md

Run /sp.specify to create the specification first.
```

### 3. Extract Requirements from Spec

Read spec.md and extract all FR-XXX requirements:

**Primary Pattern:**
```regex
- \*\*FR-(\d{3})\*\*: (.+?)(?=\n- \*\*FR-|\n###|\n##|\Z)
```

**Build Registry:**
```
{
  "FR-001": {
    "description": "Create tasks via natural language",
    "category": "Core Chat Functionality",
    "line": 145,
    "acceptance_criteria": [...]
  },
  ...
}
```

### 4. Scan Code for FR-XXX Annotations

Search for annotation patterns in code files:

**Python files** (`backend/**/*.py`):
```bash
grep -rn "Implements: FR-" backend/ --include="*.py"
```

Patterns to match:
```python
"""
Implements: FR-001, FR-002
"""
# Implements: FR-001
# Requirements: FR-001
```

**TypeScript files** (`frontend/**/*.{ts,tsx}`):
```bash
grep -rn "Implements: FR-" frontend/ --include="*.ts" --include="*.tsx"
```

Patterns to match:
```typescript
/**
 * Implements: FR-019
 */
// Implements: FR-019
```

**Build Code Registry:**
```
{
  "backend/app/services/ai/tools/task_tools.py": ["FR-001", "FR-002"],
  "frontend/app/(protected)/chat/components/ChatContainer.tsx": ["FR-019"],
  ...
}
```

### 5. Perform Bidirectional Matching

```python
spec_frs = set(requirements.keys())      # All FR-XXX from spec
code_frs = set(all_annotated_frs)        # All FR-XXX from code

matched = spec_frs & code_frs            # ✅ Both directions match
unimplemented = spec_frs - code_frs      # ❌ REQ → CODE gap
orphan = code_frs - spec_frs             # ⚠️ CODE → REQ gap
```

### 6. Generate Traceability Report

#### 6.1 Traceability Matrix

```markdown
## Traceability Matrix: [feature-name]

| FR-ID | Description | Status | Implementation Files | Fix Agent |
|-------|-------------|--------|---------------------|-----------|
| FR-001 | Create tasks via NL | ✅ Traced | task_tools.py | - |
| FR-002 | List tasks with filters | ✅ Traced | task_tools.py | - |
| FR-019 | Glass theme chat UI | ❌ Missing | - | chat-frontend-engineer |
```

#### 6.2 Gap Analysis

```markdown
## Gap Analysis

### Unimplemented Requirements (REQ → CODE gaps)

| FR-ID | Category | Description | Suggested Files | Fix Agent |
|-------|----------|-------------|-----------------|-----------|
| FR-019 | Chat UI | Glass theme interface | ChatContainer.tsx | chat-frontend-engineer |

### Orphan Annotations (CODE → REQ gaps)

| File | Annotated FR-IDs | Action |
|------|------------------|--------|
| (none) | - | - |
```

#### 6.3 Coverage Metrics

```markdown
## Coverage Summary

- **Total Requirements**: 28
- **Traced**: 10 (35.7%)
- **Missing**: 18
- **Orphan Annotations**: 0

### By Category
| Category | Total | Traced | Coverage |
|----------|-------|--------|----------|
| Agent System | 10 | 5 | 50% |
| MCP Tools | 8 | 3 | 37.5% |
| Chat UI | 6 | 1 | 16.7% |
| API/Infra | 4 | 1 | 25% |
```

### 7. Natural Language Query Output (if applicable)

When input was a natural language query:

```markdown
## Query Analysis

Your query: "[user's question]"

### Matched Requirements

| FR-ID | Description | Relevance | Status |
|-------|-------------|-----------|--------|
| FR-019 | Redirect button navigates to dashboard | High | ❌ Missing |
| FR-022 | Navigation sidebar with links | Medium | ✅ Traced |

### Traceability Check: FR-019

| Aspect | Status | Details |
|--------|--------|---------|
| Spec Definition | ✅ Found | specs/005-ai-todo-chatbot/spec.md:L145 |
| Code Annotation | ❌ Missing | No file contains "Implements: FR-019" |
| Test Coverage | ❌ Missing | No test references FR-019 |

**Result:** FR-019 is NOT implemented (no code annotation found)
```

### 8. Determine Outcome

**If all requirements traced (matched == spec_frs):**

```markdown
✅ Requirement Traceability Complete

All [N] requirements are fully traced:
- CODE → REQ: All code annotations map to valid requirements
- REQ → CODE: All requirements have code implementations

Coverage: 100% ([N]/[N])
```

**If gaps exist:**

Continue to Step 9.

### 9. Generate Fix Recommendations

For each unimplemented requirement, determine:

1. **Suggested implementation file** based on category:
   - Agent System → `backend/app/services/ai/agents/*.py`
   - MCP Tools → `backend/app/services/ai/tools/*.py`
   - Chat UI → `frontend/app/(protected)/chat/components/*.tsx`
   - API/Infra → `backend/app/api/v1/endpoints/*.py`

2. **Fix agent** based on file pattern:

| File Pattern | Fix Agent |
|--------------|-----------|
| `backend/app/api/**/*.py` | api-engineer |
| `backend/app/services/ai/**/*.py` | ai-backend-engineer |
| `backend/app/models/**/*.py` | database-engineer |
| `backend/tests/**/*.py` | testing-engineer |
| `frontend/**/*.tsx` | chat-frontend-engineer |
| `frontend/**/*.ts` | chat-frontend-engineer |

```markdown
## Fix Recommendations

### Priority 1: Add Missing Annotations

1. **FR-019** (Glass theme chat interface)
   - File: `frontend/app/(protected)/chat/components/ChatContainer.tsx`
   - Agent: `chat-frontend-engineer`
   - Action: Add `// Implements: FR-019` annotation

2. **FR-001** (Create tasks via natural language)
   - File: `backend/app/services/ai/tools/task_tools.py`
   - Agent: `ai-backend-engineer`
   - Action: Add `# Implements: FR-001` annotation
```

### 10. User Approval Prompt

```markdown
---

**Would you like me to invoke the fix agents to add these annotations?**

- Reply `yes` or `fix` to proceed with all fixes
- Reply `fix FR-001,FR-019` to fix specific requirements
- Reply `no` or `skip` to skip fixes

> Note: Fix agents will add FR-XXX annotation comments to existing code.
> They will NOT modify functionality, only add traceability markers.
```

### 11. Invoke Fix Agents (if approved)

For each approved fix, hand off to the appropriate agent:

**Handoff Context:**
```markdown
## Task: Add FR-XXX Annotation

**Requirement:** FR-019
**Description:** Glass theme chat interface
**File:** frontend/app/(protected)/chat/components/ChatContainer.tsx

**Action:** Add the following annotation comment to the file:

For TypeScript/TSX:
```typescript
/**
 * Implements: FR-019
 * @see specs/005-ai-todo-chatbot/spec.md
 */
```

For Python:
```python
"""
Implements: FR-019
See: specs/005-ai-todo-chatbot/spec.md
"""
```

**Important:**
- Add annotation at the top of the file or above the main component/function
- Do NOT modify any functionality
- Only add the traceability comment
```

### 12. Final Report

After fixes are applied:

```markdown
## Fix Results

| FR-ID | File | Status |
|-------|------|--------|
| FR-019 | ChatContainer.tsx | ✅ Annotation added |
| FR-001 | task_tools.py | ✅ Annotation added |

**Updated Coverage:** 100% (28/28)

Run `/sp.trace` again to verify all requirements are now traced.
```

## Agent Routing Reference

| Requirement Category | Primary Agent | Fallback |
|---------------------|---------------|----------|
| Core Chat Functionality | ai-backend-engineer | api-engineer |
| Voice & Language Support | chat-frontend-engineer | ai-backend-engineer |
| Agent Architecture | ai-backend-engineer | - |
| MCP Server & Tools | ai-backend-engineer | - |
| Conversation Persistence | database-engineer | api-engineer |
| Security & Access | api-engineer | - |
| Chat UI | chat-frontend-engineer | - |
| API & Infrastructure | api-engineer | - |

## Error Handling

### Spec Not Found
```
❌ Error: Spec file not found

Expected: specs/[feature]/spec.md
Actual: File does not exist

**Solution:** Run `/sp.specify` to create the specification.
```

### No Requirements in Spec
```
⚠️ Warning: No FR-XXX requirements found in spec

The spec file exists but contains no functional requirements.

**Solution:** Add requirements using the format:
- **FR-001**: [Description]
```

### Natural Language No Match
```
## Query Analysis

Your query: "[query]"

### No Matching Requirements Found

I searched the spec but couldn't find requirements matching your query.

**Suggestions:**
1. Check the spec file: `specs/[feature]/spec.md`
2. Try different keywords
3. Use `/sp.trace all` to see all requirements
4. Add the requirement with `/sp.specify` if it's missing
```

## Context

$ARGUMENTS

---

As the main request completes, you MUST create and complete a PHR (Prompt History Record).

1) Stage: `misc` (traceability analysis)
2) Generate Title: 3-7 words describing the trace action
3) Route: `history/prompts/<feature-name>/` or `history/prompts/general/`
4) Create PHR using `.specify/scripts/bash/create-phr.sh` or agent-native tools
5) Fill all placeholders including PROMPT_TEXT and RESPONSE_TEXT
