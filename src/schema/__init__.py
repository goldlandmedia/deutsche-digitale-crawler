import json
import logging

import os

import jsonschema
import requests
from requests import HTTPError

import settings
from exceptions import ConfigurationError


class ResourceAPI:
    schema = 'resource-schema.json'

    def __init__(self, base_url=settings.TARGET_URL) -> None:
        self.logger = logging.getLogger('resourceAPI')
        self.base_url = base_url
        schema_path = os.path.join(os.path.dirname(__file__), self.schema)
        self.resource_schema = json.load(open(schema_path))

    def validate(self, instance):
        jsonschema.validate(instance, self.resource_schema)

    @property
    def auth(self):
        if settings.BASIC_AUTH_USER and settings.BASIC_AUTH_PASSWORD:
            return settings.BASIC_AUTH_USER, settings.BASIC_AUTH_PASSWORD,
        else:
            raise ConfigurationError("settings.BASIC_AUTH_USER and settings.BASIC_AUTH_PASSWORD must be set.")

    def log(self, message):
        self.logger.error(message)

    def add_resource(self, resource: dict):
        try:
            # self.log("adding resource {} {} ".format(self.base_url, resource))
            request = requests.post(self.base_url, json=resource, auth=self.auth)
            request.raise_for_status()
        except HTTPError as e:
            self.log("{} {} ".format(e, e.response.content))
        except ConnectionError as e:
            self.log(e)
            raise e


class ResourceSchema(dict):
    mime_type = 'text/html'
    content_category = 'atomic'

    def __init__(self, provider_name, **kwargs) -> None:
        super().__init__(**kwargs)
        self.__setitem__('mimeType', self.mime_type)
        self.__setitem__('contentCategory', self.content_category)
        self.__setitem__('providerName', provider_name)
        # TODO: Empty licence is accepted by the resource api
        if kwargs.get('licenses', None) is None:
            self.__setitem__('licenses', [''])
