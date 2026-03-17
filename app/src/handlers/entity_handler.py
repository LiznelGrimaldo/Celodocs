# join_relationships
from app.src.business_landscape_pycelonis.service import EntityRelationship
from app.src.ocpm.constants import Namespace, Method, NamespaceType
from typing import List
import logging


class EntityHandler:
    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def compare_ccdm_attributes(
        self,
        entity_name: str,
        export_attributes: List,
        import_attributes: List,
        list_type: str,
    ):
        import_celonis_atts = list(
            filter(lambda att: att.namespace in Namespace.CELONIS, import_attributes)
        )
        export_celonis_atts = list(
            filter(lambda att: att.namespace in Namespace.CELONIS, export_attributes)
        )
        matches = [
            value for value in import_celonis_atts if value in export_celonis_atts
        ]
        different_ccdm_versions = len(matches) != len(import_celonis_atts)
        if different_ccdm_versions:
            self.logger.warning(
                f"different CCDM Versions: source catalog {list_type} on Entity {entity_name} are different to target Object"
            )
        return different_ccdm_versions
