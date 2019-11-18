# Lucene way search in django
#### ("Django" AND "DRF") OR ("Elasticserach-DSL" AND "Django Rest Elasticsearch")

_________________

## Installation

Only for Django with DRF:

```
pip install lucyfer
```

For Django with DRF and Elasticsearch-dsl with DRF:

```
pip install lucyfer[full]
```

## Dependencies

|                           | lucyfer | lucyfer[full] |
|---------------------------|---------|-------|
| lucyparser                | +       | +     |
| Django                    | +       | +     |
| djangorestframework       | +       | +     |
| django-rest-elasticsearch | -       | +     |
| elasticsearch-dsl         | -       | +     |


## Usage Example  
________________
Create your search backend class:

```python
from lucyfer.backend import LuceneSearchFilter, DjangoLuceneSearchFilterMixin, ElasticLuceneSearchFilterMixin


class SearchBackend(DjangoLuceneSearchFilterMixin, ElasticLuceneSearchFilterMixin, LuceneSearchFilter):
    pass
``` 

Copy reference to `SearchBackend` class and include it in `DEFAULT_FILTER_BACKENDS` in `settings.py` instead of default search backend:

```python
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ('path.to.SearchBackend',)
}
```

Create `searchsets.py` file in your django-application and fill it:
```python
from lucyfer.searchset import DjangoSearchSet
from lucyfer.searchset.fields.django import DjangoCharField
from lucyfer.searchset.searchhelper import DjangoSearchHelperMixin

from .models import MyModel


class MyModelSearchSet(DjangoSearchHelperMixin, DjangoSearchSet):
    some_field = DjangoCharField(sources=["another_field__name"], exclude_sources_from_mapping=True)

    class Meta:
        model = MyModel

    fields_to_exclude_from_mapping = ['field_to_exclude_from_mapping', ]

```

Include searchset class in your `ModelViewSet`:
```python
from rest_framework.viewsets import ModelViewSet

from .searchsets import MyModelSearchSet


class MyModelViewSet(ModelViewSet):
    search_class = MyModelSearchSet
```

You have to save `search_fields` in your `ModelViewSet` if you want to save custom search possibility.

Now you can use lucene-way syntax for your view.


Tests execution:
```
pytest tests/test_* -c tests/pytest.ini 
```
