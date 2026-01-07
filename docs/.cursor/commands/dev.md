# dev

**Specialized in:** Planning, implementing, testing, and deploying new features

**This command will be available in chat with /dev**

---

## Usage
```
/dev <feature description>
```

## Example
```
/dev Add parquet export format support alongside CSV and JSON
```

---

## 5-Phase Feature Development Process

### Phase 1: Requirements & Planning (20 min)
**Goal:** Define what needs to be built and how

**Questions to Answer:**
1. What is the user problem being solved?
2. Which components are affected? (frontend, backend, database)
3. What data needs to be accessed or modified?
4. Are there any database schema changes?
5. What are the acceptance criteria?

**Design Plan:**
- Backend: API routes, database changes, services
- Frontend: New components, state changes, UI
- Testing: Unit tests, integration tests, E2E tests
- Documentation: README, CHANGELOG, code comments

**Example - Parquet Export Feature:**
```
User Problem: Users want to export data in Parquet format for data science workflows
Components Affected:
  - Backend: Export service, new endpoint
  - Frontend: Export dialog, format selector
  - Database: No schema changes
  
Technical Design:
  - Backend: Add parquet generation to ExportService
  - Frontend: Add "Parquet" option to export format selector
  - API: Reuse existing /api/export endpoint (format param)
  
Database: No migrations needed
Testing: Add test_export_parquet() test case
```

**Deliverable:**
- Feature plan document
- List of files to modify
- Acceptance criteria
- Estimated effort (hours)

---

### Phase 2: Backend Implementation (30 min)
**Goal:** Implement backend logic and API routes

**Steps for Parquet Export:**

1. **Add to Service Layer**
```python
# services/export.py
def to_parquet(self, indicators: List[IndicatorResponse]) -> bytes:
    """Convert indicators to Parquet format."""
    import pyarrow as pa
    import pyarrow.parquet as pq
    from io import BytesIO
    
    # Convert to table format
    rows = []
    for ind in indicators:
        for val in ind.values:
            rows.append({
                'indicator_id': ind.id,
                'indicator_name': ind.name,
                'source': ind.source,
                'year': val['year'],
                'value': val['value']
            })
    
    # Create PyArrow table
    table = pa.Table.from_pylist(rows)
    
    # Write to bytes
    output = BytesIO()
    pq.write_table(table, output)
    return output.getvalue()
```

2. **Update Export Endpoint**
```python
# routers/export.py
@router.post("/api/export")
async def export_indicators(
    payload: ExportPayload,
    db: AsyncSession = Depends(get_db)
):
    """Export indicators in multiple formats."""
    valid_formats = ['csv', 'json', 'parquet']
    
    if payload.format not in valid_formats:
        raise HTTPException(400, f"Invalid format: {payload.format}")
    
    indicators = await get_indicators_by_ids(db, payload.indicator_ids)
    
    if payload.format == 'csv':
        content = ExportService().to_csv(indicators)
        media_type = 'text/csv'
    elif payload.format == 'json':
        content = ExportService().to_json(indicators)
        media_type = 'application/json'
    elif payload.format == 'parquet':
        content = ExportService().to_parquet(indicators)
        media_type = 'application/octet-stream'
    
    return Response(
        content=content,
        media_type=media_type,
        headers={'Content-Disposition': f'attachment; filename=export.{payload.format}'}
    )
```

3. **Dependencies**
```
# requirements.txt
pyarrow>=12.0.0  # For parquet support
```

**Deliverable:**
- New service method implemented
- API endpoint updated
- Tests passing
- Type hints present
- Error handling added

---

### Phase 3: Frontend Implementation (30 min)
**Goal:** Build UI components and integrate with backend

**Steps for Parquet Export:**

