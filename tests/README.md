# Automated Tests

Tests use only synthetic records from `shared/examples/`. They verify valid examples, rejected lifecycle mismatches, license arithmetic, and closed-issue requirements.

Run with:

```text
python -m unittest discover -s tests -v
```
