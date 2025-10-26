# Siphon Testing Setup & Workflow

## Initial Setup

### 1. Install Dependencies
```bash
pip install pytest pytest-watch click
```

### 2. Configure Pytest
Add this to your `pyproject.toml` (in your project root):

```toml
[tool.pytest.ini_options]
markers = [
    "parser: Parser strategy tests",
    "extractor: Extractor strategy tests",
    "enricher: Enricher strategy tests",
    "integration: Full pipeline integration tests",
    "slow: Tests that take >1 second",
]

addopts = [
    "-v",                    # Verbose output
    "--tb=short",           # Shorter tracebacks
    "--strict-markers",     # Fail on typo in marker names
    "-ra",                  # Show summary of all test outcomes
]

testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
```

### 3. Make Scaffold Script Executable
```bash
chmod +x scripts/scaffold_source.py
```

---

## Adding a New Source Type

### Quick Start
```bash
# 1. Scaffold the boilerplate
python scripts/scaffold_source.py Reddit

# 2. Add enum (manual step)
# Edit siphon-api/src/siphon_api/enums.py and add:
#   REDDIT = "reddit"

# 3. Start TDD loop
ptw siphon-server/tests/sources/reddit/ -- -m parser -x
```

### What Gets Created
```
siphon-server/src/siphon_server/sources/reddit/
├── __init__.py          # Imports all three classes
├── parser.py            # RedditParser with TODO stubs
├── extractor.py         # RedditExtractor with TODO stubs
└── enricher.py          # RedditEnricher with TODO stubs

siphon-server/tests/sources/reddit/
├── conftest.py          # Shared fixtures for Reddit tests
└── test_reddit.py       # Test classes for all three components
```

---

## TDD Workflow (Red → Green → Refactor)

### Phase 1: Parser
```bash
# Terminal 1: Edit code
vim siphon-server/src/siphon_server/sources/reddit/parser.py

# Terminal 2: Watch tests
ptw siphon-server/tests/sources/reddit/ -- -m parser -x
```

**Process:**
1. Write failing test in `test_reddit.py::TestRedditParser`
2. See it fail (RED)
3. Implement in `parser.py`
4. See it pass (GREEN)
5. Refactor if needed
6. Repeat until all parser tests pass

### Phase 2: Extractor
```bash
# Switch watch mode to extractor tests
ptw siphon-server/tests/sources/reddit/ -- -m extractor -x
```

Same process as parser.

### Phase 3: Enricher
```bash
# Switch watch mode to enricher tests
ptw siphon-server/tests/sources/reddit/ -- -m enricher -x
```

Same process as parser/extractor.

### Phase 4: Integration
```bash
# Run full pipeline test
pytest -m integration -v
```

---

## Common Commands

### During Development
```bash
# Watch specific component
ptw -- -m parser           # Parser only
ptw -- -m extractor        # Extractor only
ptw -- -m enricher         # Enricher only

# Watch multiple components
ptw -- -m "parser or extractor"

# Stop on first failure (faster feedback)
ptw -- -m parser -x
```

### Before Commit
```bash
# Run all tests
pytest -v

# Skip slow integration tests
pytest -m "not integration" -v

# Check specific source type
pytest siphon-server/tests/sources/youtube/ -v
```

### Debugging
```bash
# Show print statements
pytest -m parser -s

# Drop into debugger on failure
pytest -m parser --pdb

# Show why tests were skipped
pytest -v -rs
```

---

## Example: Adding YouTube Source (Step by Step)

```bash
# 1. Scaffold
python scripts/scaffold_source.py YouTube

# 2. Add to enums
echo 'YOUTUBE = "youtube"' >> siphon-api/src/siphon_api/enums.py

# 3. Implement parser (TDD)
ptw siphon-server/tests/sources/youtube/ -- -m parser -x

# In test_youtube.py::TestYouTubeParser:
def test_can_handle_valid_source(self, parser):
    assert parser.can_handle("https://youtube.com/watch?v=dQw4w9WgXcQ")

# Watch it fail (RED)
# Implement in parser.py
# Watch it pass (GREEN)

# 4. Implement extractor (TDD)
ptw siphon-server/tests/sources/youtube/ -- -m extractor -x

# Add tests, implement, repeat

# 5. Implement enricher (TDD)
ptw siphon-server/tests/sources/youtube/ -- -m enricher -x

# Add tests, implement, repeat

# 6. Integration test
pytest -m integration -v

# 7. Full suite check
pytest -v
```

---

## Tips

### Pytest-Watch Tips
- Use `-x` flag to stop on first failure (faster iteration)
- Use `--clear` to clear screen between runs
- Press Ctrl+C to stop watching

### Test Organization
- Put source-specific fixtures in `tests/sources/{source}/conftest.py`
- Put shared fixtures in `tests/conftest.py`
- Use marks to organize by component, not file structure

### Marks Best Practices
- Mark at class level: `@pytest.mark.parser` on `TestYouTubeParser`
- All methods inherit the mark automatically
- Use `pytest -m parser` to run all parser tests across all sources

### Skip vs XFail
- `@pytest.mark.skip`: Test is incomplete, don't run it
- `@pytest.mark.xfail`: Test is expected to fail (known bug)
- Scaffold generates tests with `pytest.skip()` for TODOs

---

## Troubleshooting

### "PytestUnknownMarkWarning"
- Add the mark to `[tool.pytest.ini_options]` in `pyproject.toml`
- Use `--strict-markers` to fail fast on typos

### Tests not found
- Check file names start with `test_`
- Check class names start with `Test`
- Check function names start with `test_`
- Run `pytest --collect-only` to see what pytest finds

### Pytest-watch not detecting changes
- Check you're in the right directory
- Try `ptw --clear` to force refresh
- Make sure files are `.py` extension
