from formencode import Schema, All, Invalid, validators

from nomenklatura.model.common import Name, FancyValidator


class AvailableDatasetSlug(FancyValidator):

    def _to_python(self, value, state):
        from nomenklatura.model.dataset import Dataset
        if Dataset.by_slug(value) is None:
            return value
        raise Invalid('Dataset already exists.', value, None)


class DatasetNewSchema(Schema):
    slug = All(AvailableDatasetSlug(), Name(not_empty=True))
    label = validators.String(min=3, max=255)


class DatasetEditSchema(Schema):
    allow_extra_fields = True
    label = validators.String(min=3, max=255)
    match_aliases = validators.StringBool(if_missing=False)
    ignore_case = validators.StringBool(if_missing=False)
    public_edit = validators.StringBool(if_missing=False)
    normalize_text = validators.StringBool(if_missing=False)
    enable_invalid = validators.StringBool(if_missing=False)
