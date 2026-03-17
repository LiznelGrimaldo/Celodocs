from app.src.business_landscape_pycelonis.service import (
    SqlFactoryTransformationTransport,
    FactoryListTransport,
    SqlFactoryTransport,
    ObjectEntity,
    EventEntity,
    FactoryDataSourceTransport,
    SqlFactoryDataset,
    SqlFactoryRelationshipTransformation,
    UserFactoryTemplateListTransport,
    UserFactoryTemplateTransport,
)
import logging
from app.src.ocpm.constants import Namespace, NamespaceType
from app.src.import_ocpm.joiner_manager import JoinerManager
from typing import List, Optional, Dict, Union, DefaultDict
import json


class FactoryHandler:
    """Class to handle specific related FactoryListTransport handling methods"""

    OCPM_SCHEMA_ID = "00000000-0000-0000-0000-000000000000"

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def get_custom_transformations(
        self, transformations: List[SqlFactoryTransformationTransport]
    ) -> Optional[SqlFactoryTransformationTransport]:
        for transformation in transformations:
            if transformation.namespace == NamespaceType.CUSTOM:
                return transformation

    def get_duplicate_checker_transformations(
        self, transformations: List[SqlFactoryTransformationTransport]
    ) -> Optional[SqlFactoryTransformationTransport]:
        for transformation in transformations:
            if transformation.namespace == NamespaceType.DUPLICATE_CHECKER:
                return transformation

    def get_celonis_transformations(
        self, transformations: List[SqlFactoryTransformationTransport]
    ) -> Optional[SqlFactoryTransformationTransport]:
        for transformation in transformations:
            if transformation.namespace == NamespaceType.CELONIS:
                return transformation

    def should_update_celonis_factory(
        self,
        export_factory: FactoryListTransport,
        entity_name: str,
        export_data_connection_id: str,
        export_factory_kind: str,
        objects_to_be_deployed: List[str],
        events_to_be_deployed: List[str],
        source_objects: Dict[str, ObjectEntity],
        source_events: Dict[str, EventEntity],
    ) -> bool:
        return export_factory.namespace in Namespace.CELONIS and (
            (
                entity_name in objects_to_be_deployed
                and export_factory_kind == "OBJECT"
                and entity_name in source_objects
                and export_factory.data_connection_id == export_data_connection_id
            )
            or (
                export_factory_kind == "EVENT"
                and entity_name in source_events
                and entity_name in events_to_be_deployed
            )
        )

    def get_export_factory_kind(
        self,
        export_factory: Union[FactoryListTransport, UserFactoryTemplateListTransport],
    ) -> str:
        try:
            return export_factory.target.kind.name
        except Exception:
            return export_factory.target.kind

    def is_valid_import_celonis_factory(
        self, import_factory: FactoryListTransport, import_data_connection_id: str
    ) -> bool:
        """Check if the import factory has a valid data connection ID."""
        return (
            import_factory.data_connection_id == import_data_connection_id
            or import_factory.data_connection_id == self.OCPM_SCHEMA_ID
        )

    def get_matching_sql_factories(
        self,
        export_sql_statements: Dict[str, List[SqlFactoryTransport]],
        source_sql_statements: Dict[str, List[SqlFactoryTransport]],
        entity_name: str,
        import_factory: FactoryListTransport,
        export_factory: FactoryListTransport,
    ) -> tuple:
        """Get the matching import and export SQL factories for the given entity."""
        import_sql_factory = next(
            (
                sql_factory
                for sql_factory in source_sql_statements.get(entity_name, [])
                if sql_factory.factory_id == import_factory.factory_id.split("_")[0]
                and sql_factory.data_connection_id == import_factory.data_connection_id
            ),
            None,
        )

        export_sql_factory = next(
            (
                sql_factory
                for sql_factory in export_sql_statements.get(entity_name, [])
                if sql_factory.factory_id == export_factory.factory_id.split("_")[0]
                and sql_factory.data_connection_id == export_factory.data_connection_id
            ),
            None,
        )

        return import_sql_factory, export_sql_factory

    def _get_transformation_by_id(
        self, id_name, sql_factory_datasets: List[SqlFactoryDataset]
    ) -> Optional[SqlFactoryDataset]:
        return {dataset.id: dataset for dataset in sql_factory_datasets}.get(id_name)

    def _get_transformation_by_relationship_name(
        self,
        relationship_name,
        sql_factory_datasets: List[SqlFactoryRelationshipTransformation],
    ) -> Optional[SqlFactoryRelationshipTransformation]:
        return {
            dataset.relationship_name: dataset for dataset in sql_factory_datasets
        }.get(relationship_name)

    def apply_overwrite_transformations(
        self,
        export_factory_kind: str,
        import_celonis_transformation: SqlFactoryTransformationTransport,
        export_celonis_transformation: SqlFactoryTransformationTransport,
    ):
        """Apply overwrite transformations based on the export and import transformations."""
        if export_factory_kind == "OBJECT":
            for idx, import_change_sql_factory_dataset in enumerate(
                import_celonis_transformation.change_sql_factory_datasets
            ):
                export_change_sql_factory_dataset = self._get_transformation_by_id(
                    id_name=import_change_sql_factory_dataset.id,
                    sql_factory_datasets=export_celonis_transformation.change_sql_factory_datasets,
                )
                if not import_change_sql_factory_dataset.overwrite and export_change_sql_factory_dataset:
                    import_celonis_transformation.change_sql_factory_datasets[
                        idx
                    ].overwrite = export_change_sql_factory_dataset.overwrite
                    import_celonis_transformation.change_sql_factory_datasets[
                        idx
                    ].complete_overwrite = (
                        export_change_sql_factory_dataset.complete_overwrite
                    )
                    import_celonis_transformation.change_sql_factory_datasets[
                        idx
                    ].materialise_cte = (
                        export_change_sql_factory_dataset.materialise_cte
                    )

        for idx, import_property_sql_factory_dataset in enumerate(
            import_celonis_transformation.property_sql_factory_datasets
        ):
            export_property_sql_factory_dataset = self._get_transformation_by_id(
                id_name=import_property_sql_factory_dataset.id,
                sql_factory_datasets=export_celonis_transformation.property_sql_factory_datasets,
            )
            if not import_property_sql_factory_dataset.overwrite and export_property_sql_factory_dataset:
                import_celonis_transformation.property_sql_factory_datasets[
                    idx
                ].overwrite = export_property_sql_factory_dataset.overwrite
                import_celonis_transformation.property_sql_factory_datasets[
                    idx
                ].complete_overwrite = (
                    export_property_sql_factory_dataset.complete_overwrite
                )
                import_celonis_transformation.property_sql_factory_datasets[
                    idx
                ].materialise_cte = export_property_sql_factory_dataset.materialise_cte

        for relationship_script in (
            import_celonis_transformation.relationship_transformations or []
        ):
            export_relationship_script = self._get_transformation_by_relationship_name(
                relationship_name=relationship_script.relationship_name,
                sql_factory_datasets=export_celonis_transformation.relationship_transformations,
            )
            for idx, import_sql_factory_dataset in enumerate(
                relationship_script.sql_factory_datasets
            ):
                if not import_sql_factory_dataset.overwrite and export_relationship_script:
                    export_sql_factory_dataset = self._get_transformation_by_id(
                        id_name=import_sql_factory_dataset.id,
                        sql_factory_datasets=export_relationship_script.sql_factory_datasets,
                    )
                    if export_sql_factory_dataset:
                        relationship_script.sql_factory_datasets[
                            idx
                        ].overwrite = export_sql_factory_dataset.overwrite
                        relationship_script.sql_factory_datasets[
                            idx
                        ].complete_overwrite = export_sql_factory_dataset.complete_overwrite
                        relationship_script.sql_factory_datasets[
                            idx
                        ].materialise_cte = export_sql_factory_dataset.materialise_cte

    def get_kind_of_entity(self, factory: FactoryListTransport) -> str:
        try:
            return factory.target.kind.name
        except Exception:
            return factory.target.kind

    def is_custom_factory(
        self,
        export_factory: FactoryListTransport,
        entity_name: str,
        export_data_connection_id: str,
        objects_to_be_deployed: List[str],
        events_to_be_deployed: List[str],
        source_objects: Dict[str, ObjectEntity],
        source_events: Dict[str, EventEntity],
    ):
        kind_of_entity = self.get_kind_of_entity(export_factory)
        return export_factory.namespace in (
            NamespaceType.CUSTOM,
            NamespaceType.DUPLICATE_CHECKER,
        ) and (
            (
                entity_name in objects_to_be_deployed
                and kind_of_entity == "OBJECT"
                and entity_name in source_objects
                and (
                    export_factory.data_connection_id == export_data_connection_id
                    or export_factory.data_connection_id == self.OCPM_SCHEMA_ID
                )
            )
            or (
                kind_of_entity == "EVENT"
                and entity_name in source_events
                and entity_name in events_to_be_deployed
                and (
                    export_factory.data_connection_id == export_data_connection_id
                    or export_factory.data_connection_id == self.OCPM_SCHEMA_ID
                )
            )
        )

    def get_custom_export_factories(
        self,
        export_factories: List[FactoryListTransport],
        entity_name: str,
        export_data_connection_id: str,
        objects_to_be_deployed: List[str],
        events_to_be_deployed: List[str],
        source_objects: Dict[str, ObjectEntity],
        source_events: Dict[str, EventEntity],
    ) -> List:
        """Filter custom export factories based on data connection ID."""
        return [
            ef
            for ef in export_factories
            if self.is_custom_factory(
                ef,
                entity_name,
                export_data_connection_id,
                objects_to_be_deployed,
                events_to_be_deployed,
                source_objects,
                source_events,
            )
        ]

    def get_template_factories_by_entity_name(
        self,
        entity_name: str,
        template_factories: DefaultDict[str, UserFactoryTemplateListTransport],
    ) -> List[UserFactoryTemplateListTransport]:
        return template_factories.get(entity_name, [])

    def get_template_factories_by_entity_name_and_name(
        self,
        entity_name: str,
        factory_name: str,
        template_factories: DefaultDict[str, UserFactoryTemplateListTransport],
    ) -> List[UserFactoryTemplateListTransport]:
        factories = template_factories.get(entity_name, [])
        for factory in factories:
            if factory.name == factory_name:
                return factory

    def get_template_by_entity_name_and_name(
        self,
        entity_name: str,
        template_name: str,
        templates: DefaultDict[str, UserFactoryTemplateTransport],
    ) -> UserFactoryTemplateListTransport:
        templates = templates.get(entity_name, [])
        for template in templates:
            if template.name == template_name:
                return template

    def get_list_of_factory_templates(
        self, entity_names: List[str], template_factories
    ):
        list_of_factory_templates = []
        for entity_name in entity_names:
            list_of_factory_templates.extend(
                self.get_template_factory_by_entity_name(
                    entity_name, template_factories
                )
            )
        return list_of_factory_templates

    def is_valid_import_factory(
        self,
        import_factory: FactoryListTransport,
        import_data_connection_id: str,
        kind_of_entity: str,
    ) -> bool:
        """Check if an import factory is valid based on the data connection ID and entity type."""
        return import_factory.data_connection_id == import_data_connection_id or (
            import_factory.data_connection_id == self.OCPM_SCHEMA_ID
        )

    def get_import_sql_factory(
        self,
        entity_name: str,
        import_factory: FactoryListTransport,
        source_sql_statements: Dict[str, List[SqlFactoryTransport]],
    ) -> Optional[FactoryListTransport]:
        """Retrieve import SQL factory matching the entity name and import factory details."""
        return next(
            (
                sql_factory
                for sql_factory in source_sql_statements.get(entity_name, [])
                if sql_factory.factory_id == import_factory.factory_id.split("_")[0]
                and sql_factory.data_connection_id == import_factory.data_connection_id
            ),
            None,
        )

    def get_export_sql_factories(
        self,
        export_sql_statements: Dict[str, List[SqlFactoryTransport]],
        entity_name: str,
        export_factories_ids: List[str],
    ) -> List[SqlFactoryTransport]:
        """Retrieve export SQL factories for the given entity name."""
        return [
            sql_factory
            for sql_factory in export_sql_statements.get(entity_name, [])
            if sql_factory.factory_id in export_factories_ids
        ]

    def join_custom_export_transformations(
        self, export_sql_factories: List[SqlFactoryTransport]
    ) -> SqlFactoryTransformationTransport:
        """Join export SQL factory transformations when multiple SQL Factories"""
        transformations = []
        export_custom_transformation = self.get_custom_transformations(
            export_sql_factories[0].transformations
        )
        export_celonis_transformation = self.get_celonis_transformations(
            export_sql_factories[0].transformations
        )
        for sql_factory in export_sql_factories[1:]:
            
            if export_custom_transformation and self.get_custom_transformations(sql_factory.transformations):
                export_custom_transformation = JoinerManager().join_transformations(
                    export_custom_transformation,
                    self.get_custom_transformations(sql_factory.transformations),
                )
            else:
                export_custom_transformation = export_custom_transformation or self.get_custom_transformations(sql_factory.transformations)
            if export_celonis_transformation and self.get_celonis_transformations(sql_factory.transformations):
                export_celonis_transformation = JoinerManager().join_transformations(
                    export_celonis_transformation,
                    self.get_celonis_transformations(sql_factory.transformations),
                )
            else:
                export_celonis_transformation = export_celonis_transformation or self.get_celonis_transformations(sql_factory.transformations)
        if export_custom_transformation:
            transformations.append(export_custom_transformation)
        if export_celonis_transformation:
            transformations.append(export_celonis_transformation)
        return transformations

    def join_duplicate_checker_export_transformations(
        self, export_sql_factories: List[SqlFactoryTransport]
    ) -> SqlFactoryTransformationTransport:
        export_dc_transformation = self.get_duplicate_checker_transformations(
            export_sql_factories[0].transformations
        )
        if not export_dc_transformation:
            return None

        for sql_factory in export_sql_factories[1:]:
            export_dc_transformation = JoinerManager().join_transformations(
                export_dc_transformation,
                self.get_duplicate_checker_transformations(sql_factory.transformations),
            )

        return export_dc_transformation

    def filter_relationship_transformations(
        self,
        entity_name: str,
        export_transformations: SqlFactoryTransformationTransport,
        source_objects: Dict[str, ObjectEntity],
    ):
        """Filter out invalid relationship transformations."""
        export_transformations.relationship_transformations = [
            script
            for script in export_transformations.relationship_transformations
            if script.relationship_name
            in {
                r.name
                for r in source_objects.get(
                    entity_name, ObjectEntity(relationships=[])
                ).relationships
            }
        ]

    def join_transformations(
        self,
        conflict_method: str,
        import_transformations: List[SqlFactoryTransformationTransport],
        export_transformations: List[SqlFactoryTransformationTransport],
    ) -> List:
        """Join transformations for the factory update."""
        union_transformations = []
        import_custom_transformation = self.get_custom_transformations(
            import_transformations
        )
        import_celonis_transformation = self.get_celonis_transformations(
            import_transformations
        )
        if import_custom_transformation:
            export_custom_transformations = self.get_custom_transformations(
                export_transformations
            )
            union_custom_transformations = JoinerManager().join_transformations(
                import_custom_transformation,
                export_custom_transformations,
                conflict_method=conflict_method,
            )
            union_transformations.append(union_custom_transformations)

        if import_celonis_transformation:
            export_celonis_transformations = self.get_celonis_transformations(
                export_transformations
            )
            union_celonis_transformations = JoinerManager().join_transformations(
                import_celonis_transformation,
                export_celonis_transformations,
                conflict_method=conflict_method,
            )
            union_transformations.append(union_celonis_transformations)

        return union_transformations

    def join_duplicate_checker_transformations(
        self,
        conflict_method: str,
        import_transformations: List[SqlFactoryTransformationTransport],
        export_transformations: SqlFactoryTransformationTransport,
    ) -> List:
        """Join transformations for the factory update."""
        union_transformations = []
        import_dc_transformation = self.get_duplicate_checker_transformations(
            import_transformations
        )
        if import_dc_transformation:
            union_custom_transformations = JoinerManager().join_transformations(
                import_dc_transformation,
                export_transformations,
                conflict_method=conflict_method,
            )
            union_transformations.append(union_custom_transformations)
        return union_transformations

    def prepare_factory_json(self, export_factory: FactoryListTransport) -> dict:
        """Prepare JSON structure for a new factory creation."""
        factory_json = json.loads(export_factory.json())
        factory_json["target"]["entityRef"] = factory_json["target"]["entity_ref"]
        del factory_json["target"]["entity_ref"]
        return factory_json

    def get_data_source_name(
        self,
        import_data_connection_id: str,
        source_data_sources: Dict[str, FactoryDataSourceTransport],
    ) -> str:
        """Get the display name of the data source."""
        data_source = source_data_sources.get(import_data_connection_id, " - ")
        return data_source.display_name if data_source != " - " else data_source

    def get_new_factory_display_name(
        self,
        entity_name: str,
        kind_of_entity: str,
        data_source_name: str,
        export_factory: FactoryListTransport,
    ) -> str:
        """Determine the display name for the new factory."""
        return (
            f"{entity_name} transformation - copy"
            if kind_of_entity == "EVENT"
            else f"{entity_name} transformation - {data_source_name if export_factory.data_connection_id != self.OCPM_SCHEMA_ID else 'OCPM Schema'}"
        )

    def get_new_factory_data_connection_id(
        self, export_factory: FactoryListTransport, import_data_connection_id: str
    ) -> str:
        """Get the data connection ID for the new factory."""
        return (
            import_data_connection_id
            if export_factory.data_connection_id != self.OCPM_SCHEMA_ID
            else ""
        )

    def get_new_sql_transformation_data_connection_id(
        self, export_factory: FactoryListTransport, import_data_connection_id: str
    ) -> str:
        """Get the data connection ID for the new factory."""
        return (
            import_data_connection_id
            if export_factory.data_connection_id != self.OCPM_SCHEMA_ID
            else self.OCPM_SCHEMA_ID
        )

    def join_local_parameters(
        self,
        conflict_method: str,
        import_local_parameters: List,
        export_sql_factories: List,
    ) -> List:
        """Join local parameters from import and export SQL factories."""
        export_local_parameters = list(
            {
                p.name: p
                for sql_factory in export_sql_factories
                for p in sql_factory.local_parameters
            }.values()
        )
        return JoinerManager().join_parameters(
            import_list=import_local_parameters,
            export_list=export_local_parameters,
            conflict_method=conflict_method,
        )
