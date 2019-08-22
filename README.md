# Lucene way search in django
#### ("Django" AND "DRF") OR ("Elasticserach-DSL" AND "Django Rest Elasticsearch")

_________________

## Installation

Only for Django with DRF:

```
pip install lusya
```

For Django with DRF and Elasticsearch-dsl with DRF:

```
pip install lucyfer
```

## Dependencies

|                           | lucyfer | lusya |
|---------------------------|---------|-------|
| lucyparser                | +       | +     |
| Django                    | +       | +     |
| djangorestframework       | +       | +     |
| django-rest-elasticsearch | +       | -     |
| elasticsearch-dsl         | +       | -     |


## Usage Examples

Include search backend class in `DEFAULT_FILTER_BACKENDS` in `settings.py` instead of default search backend:

```python
# todo
```

Create `serachsets.py` in application and fill it:
```python
# todo
```

Include searchset class in your `ModelViewSet`:
```python
# todo
```

Now you can use lucene-way syntax for your view:
```python
# todo
```