1. **Update Export Dialog**
```typescript
// components/ExportDialog.tsx
interface ExportOption {
  id: string;
  label: string;
  description: string;
  format: 'csv' | 'json' | 'parquet';
}

const EXPORT_OPTIONS: ExportOption[] = [
  {
    id: 'csv',
    label: 'CSV',
    description: 'Comma-separated values (best for Excel)',
    format: 'csv'
  },
  {
    id: 'json',
    label: 'JSON',
    description: 'JSON format (for APIs)',
    format: 'json'
  },
  {
    id: 'parquet',
    label: 'Parquet',
    description: 'Apache Parquet (for data science)',
    format: 'parquet'
  }
];

export const ExportDialog: React.FC = () => {
  const [selectedFormat, setSelectedFormat] = useState<string>('csv');
  
  const handleExport = async () => {
    const response = await fetch('/api/export', {
      method: 'POST',
      body: JSON.stringify({
        indicator_ids: selectedIndicators,
        format: selectedFormat
      })
    });
    
    const blob = await response.blob();
    downloadFile(blob, `export.${selectedFormat}`);
  };
  
  return (
    <dialog className="export-dialog">
      <h2>Export Data</h2>
      <div className="format-options">
        {EXPORT_OPTIONS.map(option => (
          <label key={option.id}>
            <input
              type="radio"
              value={option.id}
              checked={selectedFormat === option.id}
              onChange={(e) => setSelectedFormat(e.target.value)}
            />
            <div>
              <strong>{option.label}</strong>
              <p>{option.description}</p>
            </div>
          </label>
        ))}
      </div>
      <button onClick={handleExport}>Download</button>
    </dialog>
  );
};
```

2. **Update State Management**
```typescript
// App.tsx
const [exportFormat, setExportFormat] = useState<'csv' | 'json' | 'parquet'>('csv');
```

3. **Add Type Definitions**
```typescript
// types.ts
type ExportFormat = 'csv' | 'json' | 'parquet';

interface ExportPayload {
  indicator_ids: string[];
  format: ExportFormat;
}
```

**Deliverable:**
- New UI components created
- Backend API integrated
- Type safety throughout
- No console errors
- Responsive design

---

### Phase 4: Testing (20 min)
**Goal:** Verify feature works correctly

**Unit Tests:**
```python
# tests/unit/test_export_parquet.py
def test_to_parquet_generates_valid_file():
    """Parquet export should generate valid file."""
    service = ExportService()
    indicators = [IndicatorResponse(...)]
    
    result = service.to_parquet(indicators)
    
    assert isinstance(result, bytes)
    assert result.startswith(b'PAR1')  # Parquet magic number

def test_to_parquet_includes_all_data():
    """Parquet should include all indicator values."""
    indicators = [
        IndicatorResponse(
            id='WB_001',
            values=[{'year': 2023, 'value': 100.5}]
        )
    ]
    
    result = service.to_parquet(indicators)
    # Parse and verify content...
```

**Integration Tests:**
```python
# tests/integration/test_api_export_parquet.py
@pytest.mark.asyncio
async def test_export_endpoint_parquet(client: AsyncClient):
    """Export endpoint returns Parquet file."""
    payload = {
        'indicator_ids': ['WB_001'],
        'format': 'parquet'
    }
    
    response = await client.post('/api/export', json=payload)
    
    assert response.status_code == 200
    assert response.headers['content-type'] == 'application/octet-stream'
    assert response.content.startswith(b'PAR1')
```

**Frontend Tests:**
```typescript
// frontend/__tests__/components/ExportDialog.test.tsx
it('should show parquet option', () => {
  render(<ExportDialog />);
  
  const parquetOption = screen.getByLabelText('Parquet');
  expect(parquetOption).toBeInTheDocument();
});

it('should export as parquet when selected', async () => {
  const { user } = render(<ExportDialog />);
  
  const parquetRadio = screen.getByRole('radio', { name: /parquet/i });
  await user.click(parquetRadio);
  
  const downloadBtn = screen.getByRole('button', { name: /download/i });
  await user.click(downloadBtn);
  
  // Verify fetch was called with format: 'parquet'
  expect(global.fetch).toHaveBeenCalledWith(
    expect.anything(),
    expect.objectContaining({
      body: expect.stringContaining('parquet')
    })
  );
});
```

**E2E Tests:**
```bash
# tests/e2e/export_parquet.spec.ts
test('should export to parquet', async ({ page }) => {
  // Navigate to app
  await page.goto('/app');
  
  // Select indicators
  await page.click('[data-test="indicator-checkbox"]');
  
  // Open export dialog
  await page.click('[data-test="export-button"]');
  
  // Select parquet format
  await page.click('[value="parquet"]');
  
  // Download
  const downloadPromise = page.waitForEvent('download');
  await page.click('button:has-text("Download")');
  const download = await downloadPromise;
  
  // Verify file
  expect(download.suggestedFilename()).toContain('.parquet');
});
```

