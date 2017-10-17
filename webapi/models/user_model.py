import typing

from apistar import typesystem
from apistar.typesystem import Object


class AttributeName(typesystem.String):
    description = "Name of User attribute to modify."


class AttributeValue(typesystem.String):
    description = "Modified attribute value."


class CreatedOn(typesystem.Number):
    description = "Creation timestamp."


class DefaultDomain(typesystem.String):
    description = "Default domain for this user."


class DomainNamespace(typesystem.String):
    description = "User domain namespace. Example: 'public.example.com'"


class Domains(typesystem.Array):
    description = "A set of unique domains this User occupies."


class Email(typesystem.String):
    description = "Email address."


class EncryptedPassword(typesystem.String):
    max_length = 8
    description = "Encrypted password."


class LastModifiedOn(typesystem.Number):
    description = "Timestamp of last modification."


class Name(typesystem.String):
    description = "User's Full Name."


class UnencryptedPassword(typesystem.String):
    description = "Plain text password."


class UserId(typesystem.String):
    min_length = 1
    description = "User's ID."


class UserIdList(typing.List[typesystem.String]):
    description = "List of DomainNamespace stringified IDs."


class Version(typesystem.Number):
    description = "Current version of this User"


class User(Object):
    properties = {
        'user_id': UserId,
        'name': Name,
        'email': Email,
        'password': EncryptedPassword,
        'default_domain': DefaultDomain,
        'domains': Domains,
        'version': Version,
        '_created_on': CreatedOn,
        '_last_modified_on': LastModifiedOn
    }


class CreateUser(Object):
    properties = {
        'name': Name,
        'email': Email,
        'password': UnencryptedPassword,
        'default_domain': DefaultDomain
    }


class ModifyUser(Object):
    properties = {
        'attribute_name': AttributeName,
        'attribute_value': AttributeValue
    }


class ChangeUserPassword(Object):
    properties = {
        'new_password': UnencryptedPassword
    }
