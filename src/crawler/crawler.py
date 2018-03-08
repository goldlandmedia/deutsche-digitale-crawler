import logging
from jsonschema import ValidationError

from exceptions import MappingException
from crawler.feed import DeutscheDigitaleBibliothekFeed, LocalJsonFeed
from schema import ResourceSchema, ResourceAPI
from crawler.mapping import DDBSChulCloudTargetToSourceMapper, TargetToSourceMapper


class Crawler:
    provider_name = None
    target_to_source_mapper = None
    source_api = None

    def __init__(self, target_to_source_mapper: TargetToSourceMapper, target_api=ResourceAPI) -> None:
        self.logger = logging.getLogger(self.provider_name)
        self.source_api = self.source_api()
        self.target_to_source_mapper = target_to_source_mapper
        self.target_api = target_api()

    def log(self, message):
        self.logger.error(message)

    def crawl(self):
        feed = self.source_api.get_feed()
        for child in feed:
            resource_dict = self.parse(child)
            resource = self.validate(resource_dict)
            if resource:
                self.target_api.add_resource(resource)

    def parse(self, element: dict) -> dict:
        return self.target_to_source_mapper.map(element)

    def validate(self, resource_dict):
        target_format = ResourceSchema(self.provider_name, **resource_dict)
        try:
            self.target_api.validate(target_format)
        except ValidationError as e:
            self.log(e)
            return None
        return target_format


class DeutscheDigitaleBibliothekCrawler(Crawler):
    provider_name = "Deutsche Digitale Bibliothek"
    source_api = DeutscheDigitaleBibliothekFeed

    def __init__(self):
        super().__init__(DDBSChulCloudTargetToSourceMapper())
