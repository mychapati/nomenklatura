import colander
from colander import Invalid # noqa

from nomenklatura.model.constants import ROLES, STATES


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


def email_available(value):
    from nomenklatura.model.user import User
    return User.by_email(value) is None


class UserCreateForm(colander.MappingSchema):
    display_name = colander.SchemaNode(colander.String(),
        validator=colander.Length(min=3, max=500)) # noqa
    email = colander.SchemaNode(colander.String(),
        validator=colander.All(colander.Email(),
            colander.Function(email_available, 'E-Mail already registered'))) # noqa
    password = colander.SchemaNode(colander.String(),
        validator=colander.Length(min=3, max=500)) # noqa


class UserEditForm(colander.MappingSchema):
    display_name = colander.SchemaNode(colander.String(),
        validator=colander.Length(min=3, max=500)) # noqa
    email = colander.SchemaNode(colander.String(),
        validator=colander.Email()) # noqa
    password = colander.SchemaNode(colander.String(),
        validator=colander.Length(min=3, max=500), # noqa
        missing=None, default=None) # noqa
    system_role = colander.SchemaNode(colander.String(),
        validator=colander.OneOf(ROLES)) # noqa


class RoleForm(colander.MappingSchema):
    role = colander.SchemaNode(colander.String(),
        validator=colander.OneOf(ROLES)) # noqa
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
    enrich_root = colander.SchemaNode(colander.String(),
                                      missing=None, default=None)
    enrich_status = colander.SchemaNode(colander.String(),
                                        validator=colander.OneOf(STATES),
                                        missing=None, default=None) # noqa


class PairingForm(colander.MappingSchema):
    decision = colander.SchemaNode(colander.Boolean(),
                                   default=None, missing=None)
    left_id = colander.SchemaNode(colander.String())
    right_id = colander.SchemaNode(colander.String())
