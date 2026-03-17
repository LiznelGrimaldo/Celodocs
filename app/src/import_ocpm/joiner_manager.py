from typing import List, Any, Callable, Optional
from app.src.business_landscape_pycelonis.service import (
    EntityField,
    FactoryParameter,
    EntityRelationship,
    SqlFactoryTransformationTransport,
    EntityMetadata,
    CategoryValueReference,
    SqlFactoryDataset,
    SqlFactoryRelationshipTransformation,
)
from app.src.ocpm.constants import Method, Namespace
from app.src.import_ocpm.custom_sql_factory_script_joiner import (
    CustomSQLFactoryScriptJoiner,
)
from collections import defaultdict


class JoinerManager:
    """
    Class to handle the joining of list to import into an OCPM environment

    merge_overwrite: Combines objects, giving priority to the export list but including import list that dont conflict.
        overwrite: Uses only the export transformations.
        default: The inverse of merge_overwrite, giving priority to import list objects.
    """

    def join_lists(
        self,
        list1: List[Any],
        list2: List[Any],
        key_func: Callable[[Any], Any],
        conflict_method: str = None,
        filter_func: Callable[[Any], bool] = lambda x: True,
    ) -> List[Any]:
        list1_keys = {key_func(entity) for entity in list1}
        list2_keys = {key_func(entity) for entity in list2}

        if conflict_method == Method.MERGE_OVERWRITE:
            union_entities = [
                entity
                for entity in list1
                if key_func(entity) not in list2_keys and filter_func(entity)
            ] + list2
        elif conflict_method == Method.OVERWRITE:
            union_entities = list2
        else:
            union_entities = [
                entity
                for entity in list2
                if key_func(entity) not in list1_keys and filter_func(entity)
            ] + list1

        return union_entities

    def join_import_and_export_lists(
        self,
        import_list: List[Any],
        export_list: List[Any],
        filter_namespace: bool = False,
        conflict_method: str = None,
    ) -> List[Any]:
        key_func = lambda x: x.name
        filter_func = (
            (lambda x: x.namespace in Namespace.CUSTOM)
            if filter_namespace
            else lambda x: True
        )
        return self.join_lists(
            import_list, export_list, key_func, conflict_method, filter_func
        )

    def join_tags(
        self,
        import_list: List[str],
        export_list: List[str],
        conflict_method: str = None,
    ) -> List[str]:
        """Joins import and export tag lists based on the conflict method."""
        return self.join_lists(
            import_list,
            export_list,
            key_func=lambda x: x,
            conflict_method=conflict_method,
        )

    def join_entity_fields(
        self,
        import_list: List[EntityField],
        export_list: List[EntityField],
        conflict_method: str = None,
    ) -> List[EntityField]:
        """Joins import and export EntityField Lists based on the conflict method."""
        return self.join_lists(
            import_list,
            export_list,
            key_func=lambda x: x.name.lower(),
            conflict_method=conflict_method,
        )

    def join_category_values(
        self,
        import_list: List[EntityMetadata],
        export_list: List[EntityMetadata],
        conflict_method: str = None,
    ) -> List[EntityMetadata]:
        """Joins import and export EntityField Lists based on the conflict method."""
        return self.join_lists(
            import_list,
            export_list,
            key_func=lambda x: x.name.lower(),
            conflict_method=conflict_method,
        )

    def join_parameters(
        self,
        import_list: List[FactoryParameter],
        export_list: List[FactoryParameter],
        conflict_method: str = None,
    ) -> List[FactoryParameter]:
        """Joins import and export FactoryParameter Lists based on the conflict method."""
        return self.join_lists(
            import_list,
            export_list,
            key_func=lambda x: x.name,
            conflict_method=conflict_method,
        )

    def join_event_relationships(
        self,
        import_relationships: List[EntityRelationship],
        export_relationships: List[EntityRelationship],
        conflict_method: str = None,
    ) -> List[EntityRelationship]:
        """Joins import and export events EntityRelationship Lists based on the conflict method."""
        return self.join_relationships(
            import_relationships, export_relationships, "", conflict_method
        )

    def create_default_import_transformation(
        self, export_transformation: SqlFactoryTransformationTransport
    ) -> SqlFactoryTransformationTransport:
        """Create a default import transformation based on the export transformation."""
        return SqlFactoryTransformationTransport(
            change_sql_factory_datasets=[],
            property_sql_factory_datasets=[],
            relationship_transformations=[],
            namespace=export_transformation.namespace,
            property_names=export_transformation.property_names,
            foreign_key_names=export_transformation.foreign_key_names,
        )

    def filter_transformations(
        self, transformations: List[Any], ids_to_exclude: set
    ) -> List[Any]:
        """Filter out transformations based on a set of IDs to exclude."""
        return [
            entity
            for entity in transformations
            if entity.id.lower() not in ids_to_exclude
        ]

    def filter_relationship_transformations(
        self, transformations: List[Any], ids_to_exclude: set
    ) -> List[Any]:
        """Filter out transformations based on a set of IDs to exclude."""
        for relationship_entity in transformations:
            relationship_entity.sql_factory_datasets = self.filter_transformations(
                relationship_entity.sql_factory_datasets, ids_to_exclude
            )
        return transformations

    def collect_transformation_ids(
        self, transformation: SqlFactoryTransformationTransport
    ) -> set:
        """Collects all IDs from the provided transformation."""
        ids = {
            entity.id.lower()
            for entity in transformation.change_sql_factory_datasets or []
        }
        ids.update(
            {
                entity.id.lower()
                for entity in transformation.property_sql_factory_datasets or []
            }
        )
        ids.update(
            {
                dataset.id.lower()
                for entity in transformation.relationship_transformations or []
                for dataset in entity.sql_factory_datasets or []
            }
        )
        return ids

    def join_transformations(
        self,
        import_transformation: Optional[SqlFactoryTransformationTransport],
        export_transformation: SqlFactoryTransformationTransport,
        conflict_method: str = None,
    ) -> SqlFactoryTransformationTransport:
        """Joins import and export SQL transformations based on the conflict method."""

        if not import_transformation:
            import_transformation = self.create_default_import_transformation(
                export_transformation
            )

        if conflict_method == Method.MERGE_OVERWRITE:
            return self._merge_transformations(
                import_transformation, export_transformation
            )
        elif conflict_method == Method.OVERWRITE:
            return export_transformation
        else:  # Default behavior
            return self._default_merge_transformations(
                import_transformation, export_transformation
            )

    def _merge_transformations(
        self,
        import_transformation: SqlFactoryTransformationTransport,
        export_transformation: SqlFactoryTransformationTransport,
    ) -> SqlFactoryTransformationTransport:
        """Handles merging transformations with priority to the export."""

        export_ids = self.collect_transformation_ids(export_transformation)

        export_transformation.change_sql_factory_datasets = self.filter_transformations(
            import_transformation.change_sql_factory_datasets or [], export_ids
        ) + (export_transformation.change_sql_factory_datasets or [])

        # custom Joiner
        if self.check_possibility_to_merge_scripts(
            export_transformation, import_transformation
        ):
            export_transformation.property_sql_factory_datasets = (
                self.merge_property_scripts(
                    export_transformation, import_transformation
                )
            )
        else:
            export_transformation.property_sql_factory_datasets = (
                self.filter_transformations(
                    import_transformation.property_sql_factory_datasets or [],
                    export_ids,
                )
                + (export_transformation.property_sql_factory_datasets or [])
            )

        export_transformation.relationship_transformations = (
            self.filter_relationship_transformations(
                import_transformation.relationship_transformations or [], export_ids
            )
            + (export_transformation.relationship_transformations or [])
        )

        return export_transformation

    # def _get_relationship_transformation_by_name(self, relationship_transformation: SqlFactoryRelationshipTransformation, foreign_key_name: str):
    #     return {relationship_transformation.relationship_name:}

    def check_possibility_to_merge_scripts(
        self,
        export_transformation: SqlFactoryTransformationTransport,
        import_transformation: SqlFactoryTransformationTransport,
    ):
        custom_joiner = CustomSQLFactoryScriptJoiner(
            export_transformation, import_transformation
        )
        custom_attributes_in_import = bool(
            set(custom_joiner.extract_property_names(import_transformation)).difference(
                custom_joiner.extract_property_names(export_transformation)
            )
        )
        no_foreign_keys_in_import = not import_transformation.foreign_key_names
        return custom_attributes_in_import and no_foreign_keys_in_import

    def merge_property_scripts(
        self,
        export_transformation: SqlFactoryTransformationTransport,
        import_transformation: SqlFactoryTransformationTransport,
    ) -> List[Optional[SqlFactoryDataset]]:
        custom_joiner = CustomSQLFactoryScriptJoiner(
            export_transformation, import_transformation
        )
        merged_script = custom_joiner.generate_script(
            cte_name_target="CTE_NewAttributes",
            cte_name_source="CTE_OriginalAttributes",
        )
        # return the merged property_sql_factory_datasets
        import_transformation.property_sql_factory_datasets[0].sql = merged_script
        return [import_transformation.property_sql_factory_datasets[0]]

    def _default_merge_transformations(
        self,
        import_transformation: SqlFactoryTransformationTransport,
        export_transformation: SqlFactoryTransformationTransport,
    ) -> SqlFactoryTransformationTransport:
        """Handles merging transformations with priority to the import."""

        import_ids = self.collect_transformation_ids(import_transformation)

        import_transformation.change_sql_factory_datasets = self.filter_transformations(
            export_transformation.change_sql_factory_datasets or [], import_ids
        ) + (import_transformation.change_sql_factory_datasets or [])

        import_transformation.property_sql_factory_datasets = (
            self.filter_transformations(
                export_transformation.property_sql_factory_datasets or [], import_ids
            )
            + (import_transformation.property_sql_factory_datasets or [])
        )

        import_transformation.relationship_transformations = (
            self.filter_relationship_transformations(
                export_transformation.relationship_transformations or [], import_ids
            )
            + (import_transformation.relationship_transformations or [])
        )

        return import_transformation

    def metadata_key(self, metadata):
        return (metadata.name, metadata.namespace)

    def join_categories(
        self,
        import_categories: List[CategoryValueReference],
        export_categories: List[CategoryValueReference],
        conflict_method: str,
    ):
        # Creating dictionaries to store categories based on metadata keys
        export_dict = defaultdict(list)
        import_dict = defaultdict(list)

        for category in export_categories:
            key = self.metadata_key(category.metadata)
            export_dict[key].extend(category.values)

        for category in import_categories:
            key = self.metadata_key(category.metadata)
            import_dict[key].extend(category.values)

        result_dict = {}

        for key in set(export_dict.keys()).union(import_dict.keys()):
            export_values = export_dict.get(key, [])
            import_values = import_dict.get(key, [])

            # Assuming you have a conflict_method that handles conflicts
            result = JoinerManager().join_category_values(
                import_list=import_values,
                export_list=export_values,
                conflict_method=conflict_method,
            )

            result_dict[key] = result

        # Convert back to CategoryValueReference objects
        merged_categories = [
            CategoryValueReference(
                metadata={"name": key[0], "namespace": key[1]}, values=values
            )
            for key, values in result_dict.items()
        ]
        return merged_categories
