---
name: tdd-check
description: TDD cycle helper - run test, check result, update increment file
---

# TDD Cycle Helper

Guide through red-green-refactor with explicit test tracking.

## Usage

### `/tdd-check [test-path]`

Run test and guide next step based on result.

## TDD Cycle

### 1. Red (write failing test)
```
/tdd-check tests/test_feature.py
→ Running: pytest tests/test_feature.py -v
→ ✗ FAILED (expected - we're in red phase)
→ Next: Write minimal code to make it pass
```

### 2. Green (make it pass)
```
/tdd-check tests/test_feature.py
→ Running: pytest tests/test_feature.py -v
→ ✓ PASSED
→ Next: Refactor while keeping tests green
→ Mark test done in increment file? [Y/n]
```

### 3. Refactor
```
/tdd-check tests/test_feature.py
→ Running: pytest tests/test_feature.py -v
→ ✓ PASSED (still green after refactor)
→ Good to go. Next test?
```

## Increment File Integration

When test passes, offer to check off in increment file:
```
Found increment file: docs/backlog/in-progress/00043-feature.md
Mark "- [ ] test feature" as done? [Y/n]
→ Updating file...
→ - [x] test feature
```

## Commands

### `/tdd-check [path]`
Run specific test file.

### `/tdd-check --red`
Expect failure (red phase). Warns if test passes unexpectedly.

### `/tdd-check --green`
Expect pass (green phase). Error if fails.

### `/tdd-check --watch`
Run in watch mode: re-run on file changes.

## Test List from Increment

Parse Implementation Plan section for test items:
```markdown
## Implementation Plan
- [ ] test auth middleware rejects invalid tokens
- [ ] test auth middleware accepts valid tokens
- [ ] test auth middleware sets user context
```

Suggest next test:
```
Next unimplemented test: "test auth middleware rejects invalid tokens"
Run? [Y/n/specific test]
```

## Errors

- No test path provided, no increment file found → "Error: Provide test path or be in an in-progress increment"
- --green but test fails → "Error: Test should pass in green phase. Fix implementation."
- --red but test passes → "Warning: Test already passes. Did you already implement it?"
