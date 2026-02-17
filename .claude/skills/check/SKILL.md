---
name: check
description: Force just check before commit, block if failures
---

# Pre-Commit Check

Ensure code quality with `just check` before allowing commit.

## Usage

### `/check [--force]`

Run full check suite and report results. Failures must be fixed before commit.

## Workflow

1. **Run just check**
   ```
   just check
   ```

2. **Parse results**
   - Syntax errors → stop immediately, show error
   - Lint errors → show file:line, suggest fix
   - Type errors → show file:line, explain
   - Test failures → show test name, output

3. **Report**
   ```
   ✓ Syntax: OK
   ✓ Lint: OK
   ✓ Typecheck: OK
   ✗ Test: 2 failures
     - tests/test_auth.py::test_login
     - tests/test_proxy.py::test_timeout
   ```

4. **Block commit if failures**
   ```
   Fix failures before commit. Run: just test tests/test_auth.py -v
   ```

## Options

### `/check --force`
Skip check and allow commit anyway (use with caution).

## Fast Feedback Order

The check runs in this order for fast failure:
1. Syntax (fastest)
2. Static analysis
3. Unit tests
4. Integration tests

## Integration with /commit

When using `/commit`, it automatically runs `/check` first:
```
/commit "add feature"
→ Running checks first...
→ ✓ All checks passed
→ Committing: feat: add feature ✨
```

## Errors

- Checks fail → "Checks failed. Fix before commit. See output above."
- just missing → "Error: just not installed"
