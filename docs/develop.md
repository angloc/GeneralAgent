# Publish

```bash
# Publish pip package
poetry build -f sdist
poetry publish
```

# Test

```shell
# Create new python environment
python -m venv ga
source ga/bin/activate

# Temporarily disable python alias (if any)
unalias python

# Install dependencies
pip install .

# Export environment variables
export $(grep -v '^#' .env | sed 's/^export //g' | xargs)

# Run tests
cd test
pytest -s -v
```