**Run All Tests:**
```bash
# Backend
pytest --cov=services --cov-fail-under=90

# Frontend
npm run test -- --coverage

# E2E
npm run test:e2e
```

**Deliverable:**
- All tests passing (>90%)
- Bug reproduction tests included
- No console errors
- Performance acceptable

---

### Phase 5: Documentation & Deployment (10 min)
**Goal:** Document feature and deploy to production

**Update CHANGELOG.md:**
```markdown
## [2.7.3] - 2025-12-31
### Added
- **Parquet Export Support**: Export indicators in Apache Parquet format
  - New format option in export dialog
  - Optimized for data science workflows (Python Pandas, R)
  - Maintains full data integrity and column typing
  - Files: [export.py](backend/services/export.py#L50-70), [ExportDialog.tsx](components/ExportDialog.tsx)
  - Git commit: `abc123d`

### Changed
- Enhanced export endpoint to support parquet format
  - Updated [export.py](backend/routers/export.py) to handle new format
  - All export formats now use unified endpoint
```

**Update README.md:**
```markdown
### Export Formats

ECODATA supports three export formats:

| Format | Best For | Features |
|--------|----------|----------|
| **CSV** | Excel, spreadsheets | Human-readable, wide format |
| **JSON** | APIs, web apps | Structured, nested data |
| **Parquet** | Data science | Efficient, typed columns, compression |

Example export with Python:
\`\`\`python
import pandas as pd

# Read parquet export
df = pd.read_parquet('export.parquet')
print(df.head())
\`\`\`
```

**Code Comments:**
```python
def to_parquet(self, indicators: List[IndicatorResponse]) -> bytes:
    """
    Convert indicators to Apache Parquet format.
    
    Parquet is a columnar storage format optimized for:
    - Efficient data compression (reduces file size 80%)
    - Fast analytics queries
    - Language-agnostic (works with Python, R, Java, etc.)
    - Native support in Pandas, Polars, DuckDB
    
    Args:
        indicators: List of indicators with values
        
    Returns:
        Bytes representing parquet file content
        
    Note:
        Requires pyarrow>=12.0.0
    """
```

**Deployment:**
```bash
git add -A
git commit -m "feat(export): add parquet format support"
git push origin dev

# Wait for GitHub Actions checks ✅
# Get code review approval ✅
# Deploy to production via /dep
```

**Deliverable:**
- CHANGELOG.md updated
- README.md updated with examples
- Code comments explain feature
- Conventional commit message
- Ready for production

---

## Quick Feature Development Checklist

### Planning Phase
- [ ] Feature requirements documented
- [ ] Affected components identified
- [ ] Database changes planned (if any)
- [ ] Acceptance criteria defined

### Backend Phase
- [ ] New service methods implemented
- [ ] API endpoints working
- [ ] Database migrations run (if needed)
- [ ] Error handling added
- [ ] Type hints present

### Frontend Phase
- [ ] New components created
- [ ] Backend API integrated
- [ ] Type safety verified
- [ ] Responsive design tested
- [ ] No console errors

### Testing Phase
- [ ] Unit tests passing
- [ ] Integration tests passing
- [ ] E2E tests passing
- [ ] Overall coverage >90%
- [ ] Edge cases covered

### Documentation Phase
- [ ] CHANGELOG.md updated
- [ ] README.md updated
- [ ] Code comments added
- [ ] Conventional commit ready

### Deployment
- [ ] All checks passing
- [ ] Code review approved
- [ ] Pre-flight checks passed
- [ ] VPS deployment successful
- [ ] Health checks verify

---

## Common Feature Patterns in ECODATA

| Feature Type | Example | Files to Modify |
|--------------|---------|-----------------|
| **New Export Format** | Add Excel export | `services/export.py`, `routers/export.py`, `ExportDialog.tsx` |
| **New Data Source** | Add OECD data | `models/indicator.py`, `routers/indicators.py`, `FilterPanel.tsx` |
| **New Filter Option** | Filter by data quality | `schemas/filter.py`, `FilterPanel.tsx`, API queries |
| **New Admin Feature** | Batch operations | `routers/admin.py`, `AdminPage.tsx`, tests |
| **UI Improvement** | Dark mode theme | Tailwind config, CSS vars, all components |

---

*Last Updated: December 31, 2025*
*Project: ECODATA v2.7.2*
*Status: Production Ready*
