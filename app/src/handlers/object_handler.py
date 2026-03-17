from app.src.business_landscape_pycelonis.service import (
    ObjectEntity,
    EntityRelationship,
    Perspective,
    CategoryValueReference,
    EntityMetadata,
    CategoryValuesRequestOptions,
)
import logging
from app.src.ocpm.constants import Namespace, Method, NamespaceType
from app.src.import_ocpm.joiner_manager import JoinerManager
from app.src.handlers.entity_handler import EntityHandler
from app.src.ocpm import NamespaceType

from typing import List, Dict, Set


class ObjectHandler:
    """Class to handle specific related ObjectEntity handling methods"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def normalize_object_names(
        self, list_of_object_names: List[str], source_objects: Dict[str, ObjectEntity]
    ) -> Set[str]:
        mapping_names = {k.lower(): k for k in source_objects.keys()}
        return set(
            [mapping_names.get(obj.lower(), obj) for obj in list_of_object_names]
        )

    def normalize_object_name(
        self, object_name, source_objects: Dict[str, ObjectEntity]
    ) -> str:
        mapping_names = {k.lower(): k for k in source_objects.keys()}
        return mapping_names.get(object_name.lower(), object_name)

    def is_celonis_object_to_be_deployed(
        self,
        object_name: str,
        export_object: ObjectEntity,
        objects_to_be_deployed: List[str],
    ) -> bool:
        return (
            export_object.namespace in Namespace.CELONIS
            and object_name in objects_to_be_deployed
        )

    def is_custom_object_to_be_deployed(
        self,
        object_name: str,
        export_object: ObjectEntity,
        objects_to_be_deployed: List[str],
    ) -> bool:
        return (
            export_object.namespace == NamespaceType.CUSTOM
            and object_name in objects_to_be_deployed
        )

    def fix_category_values_from_object(self, object_entity: ObjectEntity):
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

    def fix_category_values(self, categories: List[CategoryValueReference]):
        for category in categories:
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

    def merge_custom_relationships(
        self,
        original_object: ObjectEntity,
        export_object: ObjectEntity,
        object_name: str,
        conflict_method: str,
        objects_to_be_deployed: List[str],
        source_objects: Dict[str, ObjectEntity],
    ) -> List[EntityRelationship]:
        union_relationships = self.join_relationships(
            import_relationships=[
                r
                for r in original_object.relationships
                if r.namespace == NamespaceType.CUSTOM
            ],
            export_relationships=[
                r
                for r in export_object.relationships
                if r.namespace == NamespaceType.CUSTOM
            ],
            conflict_method=conflict_method,
            source_objects=source_objects,
            objects_to_be_deployed=objects_to_be_deployed,
            object_name=object_name,
        )
        union_relationships.extend(
            [
                r
                for r in original_object.relationships
                if r.namespace in Namespace.CELONIS
            ]
        )
        return union_relationships

    def merge_default_relationships(
        self,
        original_object: ObjectEntity,
        export_object: ObjectEntity,
        object_name: str,
        conflict_method: str,
        source_objects: Dict[str, ObjectEntity],
    ) -> List[EntityRelationship]:
        union_relationships = JoinerManager().join_import_and_export_lists(
            import_list=original_object.relationships,
            export_list=export_object.relationships,
            filter_namespace=True,
            conflict_method=conflict_method,
        )
        return [
            relationship
            for relationship in union_relationships
            if (
                relationship.target.object_ref.name in source_objects
                and relationship.namespace == NamespaceType.CUSTOM
            )
            or (relationship.namespace in Namespace.CELONIS)
        ]

    def get_dependant_objects(
        self,
        relationships: List[EntityRelationship],
        export_objects: Dict[str, ObjectEntity],
        object_name: str,
        source_objects: Dict[str, ObjectEntity],
        objects_to_be_deployed: List[str],
    ) -> List[str]:
        return [
            relationship.target.object_ref.name
            for relationship in relationships
            if relationship.target.object_ref.name not in objects_to_be_deployed
            and relationship.target.object_ref.name in source_objects
            and relationship.cardinality == "HAS_MANY"
            and {
                r.target.object_ref.name: r
                for r in export_objects.get(
                    relationship.target.object_ref.name,
                    ObjectEntity(relationships=[]),
                ).relationships
                if r.cardinality == "HAS_MANY" and r.namespace == NamespaceType.CUSTOM
            }.get(object_name)
        ]

    def filter_valid_relationships(
        self,
        original_object: ObjectEntity,
        export_object: ObjectEntity,
        object_name: str,
        source_objects: Dict[str, ObjectEntity],
    ) -> List[EntityRelationship]:
        relationship_list = [
            r
            for r in original_object.relationships
            if r.target.object_ref.name in source_objects
        ]
        for relationship in relationship_list:
            if relationship.cardinality == "HAS_MANY" and relationship.target.mapped_by:
                target_relationships = source_objects.get(
                    relationship.target.object_ref.name,
                    ObjectEntity(relationships=[]),
                ).relationships
                for r in target_relationships:
                    if r.target.object_ref.name == object_name and r.target.mapped_by:
                        relationship.target.mapped_by = None
                        relationship.target.mapped_by_namespace = None
        return relationship_list

    def normalize_relationship_names(
        self,
        export_relationships: List[EntityRelationship],
        source_objects: Dict[str, ObjectEntity],
    ):
        for relationship in export_relationships:
            relationship.target.object_ref.name = self.normalize_object_name(
                object_name=relationship.target.object_ref.name,
                source_objects=source_objects,
            )

    def get_first_level_relationships(
        self,
        conflict_method: str,
        export_object: ObjectEntity,
        original_object: ObjectEntity,
        source_objects: Dict[str, ObjectEntity],
    ) -> List[EntityRelationship]:
        self.normalize_relationship_names(export_object.relationships, source_objects)

        if conflict_method == Method.MERGE_OVERWRITE:
            relationships_list = [
                relationship
                for relationship in export_object.relationships
                if not relationship.target.mapped_by
                and relationship.target.object_ref.name in source_objects
            ]
            relationships_list.extend(
                [
                    relationship
                    for relationship in original_object.relationships
                    if relationship.name not in [r.name for r in relationships_list]
                ]
            )
        elif conflict_method == Method.OVERWRITE:
            relationships_list = [
                relationship
                for relationship in export_object.relationships
                if not relationship.target.mapped_by
                and relationship.target.object_ref.name in source_objects
            ]
        else:
            relationships_list = [
                relationship
                for relationship in export_object.relationships
                if not relationship.target.mapped_by
                and relationship.target.object_ref.name in source_objects
                and relationship.name
                not in [r.name for r in original_object.relationships]
            ] + original_object.relationships
        return relationships_list

    def get_second_level_relationships(
        self,
        object_name: str,
        original_object: ObjectEntity,
        relationships_list: List[EntityRelationship],
        export_relationships,
        conflict_method: str,
        source_objects: Dict[str, ObjectEntity],
    ) -> List[EntityRelationship]:
        self.normalize_relationship_names(export_relationships, source_objects)

        if conflict_method == Method.MERGE_OVERWRITE:
            relationships_list = self.merge_second_level_relationships(
                export_relationships, original_object, object_name, source_objects
            )

        elif conflict_method == Method.OVERWRITE:
            relationships_list = [
                relationship
                for relationship in export_relationships
                if relationship.target.object_ref.name in source_objects
                and not relationship.target.mapped_by
            ]
            relationships_list.extend(
                [
                    relationship
                    for relationship in export_relationships
                    if relationship.target.object_ref.name in source_objects
                    and relationship.target.mapped_by
                    and object_name
                    in [
                        r.target.object_ref.name
                        for r in source_objects.get(
                            relationship.target.object_ref.name,
                            ObjectEntity(relationships=[]),
                        ).relationships
                    ]
                ]
            )
        else:
            relationships_list = [
                relationship
                for relationship in export_relationships
                if relationship.target.object_ref.name in source_objects
                and relationship.name
                not in [r.name for r in original_object.relationships]
            ] + original_object.relationships
        relationships_list = [
            relationship
            for relationship in relationships_list
            if relationship.target.object_ref.name in source_objects
        ]
        self.update_mapped_by_attributes(
            object_name, relationships_list, source_objects
        )
        return relationships_list

    def merge_second_level_relationships(
        self,
        export_relationships: List[EntityRelationship],
        original_object: ObjectEntity,
        object_name: str,
        source_objects: Dict[str, ObjectEntity],
    ) -> List[EntityRelationship]:
        relationships_list = [
            relationship
            for relationship in export_relationships
            if relationship.target.object_ref.name in source_objects
            and not relationship.target.mapped_by
        ]
        relationships_list.extend(
            [
                relationship
                for relationship in export_relationships
                if relationship.target.object_ref.name in source_objects
                and relationship.target.mapped_by
                and object_name
                in [
                    r.target.object_ref.name
                    for r in source_objects.get(
                        relationship.target.object_ref.name,
                        ObjectEntity(relationships=[]),
                    ).relationships
                ]
            ]
        )
        relationships_list.extend(
            [
                relationship
                for relationship in original_object.relationships
                if relationship.name not in [r.name for r in relationships_list]
            ]
        )
        return relationships_list

    def update_mapped_by_attributes(
        self,
        object_name: str,
        relationships_list: List[EntityRelationship],
        source_objects: Dict[str, ObjectEntity],
    ) -> None:
        for relationship in relationships_list:
            if relationship.cardinality == "HAS_MANY" and relationship.target.mapped_by:
                target_relationships = source_objects.get(
                    relationship.target.object_ref.name,
                    ObjectEntity(relationships=[]),
                ).relationships
                for r in target_relationships:
                    if r.target.object_ref.name == object_name and r.target.mapped_by:
                        relationship.target.mapped_by = None
                        relationship.target.mapped_by_namespace = None

    def filter_relationships(
        self,
        relationships: List[EntityRelationship],
        source_relationships: List[EntityRelationship],
        object_name: str,
        objects_to_be_deployed: List[str],
        source_objects: Dict[str, ObjectEntity],
    ) -> List[EntityRelationship]:
        return [
            relationship
            for relationship in relationships
            if (
                relationship.namespace in Namespace.CUSTOM
                and relationship.name not in [r.name for r in source_relationships]
                and (
                    relationship.target.object_ref.name in source_objects
                    or relationship.target.object_ref.name in objects_to_be_deployed
                )
            )
            or (
                relationship.namespace in Namespace.CELONIS
                and not relationship.target.mapped_by
            )
            or (
                relationship.target.mapped_by
                and object_name
                in [
                    r.target.object_ref.name
                    for r in source_objects.get(
                        relationship.target.object_ref.name,
                        ObjectEntity(relationships=[]),
                    ).relationships
                ]
                and relationship.name not in [r.name for r in source_relationships]
            )
        ]

    def join_relationships(
        self,
        import_relationships: List[EntityRelationship],
        export_relationships: List[EntityRelationship],
        object_name: str,
        objects_to_be_deployed: List[str],
        source_objects: Dict[str, ObjectEntity],
        conflict_method: str = None,
    ) -> List[EntityRelationship]:
        """Joins import and export objects EntityRelationship Lists based on the conflict method."""
        if conflict_method == Method.OVERWRITE:
            return self.filter_relationships(
                export_relationships,
                [],
                object_name,
                objects_to_be_deployed,
                source_objects,
            )

        elif conflict_method == Method.MERGE_OVERWRITE:
            union_relationships = self.filter_relationships(
                export_relationships,
                [],
                object_name,
                objects_to_be_deployed,
                source_objects,
            )
            union_relationships.extend(
                [
                    relationship
                    for relationship in import_relationships
                    if relationship.name not in [r.name for r in union_relationships]
                    and relationship.namespace in Namespace.CUSTOM
                ]
            )
            return union_relationships

        else:
            return (
                self.filter_relationships(
                    export_relationships,
                    import_relationships,
                    object_name,
                    objects_to_be_deployed,
                    source_objects,
                )
                + import_relationships
            )

    def normalize_object_name_in_perspective(
        self, perspective: Perspective, source_objects: Dict[str, ObjectEntity]
    ):
        for object in perspective.objects:
            object.name = self.normalize_object_name(object.name, source_objects)
            object.origin_ref.name = self.normalize_object_name(
                object.origin_ref.name, source_objects
            )
            for relationship in object.relationships:
                relationship.name = self.normalize_object_name(
                    relationship.name, source_objects
                )

        for projection in perspective.projections:
            projection.lead_object.name = self.normalize_object_name(
                projection.lead_object.name, source_objects
            )
