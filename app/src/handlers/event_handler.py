import logging
from app.src.business_landscape_pycelonis.service import (
    EventEntity,
    Perspective,
    EntityMetadata,
    CategoryValuesRequestOptions,
)
from app.src.ocpm.constants import Namespace, Method, NamespaceType

from typing import List, Dict, Set


class EventHandler:
    """Class to handle specific related EventEntity handling methods"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def normalize_event_names(
        self, list_of_event_names: List[str], source_events: Dict[str, EventEntity]
    ) -> Set[str]:
        mapping_names = {k.lower(): k for k in source_events.keys()}
        return set([mapping_names.get(obj.lower(), obj) for obj in list_of_event_names])

    def normalize_event_name(
        self, event_name, source_events: Dict[str, EventEntity]
    ) -> str:
        mapping_names = {k.lower(): k for k in source_events.keys()}
        return mapping_names.get(event_name.lower(), event_name)

    def is_celonis_event_to_be_deployed(
        self,
        event_name: str,
        export_event: EventEntity,
        events_to_be_deployed: List[str],
        source_events: Dict[str, EventEntity],
    ) -> bool:
        return (
            export_event.namespace in Namespace.CELONIS
            and event_name in events_to_be_deployed
            and event_name in source_events
        )

    def is_custom_event_to_be_deployed(
        self,
        event_name: str,
        export_event: EventEntity,
        events_to_be_deployed: List[str],
    ) -> bool:
        return (
            export_event.namespace == NamespaceType.CUSTOM
            and event_name in events_to_be_deployed
        )

    def normalize_event_name_in_perspective(
        self, perspective: Perspective, source_events: Dict[str, EventEntity]
    ):
        for projection in perspective.projections:
            for event in projection.event_list:
                event.name = self.normalize_event_name(event.name, source_events)
            for event in projection.events:
                event.name = self.normalize_event_name(event.name, source_events)

    def fix_category_values_from_event(self, object_entity: EventEntity):
        for category in object_entity.categories:
            for i in range(len(category.values)):
                value = category.values[i]
                if value.namespace == NamespaceType.CELONIS:
                    category.values[i] = EntityMetadata(
                        name=value.name, namespace=value.namespace
                    )
                else:
                    category.values[i] = CategoryValuesRequestOptions(
                        display_name=value.name,
                        name=value.name,
                        namespace=value.namespace,
                    )
