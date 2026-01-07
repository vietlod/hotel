# bug

**Specialized in:** Identifying root causes, fixing bugs, and preventing regressions

**This command will be available in chat with /bug**

---

## Usage
```
/bug <error description>
```

## Example
```
/bug Export to CSV failing with "UnicodeEncodeError" for Vietnamese characters
```

---

## 5-Phase Bug Fixing Process

### Phase 1: Reproduction & Documentation (15 min)
**Goal:** Confirm bug exists and document exact conditions

**Steps:**
1. Identify affected feature (data ingestion, export, filtering, etc.)
2. Create reproducible test case
3. Document error message, stack trace, browser console logs
4. Note: data inputs, browser/OS, auth status
5. Check if bug in latest code or old deployment

**Deliverable:**
- Exact steps to reproduce
- Error logs (backend/frontend)
- Expected vs actual behavior

---

### Phase 2: Root Cause Analysis (20 min)
**Goal:** Understand WHY the bug happens

**Investigation:**
1. Read error message carefully
2. Check git diff recent changes
3. Review related code paths
4. Check database state
5. Test with different inputs

**Examples:**
- **Authentication bug:** Issue in JWT validation? Token expired?
- **Export bug:** File encoding? Missing column? Large dataset timeout?
- **API bug:** Null reference? Type mismatch? Missing dependency?

**Deliverable:**
- Root cause identified
- Code section causing issue
- Why it worked before (if regression)

---

### Phase 3: Fix Implementation (20 min)
**Goal:** Write minimal fix addressing root cause ONLY

**Rules:**
1. Single, focused fix (don't refactor unless necessary)
2. Follow rules.mdc standards
3. Add error handling if missing
4. Update type hints
5. Add logging for debugging

**Example - Export Unicode Bug:**
```python
# WRONG: Refactor while fixing
def export_csv(indicators):
    # Rewrite entire export logic...
    
# RIGHT: Minimal fix
def export_csv(indicators):
    csv_content = generate_csv(indicators)
    # FIX: Add UTF-8 BOM for Vietnamese chars
    return b'\xef\xbb\xbf' + csv_content.encode('utf-8')
```

**Deliverable:**
- Minimal code changes
- Comments explaining fix
- No unrelated refactoring

---

### Phase 4: Testing (20 min)
**Goal:** Verify fix works and doesn't break anything

**Test Checklist:**
1. **Reproduce Original Bug:** Confirm it's fixed
2. **Edge Cases:** Test with boundary conditions
3. **Regression Tests:** Run existing test suite (>90%)
4. **Related Features:** Test similar functionality

**Testing Examples:**
```python
# Test Vietnamese export
def test_export_csv_vietnamese():
    indicators = [IndicatorResponse(..., name="Tăng trưởng")]
    csv = export_csv(indicators)
    assert "Tăng trưởng" in csv.decode('utf-8')

# Test large file export
def test_export_large_dataset():
    large_dataset = [Indicator(...) for _ in range(10000)]
    csv = export_csv(large_dataset)
    assert len(csv) > 0

# Test old test suite
pytest --cov=services --cov-fail-under=90
```

**Deliverable:**
- All tests passing (>90%)
- Bug reproduction test added
- No regression in related features

---

### Phase 5: Documentation & Deployment (10 min)
**Goal:** Document fix and deploy to production

**Documentation:**
1. Update CHANGELOG.md with:
   - Error: What users experienced
   - Root cause: Why it happened
   - Solution: How it's fixed
   - Files changed: What was modified
2. Add inline code comments
3. Update README if needed

**Example CHANGELOG Entry:**
```markdown
### Fixed
- **CSV Export Unicode Error**: Fixed Vietnamese characters displaying as corrupted text
  - Issue: Export to CSV buttons causing "UnicodeEncodeError" and file corruption
  - Root cause: Missing UTF-8 BOM (Byte Order Mark) in CSV output
  - Solution: Added UTF-8 BOM header to export_csv function
  - Files: [export.py](backend/services/export.py#L45-52)
  - Git commit: `abc123d`
  - Testing: Added test_export_csv_vietnamese in test suite
```

**Deployment:**
```bash
git add -A
git commit -m "fix(export): add UTF-8 BOM for Vietnamese characters"
git push origin dev
# PR review → merge → auto-deploy to production
```

**Deliverable:**
- CHANGELOG.md updated
- Code comments added
- PR description clear
- Ready for production

---

## Quick Bug Fixing Checklist

### Before Fixing
- [ ] Bug can be reproduced with clear steps
- [ ] Root cause identified and documented
- [ ] Impact scope understood (affecting how many users?)

### While Fixing
- [ ] Only change what's necessary (no refactoring)
- [ ] Follow type safety (Rule 2)
- [ ] Add error handling (Rule 4)
- [ ] Add logging for monitoring (Rule 10)

### Before Deployment
- [ ] Bug is fixed (reproducible bug test passes)
- [ ] No regressions (>90% test suite passing)
- [ ] CHANGELOG.md updated with details
- [ ] Code comments explain the fix
- [ ] Conventional commit message: `fix(scope): description`

---

## Common Bug Patterns in ECODATA

| Bug Type | Example | Fix Location |
|----------|---------|--------------|
| **API Errors** | 500 response on indicator fetch | `routers/indicators.py` - Check query logic, error handling |
| **Database Issues** | Foreign key constraint violated | `models/*.py` - Check relationship definitions, cascades |
| **Encoding Errors** | Vietnamese text corrupted in export | `services/export.py` - Add UTF-8 BOM, set encoding explicitly |
| **Type Errors** | `TypeError: 'NoneType' object is not subscriptable` | Check type hints, add None checks |
| **Authentication** | 403 Forbidden on admin endpoint | `dependencies.py` - Check role requirements, token validation |
| **External API** | "Connection timeout from World Bank API" | `services/crawlers.py` - Add retry logic, increase timeout |

---

*Last Updated: December 31, 2025*
*Project: ECODATA v2.7.2*
*Status: Production Ready*
