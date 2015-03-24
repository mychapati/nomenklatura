import colander
from normality import slugify
from colander import Invalid # noqa


class Ref(object):

    def deserialize(self, node, cstruct):
        if cstruct is colander.null:
            return colander.null
        value = self.decode(cstruct)
        if value is None:
            raise colander.Invalid(node, 'Missing')
        return value

    def cstruct_children(self, node, cstruct):
        return []


class UserRef(Ref):

    def decode(self, cstruct):
        from nomenklatura.model.user import User

        if hasattr(cstruct, 'api_key'):
            return cstruct
        if isinstance(cstruct, (basestring, int)):
            return User.by_id(cstruct)
        if isinstance(cstruct, dict):
            return self.decode(cstruct.get('id'))
        return None


def dataset_slug_available(value):
    from nomenklatura.model.dataset import Dataset
    existing = Dataset.by_slug(value)
    return existing is None


class DatasetCreateForm(colander.MappingSchema):
    slug = colander.SchemaNode(colander.String(),
        preparer=slugify,
        validator=colander.All(
            colander.Function(dataset_slug_available, 'Invalid slug'),
            colander.Length(min=3, max=100))) # noqa
    label = colander.SchemaNode(colander.String(),
        validator=colander.Length(min=3, max=500)) # noqa


class DatasetEditForm(colander.MappingSchema):
    label = colander.SchemaNode(colander.String(),
        validator=colander.Length(min=3, max=500)) # noqa
    public = colander.SchemaNode(colander.Boolean())
    normalize_text = colander.SchemaNode(colander.Boolean())
    ignore_case = colander.SchemaNode(colander.Boolean())
    enable_invalid = colander.SchemaNode(colander.Boolean())
    match_aliases = colander.SchemaNode(colander.Boolean())


class UserEditForm(colander.MappingSchema):
    display_name = colander.SchemaNode(colander.String(),
        validator=colander.Length(min=3, max=500)) # noqa
    email = colander.SchemaNode(colander.String(),
        validator=colander.Email()) # noqa


class RoleForm(colander.MappingSchema):
    role = colander.SchemaNode(colander.String(),
        validator=colander.OneOf(['none', 'read', 'edit', 'manage'])) # noqa
    user = colander.SchemaNode(UserRef())


class ContextEditForm(colander.MappingSchema):
    source_url = colander.SchemaNode(colander.String(),
                                     validator=colander.url,
                                     missing=None,
                                     default=None)
    publisher = colander.SchemaNode(colander.String(),
                                    missing=None, default=None)
    publisher_url = colander.SchemaNode(colander.String(),
                                        validator=colander.url,
                                        missing=None,
                                        default=None)
    active = colander.SchemaNode(colander.Boolean(),
                                 default=True, missing=True)
    resource_name = colander.SchemaNode(colander.String(),
                                        missing=None, default=None)
    resource_mapping = colander.SchemaNode(colander.Mapping(unknown='preserve'),
                                           missing=None, default=None)
