from app.src.business_landscape_pycelonis.service import (
    BusinessLandscapePycelonis,
    Perspective,
    ObjectEntity,
    EventEntity,
    Process as bl_Process,
    FactoryListTransport,
    SqlFactoryTransport,
    ObjectEntityRequestOptions,
    SqlFactoryRequestOptions,
    PerspectiveRequestOptions,
    ProcessUpdateOptions,
    DataSourceConnectionRequestOptions,
    FactoryDataSourceTransport,
    EventEntityRequestOptions,
    EntityRelationship,
    EntityField,
    FactoryParameter,
    FactoryTarget,
    SqlFactoryTransformationTransport,
    PerspectiveSpecObject,
    Projection,
    EntityMetadata,
    RelationshipIdentifierRequestOptions,
    RelationshipCardinality,
    ObjectRelationship,
    ObjectRelationshipRequestOptions,
    DataSourceConnection,
    CategoryValueReference,
    Environment,
    EnvironmentRequestOptions,
    CategoryValuesRequestOptions,
    PerspectiveSpecEvent,
    UserFactoryTemplateListTransport,
    UserFactoryTemplateTransport,
    UserFactoryTemplateRequestOptions,
)
from app.src.meta_types.metaTypes import Process, Factory, Object, Event, Table, App
from app.src.export_ocpm.export_ocpm import ExportOCPM
from app.src.tools.log_formatter import format_exception_for_logging
from app.src.tools.logger_setup import setup_logger
from app.src.import_ocpm.joiner_manager import JoinerManager
from app.src.ocpm.business_graph_api import BusinessGraphAPI
from app.src.ocpm import Namespace, Namespace, Method, NamespaceType, DataValidator

from app.src.handlers import ObjectHandler, FactoryHandler, EntityHandler, EventHandler

import pycelonis
import requests
from collections import defaultdict
from typing import Any, List, Dict, Union, Optional, Callable, Literal, DefaultDict


class ImportOCPM:
    OCPM_SCHEMA_ID = "00000000-0000-0000-0000-000000000000"

    def __init__(
        self,
        celonis: pycelonis.Celonis,
        workspace_id: str,
        environment: str,
        ocpm_export: ExportOCPM,
        conflict_method: str = Method.DEFAULT,
        copy_all_content: bool = False,
        logger_level: str = "INFO",
    ) -> None:
        self.celonis = celonis
        self.workspace_id = DataValidator().validate_workspace_id(workspace_id)
        self.environment = DataValidator().validate_environment(environment)

        self.api = BusinessGraphAPI(celonis.client, self.environment, self.workspace_id)

        self.logger = setup_logger("ImportOCPM", "import_ocpm", logger_level)

        self.ocpm_export = ocpm_export
        self.conflict_method = conflict_method
        self.copy_all_content = copy_all_content

        # Initialize collections and related data
        self._initialize_data_collections()
        self._initialize_deployment_lists()

        # Load initial data
        self._load_initial_data()
        self.__asset_tracking(url=self.celonis.client.base_url)

        # Initialize Handlers
        self._initialize_handlers()

    def _initialize_data_collections(self) -> None:
        """Initializes collections for storing data objects."""
        self.new_objects_ids: Dict[str, str] = {}
        self.objects: Dict[str, ObjectEntity] = {}
        self.events: Dict[str, EventEntity] = {}
        self.perspectives: Dict[str, Perspective] = {}
        self.factories: Dict[str, FactoryListTransport] = {}
        self.sql_statements: Dict[str, List[SqlFactoryTransport]] = {}
        self.catalog_processes: List[bl_Process] = []
        self.environments: Dict[str, Environment] = {}
        self.data_sources: Dict[str, FactoryDataSourceTransport] = {}
        self.template_factories: DefaultDict[
            List[UserFactoryTemplateListTransport]
        ] = defaultdict(list)
        self.templates: DefaultDict[List[UserFactoryTemplateTransport]] = defaultdict(
            list
        )

    def _initialize_deployment_lists(self) -> None:
        """Initializes lists for objects and events to be deployed."""
        self.objects_to_be_deployed: List[str] = []
        self.events_to_be_deployed: List[str] = []

    def _load_initial_data(self) -> None:
        """Loads initial data required for ImportOCPM."""
        self.logger.info("Loading initial data for ImportOCPM...")
        self.fetch_business_landscape_processes()
        self.get_environments()
        self.fetch_factory_data_sources()
        self.fetch_perspectives()
        self.logger.info("Initial data loaded successfully.")

    def _initialize_handlers(self) -> None:
        self.object_handler = ObjectHandler(logger=self.logger)
        self.event_handler = EventHandler(logger=self.logger)
        self.factory_handler = FactoryHandler(logger=self.logger)
        self.entity_handler = EntityHandler(logger=self.logger)

    def get_content_from_source_team(self) -> None:
        """Retrieves all relevant content from the source team."""
        self.logger.info("Getting content from environment ...")

        entity_retrievals = [
            (self.fetch_object_entities, Namespace.CELONIS, "Objects Entities"),
            (self.fetch_object_entities, Namespace.CUSTOM, "Custom Objects Entities"),
            (self.fetch_event_entities, Namespace.CELONIS, "Celonis Event Entities"),
            (self.fetch_event_entities, Namespace.CUSTOM, "Custom Event Entities"),
        ]
        for func, namespace, description in entity_retrievals:
            self._retrieve_entities(func, namespace, description)

        self.logger.info("Getting Perspectives")
        self.fetch_perspectives()

    def _retrieve_entities(
        self, func: Callable, namespace: Namespace, description: str
    ) -> None:
        """Helper method to retrieve entities and log the process."""
        self.logger.info(f"Getting {description}")
        func(namespace=namespace)

    def _retrieve_factories(
        self,
        data_connection_id: str,
        description: str,
        target_kind: Literal["OBJECT", "EVENT"],
    ) -> None:
        """Helper method to retrieve factories and log the process."""
        self.logger.info(f"Getting all {description}")
        self.fetch_factory_entities(
            data_connection_id=data_connection_id, target_kind=target_kind
        )

    def import_content(
        self,
        import_data_connection_id: str,
        export_data_connection_id: str,
        selected_perspectives: List[str],
        update_ccdm: bool = True,
    ):
        """Import objects, events, factories with SQL transformations and perspectives."""
        DataValidator().validate_ids(
            import_data_connection_id, export_data_connection_id
        )
        DataValidator().validate_list(selected_perspectives, "selected_perspectives")

        self._update_ccdm_version(update_ccdm)

        self.import_objects_and_events()

        self.import_templates()

        self.import_transformations(
            import_data_connection_id, export_data_connection_id
        )
        self.push_custom_perspectives(selected_perspectives)

        self.delete_overwrite_objects()
        self.logger.info("Import Completed")

    def _update_ccdm_version(self, update_ccdm: bool):
        source_develop_env = self.ocpm_export.environments.get("develop")
        target_develop_env = self.environments.get("develop")

        if source_develop_env.content_tag != target_develop_env.content_tag:
            self.logger.warning(
                f"Different CCDM Versions from source environment ({source_develop_env.content_tag}) and target environment ({target_develop_env.content_tag})"
            )
            if update_ccdm:
                self.logger.info(
                    f"Updating target environment ({target_develop_env.content_tag}) to {source_develop_env.content_tag}"
                )
                request_body = EnvironmentRequestOptions(
                    content_tag=source_develop_env.content_tag,
                    display_name=target_develop_env.display_name,
                    name=target_develop_env.name,
                    readonly=target_develop_env.readonly,
                )
                new_env = self.api.put_environment(
                    environment_id=target_develop_env.id, request_body=request_body
                )
                if new_env:
                    self.logger.info(
                        f"Target catalog version changed from {target_develop_env.content_tag} to {source_develop_env.content_tag}"
                    )
                else:
                    self.logger.error(
                        f"Failed to change catalog version from {target_develop_env.content_tag} to {source_develop_env.content_tag}"
                    )

    def import_entities(self, selected_perspectives: List[str]) -> None:
        """Import objects, events, and perspectives."""
        DataValidator().validate_list(selected_perspectives, "selected_perspectives")
        self.import_objects_and_events()
        self.push_custom_perspectives(selected_perspectives)

    def import_transformations(
        self, import_data_connection_id: str, export_data_connection_id: str
    ) -> None:
        """Import factories with SQL transformations."""
        DataValidator().validate_ids(
            import_data_connection_id, export_data_connection_id
        )
        ## OBJECT TRANSFORMATIONS
        self.get_updated_factories(import_data_connection_id, target_kind="OBJECT")
        self.get_sql_statements_from_object_factories()
        self.push_factories_to_celonis(
            import_data_connection_id, export_data_connection_id, target_kind="OBJECT"
        )

        ## EVENT TRANSFORMATIONS
        # reset import factories and sql statements
        self.factories = {}
        self.sql_statements = {}
        self.get_updated_factories(import_data_connection_id, target_kind="EVENT")
        self.get_sql_statements_from_event_factories()

        self.push_factories_to_celonis(
            import_data_connection_id, export_data_connection_id, target_kind="EVENT"
        )

    def import_templates(self) -> None:
        self.fetch_template_factories()
        self.get_templates_from_entity_factories()
        self.push_template_factories()

    def delete_overwrite_objects(self) -> None:
        """Deletes objects and events if the conflict method is set to OVERWRITE and copy_all_content is True."""
        if self._should_delete_overwrite_objects():
            self.delete_objects()
            self.delete_events()

    def _should_delete_overwrite_objects(self) -> bool:
        """Checks if overwrite objects should be deleted based on conflict method and content copy flag."""
        return self.conflict_method == Method.OVERWRITE and self.copy_all_content

    def fetch_object_entities(self, namespace: Namespace) -> None:
        self.objects = self.api.get_object_entities(self.objects, namespace)

    def fetch_factory_entities(
        self, data_connection_id: str, target_kind: Literal["OBJECT", "EVENT"]
    ) -> None:
        self.factories = self.api.get_factories_entities(
            self.factories,
            data_connection_id=data_connection_id,
            target_kind=target_kind,
        )

    def fetch_template_factories(self) -> None:
        template_factories_response = self.api.get_template_factories()
        for t in template_factories_response.content or []:
            self.template_factories[t.target.entity_ref.name].append(t)

    def fetch_event_entities(self, namespace: Namespace) -> None:
        self.events = self.api.get_event_entities(self.events, namespace)

    def get_sql_statements_from_object_factories(self) -> None:
        """Retrieves SQL statements from object factories."""
        objects_to_be_deployed = self.object_handler.normalize_object_names(
            self.objects_to_be_deployed, self.objects
        )
        self._get_sql_statements(objects_to_be_deployed)

    def get_sql_statements_from_event_factories(self) -> None:
        """Retrieves SQL statements from event factories."""
        events_to_be_deployed = self.event_handler.normalize_event_names(
            self.events_to_be_deployed, self.events
        )
        self._get_sql_statements(events_to_be_deployed)

    def get_templates_from_entity_factories(self) -> None:
        objects_to_be_deployed = self.object_handler.normalize_object_names(
            self.objects_to_be_deployed, self.objects
        )
        events_to_be_deployed = self.event_handler.normalize_event_names(
            self.events_to_be_deployed, self.events
        )
        self._get_templates(objects_to_be_deployed)
        self._get_templates(events_to_be_deployed)

    def _get_sql_statements(self, entities: List[str]) -> None:
        """Helper method to retrieve SQL statements from factories."""
        for entity_name in entities:
            factory_obj = self.get_object_factory_by_entity_name(entity_name)
            if factory_obj:
                factory_id = factory_obj.factory_id
                sql_statements = self.get_sql_scripts_from_factory(factory_id)
                if entity_name not in self.sql_statements:
                    self.sql_statements[entity_name] = [sql_statements]
                else:
                    self.sql_statements[entity_name].append(sql_statements)

    def _get_templates(self, entities: List[str]) -> None:
        """Helper method to retrieve Templates from template factories."""
        for entity_name in entities:
            factory_objects = self.get_template_factory_by_entity_name(entity_name)
            for factory in factory_objects:
                template_id = factory.id
                template = self.get_template_from_factory(template_id=template_id)
                self.templates[entity_name].append(template)

    def fetch_perspectives(self) -> None:
        perspectives = self.api.get_perspectives()
        self.perspectives = {p.name: p for p in perspectives.content}

    def get_updated_factories(
        self, data_connection_id: str, target_kind: Literal["OBJECT", "EVENT"]
    ) -> None:
        """Updates the list of factories based on data connection ID."""
        self.fetch_factory_entities(
            data_connection_id=data_connection_id, target_kind=target_kind
        )

    def get_updated_sql_statements(self) -> None:
        self.get_sql_statements_from_object_factories()
        self.get_sql_statements_from_event_factories()

    def import_objects_and_events(self) -> None:
        """Imports objects and events based on the data connection ID."""
        self.get_content_from_source_team()
        many_to_many_rels = self.push_objects_and_events_to_celonis()

        if many_to_many_rels:
            self.logger.debug("Pushing MANY_TO_MANY dependant objects")
            self.put_custom_object_types(
                include_first_level_relationships=False,
                include_second_level_relationships=True,
                dependant_objects=many_to_many_rels,
            )

    def push_objects_and_events_to_celonis(self) -> List[str]:
        """Pushes object and event types to Celonis."""
        many_to_many_rels = []
        many_to_many_rels.extend(
            self.push_celonis_object_types(with_custom_relationships=False)
        )
        self.fetch_object_entities(namespace=Namespace.CELONIS)
        self.post_custom_object_types()
        self.fetch_object_entities(namespace=Namespace.CUSTOM)
        many_to_many_rels.extend(
            self.put_custom_object_types(
                include_first_level_relationships=True,
                include_second_level_relationships=False,
            )
        )
        self.fetch_object_entities(namespace=Namespace.CUSTOM)
        many_to_many_rels.extend(
            self.push_celonis_object_types(with_custom_relationships=True)
        )
        self.fetch_object_entities(namespace=Namespace.CELONIS)
        self.put_custom_object_types(
            include_first_level_relationships=False,
            include_second_level_relationships=True,
        )
        self.fetch_object_entities(namespace=Namespace.CUSTOM)
        self.push_celonis_event_types()
        self.push_custom_event_types()
        self.fetch_event_entities(namespace=Namespace.CUSTOM)
        return many_to_many_rels

    def push_factories_to_celonis(
        self,
        import_data_connection_id: str,
        export_data_connection_id: str,
        target_kind: Literal["OBJECT", "EVENT"],
    ) -> None:
        """Imports factories from the export to the import data connection."""
        self.put_celonis_factories(
            import_data_connection_id=import_data_connection_id,
            export_data_connection_id=export_data_connection_id,
            target_kind=target_kind,
        )
        self.put_custom_factories(
            import_data_connection_id=import_data_connection_id,
            export_data_connection_id=export_data_connection_id,
            target_kind=target_kind,
        )

    def push_template_factories(self):
        objects_to_be_deployed = self.object_handler.normalize_object_names(
            self.objects_to_be_deployed, self.objects
        )
        events_to_be_deployed = self.event_handler.normalize_event_names(
            self.events_to_be_deployed, self.objects
        )

        iterate_entities = objects_to_be_deployed.union(events_to_be_deployed)

        for entity_name in iterate_entities:
            target_kind = "OBJECT" if entity_name in objects_to_be_deployed else "EVENT"
            if entity_name in objects_to_be_deployed:
                entity_name = self.object_handler.normalize_object_name(
                    entity_name, self.objects
                )
            else:
                entity_name = self.event_handler.normalize_event_name(
                    entity_name, self.events
                )

            export_template_factories = (
                self.factory_handler.get_template_factories_by_entity_name(
                    entity_name,
                    self.ocpm_export.template_factories,
                )
            )
            for template_factory in export_template_factories:
                import_factory = (
                    self.factory_handler.get_template_factories_by_entity_name_and_name(
                        entity_name=entity_name,
                        factory_name=template_factory.name,
                        template_factories=self.template_factories,
                    )
                )
                import_template_found = True if import_factory else False

                if import_template_found:
                    export_template = (
                        self.factory_handler.get_template_by_entity_name_and_name(
                            entity_name=entity_name,
                            template_name=template_factory.name,
                            templates=self.ocpm_export.templates,
                        )
                    )
                    import_template = (
                        self.factory_handler.get_template_by_entity_name_and_name(
                            entity_name=entity_name,
                            template_name=template_factory.name,
                            templates=self.templates,
                        )
                    )

                    import_template = self._update_template_transformations(
                        entity_name=entity_name,
                        export_template=export_template,
                        import_template=import_template,
                    )

                else:
                    # create a new one (POST)
                    result_factory = self._create_new_template_factory(
                        template_factory,
                    )
                    # update new name
                    export_template = (
                        self.factory_handler.get_template_by_entity_name_and_name(
                            entity_name=entity_name,
                            template_name=template_factory.name,
                            templates=self.ocpm_export.templates,
                        )
                    )
                    result_factory.name = export_template.name

                    if result_factory:
                        result_template = self._update_template_transformations(
                            entity_name=entity_name,
                            export_template=export_template,
                            import_template=result_factory,
                        )
                        self.templates[entity_name].append(result_template)

    def get_environment(self, name: str) -> Environment:
        environments = self.api.get_environments()
        for env in environments:
            if env.name == name:
                return env

    def get_environments(self) -> None:
        self.environments = {e.name: e for e in self.api.get_environments()}

    def _log_error(self, message: str, exception: Exception) -> None:
        """Logs an error message and the associated exception."""
        self.logger.error(message)
        self.logger.debug(str(exception))
        formatted_message = format_exception_for_logging(exception)
        self.logger.error(formatted_message)

    ##############################
    # Objects handling
    #############################
    def push_celonis_object_types(
        self, with_custom_relationships: bool = True
    ) -> List[str]:
        dependant_objects = []
        objects_to_be_deployed = self.object_handler.normalize_object_names(
            self.objects_to_be_deployed, self.objects
        )
        for object_name, export_object in self.ocpm_export.objects.items():
            if self.object_handler.is_celonis_object_to_be_deployed(
                object_name, export_object, objects_to_be_deployed
            ):
                self.logger.info(f"Updating celonis object {object_name}")
                original_object = self.objects.get(object_name)

                if not original_object:
                    self.logger.warning(
                        f"Celonis Object {object_name} is not enabled in Objects & Events"
                    )
                    continue

                self.entity_handler.compare_ccdm_attributes(
                    object_name,
                    export_object.fields,
                    original_object.fields,
                    "attributes",
                )

                union_fields = JoinerManager().join_entity_fields(
                    import_list=original_object.fields,
                    export_list=export_object.fields,
                    conflict_method=self.conflict_method,
                )
                union_tags = JoinerManager().join_tags(
                    import_list=original_object.tags,
                    export_list=export_object.tags,
                    conflict_method=self.conflict_method,
                )

                union_categories = JoinerManager().join_categories(
                    import_categories=original_object.categories,
                    export_categories=export_object.categories,
                    conflict_method=self.conflict_method,
                )
                ## FIXME: use till this issue is fix in the API
                self.object_handler.fix_category_values(union_categories)

                union_relationships = self.get_union_relationships(
                    original_object,
                    export_object,
                    object_name,
                    with_custom_relationships,
                    check_ccdm=True,
                )

                dependant_objects.extend(
                    self.object_handler.get_dependant_objects(
                        union_relationships,
                        self.ocpm_export.objects,
                        object_name,
                        self.objects,
                        objects_to_be_deployed,
                    )
                )
                # PUT Updated Celonis Object type
                self.put_object_type_api(
                    object_name=object_name,
                    object_type_id=original_object.id,
                    categories=union_categories,
                    color=export_object.color,
                    description=export_object.description,
                    fields=union_fields,
                    tags=union_tags,
                    relationships=union_relationships,
                )

        return dependant_objects

    def post_custom_object_types(self) -> None:
        objects_to_be_deployed = self.object_handler.normalize_object_names(
            self.objects_to_be_deployed, self.objects
        )
        for object_name, export_object in self.ocpm_export.objects.items():
            object_name = self.object_handler.normalize_object_name(
                object_name, self.objects
            )
            if self.object_handler.is_custom_object_to_be_deployed(
                object_name, export_object, objects_to_be_deployed
            ):
                original_object = self.objects.get(object_name)
                if not original_object:
                    self.logger.info(f"Creating custom object {object_name}")
                    ##
                    self.object_handler.fix_category_values_from_object(export_object)
                    ##
                    self.post_object_type_api(
                        color=export_object.color,
                        object_name=export_object.name,
                        categories=export_object.categories,
                        description=export_object.description,
                        fields=export_object.fields,
                        tags=export_object.tags,
                    )
                else:
                    self.logger.info(f"Updating custom object {object_name}")

                    union_fields = JoinerManager().join_entity_fields(
                        import_list=original_object.fields,
                        export_list=export_object.fields,
                        conflict_method=self.conflict_method,
                    )
                    union_tags = JoinerManager().join_tags(
                        import_list=original_object.tags,
                        export_list=export_object.tags,
                        conflict_method=self.conflict_method,
                    )
                    relationship_list = self.object_handler.filter_valid_relationships(
                        original_object, export_object, object_name, self.objects
                    )
                    union_categories = JoinerManager().join_categories(
                        import_categories=original_object.categories,
                        export_categories=export_object.categories,
                        conflict_method=self.conflict_method,
                    )

                    ## FIXME: use till this issue is fix in the API
                    self.object_handler.fix_category_values(union_categories)

                    self.put_object_type_api(
                        object_name=export_object.name,
                        object_type_id=original_object.id,
                        categories=union_categories,
                        color=export_object.color,
                        description=export_object.description,
                        fields=union_fields,
                        tags=union_tags,
                        relationships=relationship_list,
                    )

    def put_custom_object_types(
        self,
        include_first_level_relationships: bool = True,
        include_second_level_relationships: bool = True,
        dependant_objects: List[str] = [],
    ) -> None:
        objects_to_be_deployed = self.object_handler.normalize_object_names(
            self.objects_to_be_deployed, self.objects
        )
        for object_name, export_object in self.ocpm_export.objects.items():
            object_name = self.object_handler.normalize_object_name(
                object_name, self.objects
            )
            if self.object_handler.is_custom_object_to_be_deployed(
                object_name, export_object, objects_to_be_deployed
            ) or (
                include_second_level_relationships and object_name in dependant_objects
            ):
                self.logger.info(
                    f"Updating custom relationships for object {object_name}"
                )

                original_object = self.objects.get(object_name)

                relationships_list = []
                if include_first_level_relationships:
                    relationships_list = (
                        self.object_handler.get_first_level_relationships(
                            self.conflict_method,
                            export_object,
                            original_object,
                            self.objects,
                        )
                    )
                    self.object_handler.update_mapped_by_attributes(
                        object_name, relationships_list, self.objects
                    )
                    dependant_objects.extend(
                        self.object_handler.get_dependant_objects(
                            relationships_list,
                            self.ocpm_export.objects,
                            object_name,
                            self.objects,
                            objects_to_be_deployed,
                        )
                    )

                if include_second_level_relationships:
                    relationships_list = (
                        self.object_handler.get_second_level_relationships(
                            object_name,
                            original_object,
                            relationships_list,
                            export_object.relationships,
                            conflict_method=self.conflict_method,
                            source_objects=self.objects,
                        )
                    )

                self.put_object_type_api(
                    object_name=object_name,
                    object_type_id=original_object.id,
                    color=original_object.color,
                    categories=original_object.categories,
                    description=original_object.description,
                    fields=original_object.fields,
                    tags=original_object.tags,
                    relationships=relationships_list,
                )

        return dependant_objects

    ##############################
    # Events handling
    #############################
    def push_celonis_event_types(self) -> None:
        events_to_be_deployed = self.event_handler.normalize_event_names(
            self.events_to_be_deployed, self.events
        )
        for event_name, export_event in self.ocpm_export.events.items():
            event_name = self.event_handler.normalize_event_name(
                event_name, self.events
            )
            if self.event_handler.is_celonis_event_to_be_deployed(
                event_name, export_event, events_to_be_deployed, self.events
            ):
                self.logger.info(f"Update celonis event {event_name}")
                import_event = self.events.get(event_name)
                if import_event:
                    self.entity_handler.compare_ccdm_attributes(
                        event_name,
                        export_event.fields,
                        import_event.fields,
                        "attributes",
                    )

                    self.entity_handler.compare_ccdm_attributes(
                        event_name,
                        export_event.relationships,
                        import_event.relationships,
                        "relationships",
                    )

                    ## FIXME: use till this issue is fix in the API
                    self.event_handler.fix_category_values_from_event(export_event)

                    self.put_event_type_api(
                        event_id=import_event.id,
                        event_name=export_event.name,
                        categories=export_event.categories,
                        description=export_event.description,
                        fields=export_event.fields,
                        relationships=[
                            r
                            for r in export_event.relationships
                            if (r.target.object_ref.name in self.objects)
                            or (r.namespace in Namespace.CELONIS)
                        ],
                        tags=export_event.tags,
                    )

    def push_custom_event_types(self) -> None:
        events_to_be_deployed = self.event_handler.normalize_event_names(
            self.events_to_be_deployed, self.events
        )
        for event_name, export_event in self.ocpm_export.events.items():
            event_name = self.event_handler.normalize_event_name(
                event_name, self.events
            )
            if self.event_handler.is_custom_event_to_be_deployed(
                event_name, export_event, events_to_be_deployed
            ):
                self.logger.info(f"Update custom event {event_name}")
                import_event = self.events.get(event_name)
                if import_event:
                    union_fields = JoinerManager().join_entity_fields(
                        import_list=import_event.fields,
                        export_list=export_event.fields,
                        conflict_method=self.conflict_method,
                    )
                    union_relationships = self.object_handler.join_relationships(
                        import_relationships=import_event.relationships,
                        export_relationships=export_event.relationships,
                        object_name=event_name,
                        objects_to_be_deployed=self.object_handler.normalize_object_names(
                            self.objects_to_be_deployed, self.objects
                        ),
                        source_objects=self.objects,
                        conflict_method=self.conflict_method,
                    )

                    union_categories = JoinerManager().join_categories(
                        import_categories=import_event.categories,
                        export_categories=export_event.categories,
                        conflict_method=self.conflict_method,
                    )

                    ## FIXME: use till this issue is fix in the API
                    self.object_handler.fix_category_values(union_categories)

                    self.put_event_type_api(
                        event_id=import_event.id,
                        event_name=event_name,
                        description=export_event.description,
                        categories=union_categories,
                        fields=union_fields,
                        relationships=union_relationships,
                        tags=export_event.tags,
                    )

                else:
                    ## FIXME: use till this issue is fix in the API
                    self.event_handler.fix_category_values_from_event(export_event)

                    self.post_event_type_api(
                        event_name=event_name,
                        description=export_event.description,
                        categories=export_event.categories,
                        fields=export_event.fields,
                        relationships=[
                            r
                            for r in export_event.relationships
                            if r.target.object_ref.name in self.objects
                        ],
                        tags=export_event.tags,
                    )

    ##############################
    # Perspectives handling
    #############################
    def push_custom_perspectives(self, selected_perspectives: List[str]) -> None:
        for perspective_name, perspective_aux in self.ocpm_export.perspectives.items():
            if (
                perspective_name in selected_perspectives
                and perspective_aux.namespace == NamespaceType.CUSTOM
            ):
                import_perspective = self.perspectives.get(perspective_name)
                export_perspective = self.ocpm_export.perspectives.get(perspective_name)

                self.object_handler.normalize_object_name_in_perspective(
                    export_perspective, self.objects
                )
                self.event_handler.normalize_event_name_in_perspective(
                    export_perspective, self.events
                )

                if not import_perspective:
                    self.logger.info(f"Create custom perspective {perspective_name}")
                    self.post_perspective_api(
                        default_projection=export_perspective.default_projection,
                        description=export_perspective.description,
                        name=export_perspective.name,
                        objects=export_perspective.objects,
                        events=export_perspective.events,
                        projections=export_perspective.projections,
                        tags=export_perspective.tags,
                        base_ref=export_perspective.base_ref,
                    )
                else:
                    self.logger.info(f"Update custom perspective {perspective_name}")
                    self.put_perspective_api(
                        perspective_id=import_perspective.id,
                        default_projection=export_perspective.default_projection,
                        description=export_perspective.description,
                        name=export_perspective.name,
                        objects=export_perspective.objects,
                        events=export_perspective.events,
                        projections=export_perspective.projections,
                        tags=export_perspective.tags,
                        base_ref=export_perspective.base_ref,
                    )

        if self.conflict_method == Method.OVERWRITE and self.copy_all_content:
            self.fetch_perspectives()
            for perspective_name, perspective in self.perspectives.items():
                if perspective_name not in self.ocpm_export.perspectives:
                    if perspective.namespace == NamespaceType.CUSTOM:
                        self.delete_perspective_api(perspective.id)

    ##############################
    # Factories & Transformations
    ##############################
    def put_celonis_factories(
        self,
        export_data_connection_id: str,
        import_data_connection_id: str,
        target_kind: Literal["OBJECT", "EVENT"],
    ):
        iterate_entities = (
            self.objects_to_be_deployed
            if target_kind == "OBJECT"
            else self.events_to_be_deployed
        )

        for entity_name in iterate_entities:
            export_factories = {
                key.lower(): f for key, f in self.ocpm_export.factories.items()
            }.get(entity_name.lower(), [])
            export_factories = [
                f
                for f in export_factories
                if self.factory_handler.get_export_factory_kind(f) == target_kind
            ]

            for export_factory in export_factories:
                if self.factory_handler.should_update_celonis_factory(
                    export_factory,
                    entity_name,
                    export_data_connection_id,
                    target_kind,
                    self.object_handler.normalize_object_names(
                        self.objects_to_be_deployed, self.objects
                    ),
                    self.event_handler.normalize_event_names(
                        self.events_to_be_deployed, self.events
                    ),
                    self.objects,
                    self.events,
                ):
                    import_factory = self.factories.get(entity_name)
                    if (
                        import_factory
                        and self.factory_handler.is_valid_import_celonis_factory(
                            import_factory, import_data_connection_id
                        )
                    ):
                        self.logger.info(
                            f"Update transformation on Celonis Transformation {entity_name}"
                        )
                        export_sql_factory = import_sql_factory = None
                        (
                            import_sql_factory,
                            export_sql_factory,
                        ) = self.factory_handler.get_matching_sql_factories(
                            self.ocpm_export.sql_statements,
                            self.sql_statements,
                            entity_name,
                            import_factory,
                            export_factory,
                        )

                        if import_sql_factory and export_sql_factory:
                            self._update_celonis_factory(
                                self.factory_handler.get_kind_of_entity(export_factory),
                                import_factory,
                                export_sql_factory,
                                import_sql_factory,
                                import_data_connection_id,
                            )

    def put_custom_factories(
        self,
        export_data_connection_id: str,
        import_data_connection_id: str,
        target_kind: Literal["OBJECT", "EVENT"],
    ):
        self.logger.info(
            f"Copying transformations with Data Connection"
            f'{export_data_connection_id if export_data_connection_id else " (Global)"} '
            f"from source Data Pool into transformations with Data Connection "
            f'{import_data_connection_id if import_data_connection_id else " (Global)"} '
            f"to target Data Pool"
        )
        objects_to_be_deployed = self.object_handler.normalize_object_names(
            self.objects_to_be_deployed, self.objects
        )
        events_to_be_deployed = self.event_handler.normalize_event_names(
            self.events_to_be_deployed, self.objects
        )

        iterate_entities = (
            self.objects_to_be_deployed
            if target_kind == "OBJECT"
            else self.events_to_be_deployed
        )

        for entity_name in iterate_entities:
            if target_kind == "OBJECT":
                entity_name = self.object_handler.normalize_object_name(
                    entity_name, self.objects
                )
            else:
                entity_name = self.event_handler.normalize_event_name(
                    entity_name, self.events
                )

            export_factories = {
                key.lower(): f for key, f in self.ocpm_export.factories.items()
            }.get(entity_name.lower(), [])
            export_factories = [
                f
                for f in export_factories
                if self.factory_handler.get_export_factory_kind(f) == target_kind
            ]

            custom_export_factories = self.factory_handler.get_custom_export_factories(
                export_factories,
                entity_name,
                export_data_connection_id,
                objects_to_be_deployed,
                events_to_be_deployed,
                self.objects,
                self.events,
            )
            if custom_export_factories:
                # POST Factory for object
                export_factory = custom_export_factories[0]
                kind_of_entity = self.factory_handler.get_kind_of_entity(export_factory)

                import_sql_factory_found = False
                import_factory = self.factories.get(entity_name)

                import_factory = self.factories.get(entity_name)
                export_factories_ids = [
                    export_factory.factory_id.split("_")[0]
                    for export_factory in custom_export_factories
                ]
                if import_factory and self.factory_handler.is_valid_import_factory(
                    import_factory, import_data_connection_id, kind_of_entity
                ):
                    import_sql_factory_found = self._update_existing_factory(
                        entity_name,
                        import_factory,
                        custom_export_factories,
                        import_data_connection_id,
                        export_factories_ids,
                    )
                    if not import_sql_factory_found:
                        self._create_new_factory(
                            entity_name,
                            export_factory,
                            import_data_connection_id,
                            kind_of_entity,
                            export_factories_ids,
                        )
                else:
                    self._create_new_factory(
                        entity_name,
                        export_factory,
                        import_data_connection_id,
                        kind_of_entity,
                        export_factories_ids,
                    )

            else:
                self._handle_no_custom_factories(entity_name, export_data_connection_id)

    def delete_objects(self):
        self.fetch_object_entities(namespace=Namespace.CUSTOM)

        for obj_name in list(self.objects.keys()):
            if obj_name not in self.ocpm_export.objects.keys():
                if (
                    (self.objects.get(obj_name).namespace == NamespaceType.CUSTOM)
                ):
                    self.delete_object_entity_by_name(obj_name)

        self.fetch_object_entities(namespace=Namespace.CUSTOM)
        # clean relationships
        for obj_name, obj_entity in self.objects.items():
            ##
            self.object_handler.fix_category_values_from_object(obj_entity)
            ##
            self.put_object_type_api(
                object_name=obj_entity.name,
                object_type_id=obj_entity.id,
                categories=obj_entity.categories,
                color=obj_entity.color,
                description=obj_entity.description,
                fields=obj_entity.fields,
                tags=obj_entity.tags,
                relationships=[
                    r
                    for r in obj_entity.relationships
                    if (r.target.object_ref.name in self.objects)
                    or (r.namespace in Namespace.CELONIS)
                ],
            )

    def delete_events(self):
        self.fetch_object_entities(namespace=Namespace.CUSTOM)
        self.fetch_event_entities(namespace=Namespace.CUSTOM)

        for event_name in list(self.events.keys()):
            if event_name not in self.ocpm_export.events.keys():
                if self.events.get(event_name).namespace == NamespaceType.CUSTOM:
                    self.delete_event_entity_by_name(event_name)

        self.fetch_event_entities(namespace=Namespace.CUSTOM)
        # clean relationships
        for event_name, event_entity in self.events.items():
            if event_entity.namespace == NamespaceType.CUSTOM:
                self.event_handler.fix_category_values_from_event(event_entity)
                self.put_event_type_api(
                    event_id=event_entity.id,
                    event_name=event_entity.name,
                    categories=event_entity.categories,
                    description=event_entity.description,
                    fields=event_entity.fields,
                    relationships=[
                        r
                        for r in event_entity.relationships
                        if r.target.object_ref.name in self.objects
                    ],
                    tags=event_entity.tags,
                )

    def fetch_factory_data_sources(self) -> None:
        self.data_sources = {
            d.data_source_id: d for d in self.api.get_factories_data_sources()
        }

    def fetch_business_landscape_processes(self) -> None:
        catalog_processes = self.api.get_bl_processes()
        self.catalog_processes = {p.name: p for p in catalog_processes.content}

    def get_sql_scripts_from_factory(self, factory_id: str) -> SqlFactoryTransport:
        return self.api.get_sql_transform_from_factory(factory_id)

    def get_template_from_factory(self, template_id: str) -> SqlFactoryTransport:
        return self.api.get_sql_transform_template_from_template_id(template_id)

    def get_object_factory_by_entity_name(
        self, entity_name
    ) -> List[FactoryListTransport]:
        return self.factories.get(entity_name)

    def get_template_factory_by_entity_name(
        self, entity_name
    ) -> List[UserFactoryTemplateListTransport]:
        return self.template_factories[entity_name]

    def get_object_entity_by_name(self, object_name: str) -> Union[ObjectEntity, None]:
        return self.objects.get(object_name)

    def get_event_entity_by_name(self, event_name: str) -> Union[EventEntity, None]:
        return self.events.get(event_name)

    def enable_process_api(self, process_name: str) -> Process:
        return self.api.enable_process(process_name=process_name)

    def deploy_catalog_process_transformations_api(
        self,
        process_name: str,
        data_source_connections: List[DataSourceConnection],
    ) -> None:
        request_body = ProcessUpdateOptions(
            dataSourceConnections=[
                DataSourceConnectionRequestOptions(
                    dataSourceId=data_connection.data_source_id,
                    enabled=data_connection.enabled,
                    transformationType=data_connection.transformation_type,
                )
                for data_connection in data_source_connections
            ],
            description="",
            displayName="",
        )
        return self.api.deploy_catalog_process_transformations_api(
            process_name=process_name, request_body=request_body
        )

    def enable_needed_processes(
        self,
        processes_to_deploy: List[str],
        data_connection_id: str,
        transformation_type: str = "sap-ecc",
    ) -> None:
        if not isinstance(processes_to_deploy, list):
            raise TypeError("processes_to_deploy {processes_to_deploy} is not a list")
        if processes_to_deploy:
            if not DataValidator().validate_id_format(data_connection_id):
                if data_connection_id == "":
                    self.logger.error(
                        "You cannot use a Global Connection to deploy Catalog Processes"
                    )
                raise ValueError(
                    f'data_connection_id "{data_connection_id}" is not a valid Data Connection ID'
                )

            for process_name, process in self.catalog_processes.items():
                if process.display_name in processes_to_deploy:
                    if not process.enabled:
                        self.logger.info(
                            f"Process {process.display_name} is not enabled"
                        )
                        self.logger.info(f"Enabling process {process.display_name}")
                        self.enable_process_api(process_name=process.name)

                    else:
                        self.logger.info(
                            f"Process {process.display_name} is already enabled"
                        )
                    if transformation_type in ["sap-ecc", "oracle"]:
                        
                        transformations_enabled = False
                        data_source_in_list = False
                        for process_data_connection in process.data_source_connections:
                            if (
                                process_data_connection.data_source_id == data_connection_id
                                and process_data_connection.enabled
                            ):
                                transformations_enabled = True
                            elif (
                                process_data_connection.data_source_id == data_connection_id
                                and not process_data_connection.enabled
                            ):
                                process_data_connection.enabled = True
                                transformations_enabled = False
                                data_source_in_list = True

                        if not data_source_in_list:
                            process.data_source_connections.append(
                                DataSourceConnection(
                                    data_source_id=data_connection_id,
                                    enabled=True,
                                    transformation_type=transformation_type,
                                )
                            )
                        if not transformations_enabled:
                            self.deploy_catalog_process_transformations_api(
                                process_name=process.name,
                                data_source_connections=process.data_source_connections,
                            )
                        else:
                            self.logger.info(
                                f"Transformations for process {process.display_name} and Data Connection {data_connection_id} are already enabled"
                            )
                    else:
                        self.logger.warning(f"transformation_type is not sap-ecc or oracle; the transformations will not be enabled for process {process.display_name}")

    def define_object_names_to_be_deployed_from_perspectives(
        self, selected_perspective: List[str]
    ) -> None:
        if not isinstance(selected_perspective, list):
            raise TypeError(
                f"selected_perspective {selected_perspective} is not a list"
            )

        selected_perspective = [
            perspective
            for perspective in selected_perspective
            if perspective in self.ocpm_export.processes
        ]
        objects_to_be_deployed = list(
            set(
                [
                    obj.name if isinstance(obj, Object) else obj
                    for process_name in selected_perspective
                    for obj in self.ocpm_export.processes.get(process_name).objects
                    if obj
                ]
            )
        )
        self.objects_to_be_deployed.extend(objects_to_be_deployed)
        self.objects_to_be_deployed = [x for x in set(self.objects_to_be_deployed) if x]
        if objects_to_be_deployed:
            self.logger.info(
                f'Objects {", ".join([x for x in objects_to_be_deployed if x])} were added'
            )

        events_to_be_deployed = list(
            set(
                [
                    event.name if isinstance(event, EventEntity) else event
                    for process_name in selected_perspective
                    for event in self.ocpm_export.processes.get(process_name).events
                    if event
                ]
            )
        )
        self.events_to_be_deployed.extend(events_to_be_deployed)
        self.events_to_be_deployed = [x for x in set(self.events_to_be_deployed) if x]

        for event_name, event in self.ocpm_export.events.items():
            for rel in event.relationships:
                object_ref_name = rel.target.object_ref.name
                if (
                    object_ref_name in self.objects_to_be_deployed
                    and event_name not in self.events_to_be_deployed
                ):
                    self.events_to_be_deployed.append(event_name)

        if self.events_to_be_deployed:
            self.logger.info(
                f'Events {", ".join(self.events_to_be_deployed)} were added'
            )

    def define_object_names_to_be_deployed(self, object_names: List[str]) -> None:
        if isinstance(object_names, list):
            self.objects_to_be_deployed.extend(object_names)
            self.objects_to_be_deployed = list(set(self.objects_to_be_deployed))
            if object_names:
                self.logger.info(f'Objects {", ".join(object_names)} were added')
        else:
            self.logger.error("value for object_names is not a list")

    def define_event_names_to_be_deployed(self, event_names: List[str]) -> None:
        if isinstance(event_names, list):
            self.events_to_be_deployed.extend(event_names)
            self.events_to_be_deployed = list(set(self.events_to_be_deployed))
            if event_names:
                self.logger.info(f'Events {", ".join(event_names)} were added')
        else:
            self.logger.error("value for object_names is not a list")

    ##############################
    # API Handling
    ##############################
    def put_object_type_api(
        self,
        object_name: str,
        object_type_id: str,
        categories: List[CategoryValueReference],
        color: str,
        description: str,
        fields: List[EntityField],
        tags: List[str],
        relationships: List[EntityRelationship],
    ) -> ObjectEntity:
        request_body = ObjectEntityRequestOptions(
            categories=categories,
            color=color,
            description=description,
            fields=fields,
            name=object_name,
            tags=tags,
            relationships=relationships or [],
        )
        result_object = self.api.put_object_type(
            object_type_id=object_type_id,
            request_body=request_body,
        )
        if result_object:
            self.objects[result_object.name] = result_object
        return result_object

    def post_object_type_api(
        self,
        object_name: str,
        categories: List[CategoryValueReference],
        color: str,
        description: str,
        fields: List[EntityField],
        tags: List[str],
    ) -> ObjectEntity:
        request_body = ObjectEntityRequestOptions(
            categories=categories,
            color=color,
            description=description,
            fields=fields,
            name=object_name,
            tags=tags,
            relationships=[],
        )
        result_object = self.api.post_object_type(
            request_body=request_body,
        )
        if result_object:
            self.objects[result_object.name] = result_object
        return result_object

    def put_factories_sql_factory_api(
        self,
        factory_id: str,
        data_connection_id: str,
        disabled: bool,
        description: str,
        display_name: str,
        local_parameters: List[FactoryParameter],
        namespace: str,
        target: FactoryTarget,
        transformations: List[SqlFactoryTransformationTransport],
        user_template_name: str = None,
    ) -> SqlFactoryTransport:
        request_body = SqlFactoryRequestOptions(
            dataConnectionId=data_connection_id,
            description=description,
            displayName=display_name,
            draft=False,
            disabled=disabled,
            localParameters=local_parameters,
            namespace=namespace,
            target=target,
            transformations=transformations,
            factory_id=factory_id,
            save_mode="VALIDATE",
            user_template_name=user_template_name,
        )
        return self.api.put_factories_sql_factory(
            factory_id=factory_id, request_body=request_body
        )

    def put_template_api(
        self,
        template_id: str,
        description: str,
        name: str,
        local_parameters: List[FactoryParameter],
        target: FactoryTarget,
        transformations: List[SqlFactoryTransformationTransport],
        updated_sql_factories: Optional[
            "Dict[str, Optional[SqlFactoryRequestOptions]]"
        ],
    ) -> SqlFactoryTransport:
        # TODO: updated_sql_factories is a problem --> need to get all of the dependant instances and add them in the list
        request_body = UserFactoryTemplateRequestOptions(
            description=description,
            name=name,
            draft=False,
            local_parameters=local_parameters,
            target=target,
            transformations=transformations,
            updated_sql_factories=updated_sql_factories,
        )
        return self.api.put_template(template_id=template_id, request_body=request_body)

    def post_custom_factory_api(
        self,
        data_connection_id: str,
        target: FactoryTarget,
        display_name: str,
        user_template_name: str,
    ) -> dict:
        factory_request_body = self.api.create_factory_request_body(
            data_connection_id=data_connection_id,
            target=target,
            display_name=display_name,
            user_template_name=user_template_name,
        )

        return self.api.post_custom_factory(request_body=factory_request_body)

    def post_perspective_api(
        self,
        default_projection: str,
        description: str,
        name: str,
        objects: List[PerspectiveSpecObject],
        events: List[PerspectiveSpecEvent],
        projections: List[Projection],
        tags: List[str],
        base_ref: Optional[EntityMetadata],
    ) -> Perspective:
        """Posts a perspective, using v2 API if applicable."""
        request_body = PerspectiveRequestOptions(
            defaultProjection=default_projection,
            description=description,
            name=name,
            objects=objects,
            events=events,
            projections=projections,
            tags=tags,
            base_ref=base_ref,
        )
        return self.api.post_perspective(request_body=request_body)

    def put_perspective_api(
        self,
        perspective_id: str,
        default_projection: str,
        description: str,
        name: str,
        objects: List[PerspectiveSpecObject],
        events: List[PerspectiveSpecEvent],
        projections: List[Projection],
        tags: List[str],
        base_ref: Optional[EntityMetadata],
    ) -> Perspective:
        """Updates a perspective, using v2 API if applicable."""
        request_body = PerspectiveRequestOptions(
            defaultProjection=default_projection,
            description=description,
            name=name,
            objects=objects,
            events=events,
            projections=projections,
            tags=tags,
            base_ref=base_ref,
        )
        return self.api.put_perspective(
            perspective_id=perspective_id, request_body=request_body
        )

    def post_event_type_api(
        self,
        event_name: str,
        categories: List[CategoryValueReference],
        description: str,
        fields: List[EntityField],
        relationships: List[EntityRelationship],
        tags: List[str],
    ) -> EventEntity:
        """Posts an event type, using v2 API if applicable."""
        request_body = EventEntityRequestOptions(
            categories=categories,
            description=description,
            fields=fields,
            name=event_name,
            relationships=relationships,
            tags=tags,
        )
        result_event = self.api.post_event_type(request_body=request_body)
        if result_event:
            self.events[event_name] = result_event
        return result_event

    def put_event_type_api(
        self,
        event_id: str,
        event_name: str,
        categories: List[CategoryValueReference],
        description: str,
        fields: List[EntityField],
        relationships: List[EntityRelationship],
        tags: List[str],
    ) -> EventEntity:
        """Updates an event type, using v2 API if applicable."""
        request_body = EventEntityRequestOptions(
            categories=categories,
            description=description,
            fields=fields,
            name=event_name,
            relationships=relationships,
            tags=tags,
        )
        result_event = self.api.put_event_type(
            event_type_id=event_id, request_body=request_body
        )
        if result_event:
            self.events[event_name] = result_event
        return result_event

    def post_object_relationship_api(
        self,
        bidirectional: bool,
        cardinality: str,
        source: RelationshipIdentifierRequestOptions,
        target: RelationshipIdentifierRequestOptions,
    ) -> ObjectRelationship:
        """Posts an object relationship, using v2 API if applicable."""
        request_body = ObjectRelationshipRequestOptions(
            bidirectional=bidirectional,
            cardinality=cardinality,
            source=source,
            target=target,
        )
        return self.api.post_object_relationship(request_body=request_body)

    def get_union_relationships(
        self,
        original_object: ObjectEntity,
        export_object: ObjectEntity,
        object_name: str,
        with_custom_relationships: bool,
        check_ccdm=False,
    ) -> List[EntityRelationship]:
        if with_custom_relationships:
            if check_ccdm:
                self.entity_handler.compare_ccdm_attributes(
                    object_name,
                    export_object.relationships,
                    original_object.relationships,
                    "relationships",
                )
            union_relationships = self.object_handler.merge_custom_relationships(
                original_object,
                export_object,
                object_name,
                self.conflict_method,
                self.object_handler.normalize_object_names(
                    self.objects_to_be_deployed, self.objects
                ),
                self.objects,
            )
        else:
            if check_ccdm:
                self.entity_handler.compare_ccdm_attributes(
                    object_name,
                    export_object.relationships,
                    original_object.relationships,
                    "relationships",
                )
            union_relationships = self.object_handler.merge_default_relationships(
                original_object,
                export_object,
                object_name,
                self.conflict_method,
                self.objects,
            )

        return union_relationships

    def create_relationship_identifier(
        self, object_ref: EntityMetadata, relationship_name: Optional[str]
    ) -> RelationshipIdentifierRequestOptions:
        """Creates a relationship identifier."""
        return RelationshipIdentifierRequestOptions(
            object=object_ref, relationship=relationship_name
        )

    def create_object_relationship(
        self,
        bidirectional: bool,
        cardinality: str,
        source: RelationshipIdentifierRequestOptions,
        target: RelationshipIdentifierRequestOptions,
    ) -> ObjectRelationship:
        """Creates an object relationship with validation."""
        valid_cardinalities = [
            RelationshipCardinality.ONE_TO_MANY,
            RelationshipCardinality.MANY_TO_ONE,
            RelationshipCardinality.ONE_TO_ONE,
            RelationshipCardinality.MANY_TO_MANY,
        ]
        if cardinality not in valid_cardinalities:
            raise ValueError(f'cardinality not in {", ".join(valid_cardinalities)}')

        result_relationship = self.post_object_relationship_api(
            bidirectional=bidirectional,
            cardinality=cardinality,
            source=source,
            target=target,
        )

        if result_relationship:
            self._update_object_types(result_relationship)
            return result_relationship

    def delete_object_type_by_id_api(self, object_id: str) -> None:
        """Deletes an object type by ID, using v2 API if applicable."""
        return self.api.delete_object_type(object_type_id=object_id)

    def delete_event_type_by_id_api(self, event_id: str) -> None:
        """Deletes an event type by ID, using v2 API if applicable."""
        return self.api.delete_event_type(event_type_id=event_id)

    def delete_factory_type_by_id_api(self, factory_id: str) -> None:
        """Deletes a factory type by ID, using v2 API if applicable."""
        return self.api.delete_factory(factory_id=factory_id)

    def delete_perspective_api(self, perspective_id: str) -> None:
        """Deletes a perspective by ID, using v2 API if applicable."""
        return self.api.delete_perspective(perspective_id=perspective_id)

    def _get_union_transformations(
        self,
        export_factory_kind: str,
        import_celonis_transformation: SqlFactoryTransformationTransport,
        export_celonis_transformation: SqlFactoryTransformationTransport,
        import_custom_transformation: SqlFactoryTransformationTransport,
        export_custom_transformation: SqlFactoryTransformationTransport,
    ) -> list:
        """Determine the union of transformations based on the conflict method."""
        if self.conflict_method in (Method.OVERWRITE, Method.MERGE_OVERWRITE):
            union_transformations = [export_celonis_transformation]
        else:
            self.factory_handler.apply_overwrite_transformations(
                export_factory_kind,
                import_celonis_transformation,
                export_celonis_transformation,
            )
            union_transformations = [import_celonis_transformation]

        if export_custom_transformation:
            union_custom_transformations = JoinerManager().join_transformations(
                import_custom_transformation,
                export_custom_transformation,
                conflict_method=self.conflict_method,
            )
            union_transformations.append(union_custom_transformations)

        return union_transformations

    def _update_celonis_factory(
        self,
        export_factory_kind: str,
        import_factory: FactoryListTransport,
        export_sql_factory: SqlFactoryTransport,
        import_sql_factory: SqlFactoryTransport,
        import_data_connection_id: str,
    ):
        """Update the Celonis factory with the new transformations and parameters."""
        union_local_parameters = JoinerManager().join_parameters(
            import_list=import_sql_factory.local_parameters,
            export_list=export_sql_factory.local_parameters,
            conflict_method=self.conflict_method,
        )

        import_custom_transformation = self.factory_handler.get_custom_transformations(
            import_sql_factory.transformations
        )
        export_custom_transformation = self.factory_handler.get_custom_transformations(
            export_sql_factory.transformations
        )

        import_celonis_transformation = (
            self.factory_handler.get_celonis_transformations(
                import_sql_factory.transformations
            )
        )
        export_celonis_transformation = (
            self.factory_handler.get_celonis_transformations(
                export_sql_factory.transformations
            )
        )

        union_transformations = self._get_union_transformations(
            export_factory_kind=export_factory_kind,
            import_celonis_transformation=import_celonis_transformation,
            export_celonis_transformation=export_celonis_transformation,
            import_custom_transformation=import_custom_transformation,
            export_custom_transformation=export_custom_transformation,
        )

        self.put_factories_sql_factory_api(
            factory_id=import_sql_factory.factory_id,
            data_connection_id=import_data_connection_id
            if export_sql_factory.data_connection_id != self.OCPM_SCHEMA_ID
            else self.OCPM_SCHEMA_ID,
            description="",
            display_name=import_factory.display_name,
            disabled=export_sql_factory.disabled,
            local_parameters=union_local_parameters,
            namespace=export_sql_factory.namespace,
            target=export_sql_factory.target,
            transformations=union_transformations,
            user_template_name=None,
        )

    def _compare_ccdm_attributes(
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

    def _update_existing_factory(
        self,
        entity_name: str,
        import_factory: FactoryListTransport,
        custom_export_factories: List[FactoryListTransport],
        import_data_connection_id: str,
        export_factories_ids: List[str],
    ) -> bool:
        """Update existing import factory if it matches the export data."""
        import_sql_factory = self.factory_handler.get_import_sql_factory(
            entity_name, import_factory, self.sql_statements
        )

        if import_sql_factory:
            export_sql_factories = self.factory_handler.get_export_sql_factories(
                self.ocpm_export.sql_statements, entity_name, export_factories_ids
            )

            if export_sql_factories:
                self._update_factory_transformations(
                    entity_name,
                    import_sql_factory,
                    export_sql_factories,
                    custom_export_factories[0],
                    import_data_connection_id,
                )
                return True

        return False

    def _update_factory_transformations(
        self,
        entity_name: str,
        import_sql_factory: SqlFactoryTransport,
        export_sql_factories: List[SqlFactoryTransport],
        export_factory: FactoryListTransport,
        import_data_connection_id: str,
    ):
        """Update the SQL factory with new transformations and parameters."""
        union_local_parameters = self.factory_handler.join_local_parameters(
            self.conflict_method,
            import_sql_factory.local_parameters,
            export_sql_factories,
        )

        export_sql_factory_transformations = (
            self.factory_handler.join_custom_export_transformations(
                export_sql_factories
            )
        )
        if entity_name in self.objects:
            for transformation in export_sql_factory_transformations:
                self.factory_handler.filter_relationship_transformations(
                    entity_name, transformation, self.objects
                )
        if entity_name in self.events:
            for transformation in export_sql_factory_transformations:
                self.factory_handler.filter_relationship_transformations(
                    entity_name, transformation, self.events
                )

        union_transformations = self.factory_handler.join_transformations(
            self.conflict_method,
            import_sql_factory.transformations,
            export_sql_factory_transformations,
        )

        export_dc_sql_factory_transformations = (
            self.factory_handler.join_duplicate_checker_export_transformations(
                export_sql_factories
            )
        )

        if export_dc_sql_factory_transformations:
            if entity_name in self.objects:
                self.factory_handler.filter_relationship_transformations(
                    entity_name, export_dc_sql_factory_transformations, self.objects
                )
            if entity_name in self.events:
                self.factory_handler.filter_relationship_transformations(
                    entity_name, export_dc_sql_factory_transformations, self.events
                )

            duplicate_checker_union_transformations = (
                self.factory_handler.join_duplicate_checker_transformations(
                    self.conflict_method,
                    import_sql_factory.transformations,
                    export_dc_sql_factory_transformations,
                )
            )

            union_transformations.extend(duplicate_checker_union_transformations)

        self.logger.info(f"Updating transformation for {entity_name}")
        user_template_name = None
        if import_sql_factory.has_user_template:
            user_template_name = export_factory.user_factory_template_reference.name

        self.put_factories_sql_factory_api(
            factory_id=import_sql_factory.factory_id,
            data_connection_id=import_sql_factory.data_connection_id,
            description="",
            display_name=import_sql_factory.display_name,
            disabled=export_factory.disabled,
            local_parameters=union_local_parameters,
            namespace=export_factory.namespace,
            target=export_factory.target,
            transformations=union_transformations,
            user_template_name=user_template_name,
        )

    def _update_template_transformations(
        self,
        entity_name: str,
        export_template: UserFactoryTemplateTransport,
        import_template: Union[
            UserFactoryTemplateTransport, UserFactoryTemplateListTransport
        ],
    ):
        # FIXME: update function with relevant updates
        # NOW: just testing
        if isinstance(import_template, UserFactoryTemplateListTransport):
            # Not template has been created for import_template
            return self.put_template_api(
                template_id=import_template.id,
                description=export_template.description,
                name=import_template.name,
                local_parameters=export_template.local_parameters,
                target=export_template.target,
                transformations=export_template.transformations,
                updated_sql_factories={},
            )
        else:
            union_local_parameters = self.factory_handler.join_local_parameters(
                self.conflict_method,
                import_template.local_parameters,
                [export_template],
            )

            if entity_name in self.objects:
                for transformation in export_template.transformations:
                    self.factory_handler.filter_relationship_transformations(
                        entity_name, transformation, self.objects
                    )
            if entity_name in self.events:
                for transformation in export_template.transformations:
                    self.factory_handler.filter_relationship_transformations(
                        entity_name, transformation, self.events
                    )

            union_transformations = self.factory_handler.join_transformations(
                self.conflict_method,
                import_template.transformations,
                export_template.transformations,
            )

            export_dc_sql_factory_transformations = (
                self.factory_handler.join_duplicate_checker_export_transformations(
                    [export_template]
                )
            )

            if export_dc_sql_factory_transformations:
                if entity_name in self.objects:
                    self.factory_handler.filter_relationship_transformations(
                        entity_name, export_dc_sql_factory_transformations, self.objects
                    )
                if entity_name in self.events:
                    self.factory_handler.filter_relationship_transformations(
                        entity_name, export_dc_sql_factory_transformations, self.events
                    )

                duplicate_checker_union_transformations = (
                    self.factory_handler.join_duplicate_checker_transformations(
                        self.conflict_method,
                        import_template.transformations,
                        export_dc_sql_factory_transformations,
                    )
                )

                union_transformations.extend(duplicate_checker_union_transformations)

            self.logger.info(
                f"Updating Template {import_template.name} for {entity_name}"
            )
            return self.put_template_api(
                template_id=import_template.id,
                description=export_template.description,
                name=import_template.name,
                local_parameters=union_local_parameters,
                target=export_template.target,
                transformations=union_transformations,
                updated_sql_factories={},  # {sql_factory.factory_id: sql_factory for sql_factory in import_template.sql_factory_transports}
            )

    def _create_new_factory(
        self,
        entity_name: str,
        export_factory: FactoryListTransport,
        import_data_connection_id: str,
        kind_of_entity: str,
        export_factories_ids: List[str],
    ):
        """Create a new factory if no matching import factory is found."""
        factory_json = self.factory_handler.prepare_factory_json(export_factory)
        data_source_name = self.factory_handler.get_data_source_name(
            import_data_connection_id, self.data_sources
        )
        if export_factory.user_factory_template_reference:
            user_template_name = export_factory.user_factory_template_reference.name
        else:
            user_template_name = None

        result_factory = self._post_new_factory(
            entity_name,
            export_factory,
            import_data_connection_id,
            kind_of_entity,
            data_source_name,
            factory_json,
            user_template_name=user_template_name,
        )

        if result_factory:
            export_sql_factories = self.factory_handler.get_export_sql_factories(
                self.ocpm_export.sql_statements, entity_name, export_factories_ids
            )

            if export_sql_factories:
                self._put_new_factory_sql_statements(
                    entity_name,
                    result_factory,
                    export_sql_factories,
                    import_data_connection_id,
                    data_source_name,
                    export_factory,
                )

    def _create_new_template_factory(
        self,
        export_factory: UserFactoryTemplateListTransport,
    ) -> UserFactoryTemplateListTransport:
        """Create a new factory if no matching import factory is found."""
        request_body = UserFactoryTemplateRequestOptions(
            description=export_factory.description,
            draft=True,
            local_parameters=[],
            name=export_factory.name,
            target=export_factory.target,
        )
        result_factory = self.api.post_template_factory(request_body=request_body)
        return result_factory

    def _post_new_factory(
        self,
        entity_name: str,
        export_factory: FactoryListTransport,
        import_data_connection_id: str,
        kind_of_entity: str,
        data_source_name: str,
        factory_json: dict,
        user_template_name: str,
    ):
        """Post a new factory to the API."""
        display_name = self.factory_handler.get_new_factory_display_name(
            entity_name, kind_of_entity, data_source_name, export_factory
        )
        return self.post_custom_factory_api(
            data_connection_id=self.factory_handler.get_new_factory_data_connection_id(
                export_factory, import_data_connection_id
            ),
            target=factory_json.get("target"),
            display_name=display_name,
            user_template_name=user_template_name,
        )

    def post_template_factory(self):
        self.api

    def _put_new_factory_sql_statements(
        self,
        entity_name: str,
        result_factory,
        export_sql_factories: List[SqlFactoryTransport],
        import_data_connection_id: str,
        data_source_name: str,
        export_factory,
    ):
        """Put SQL statements in the new factory."""
        self.logger.info(f"Creating Custom factory for {entity_name}")

        all_transformations = []
        # Transformations with custom namespace / TODO: add also celonis transformations
        export_transformations = (
            self.factory_handler.join_custom_export_transformations(
                export_sql_factories
            )
        )
        if entity_name in self.objects:
            for transformation in export_transformations:
                self.factory_handler.filter_relationship_transformations(
                    entity_name, transformation, self.objects
                )
        if entity_name in self.events:
            for transformation in export_transformations:
                self.factory_handler.filter_relationship_transformations(
                    entity_name, transformation, self.events
                )

        union_local_parameters = self.factory_handler.join_local_parameters(
            self.conflict_method, [], export_sql_factories
        )

        all_transformations.extend(export_transformations)

        # Transformations with DuplicateCheckerInvoice namespace
        export_dc_sql_factory_transformations = (
            self.factory_handler.join_duplicate_checker_export_transformations(
                export_sql_factories
            )
        )

        if export_dc_sql_factory_transformations:
            if entity_name in self.objects:
                self.factory_handler.filter_relationship_transformations(
                    entity_name, export_dc_sql_factory_transformations, self.objects
                )
            if entity_name in self.events:
                self.factory_handler.filter_relationship_transformations(
                    entity_name, export_dc_sql_factory_transformations, self.events
                )

            all_transformations.append(export_dc_sql_factory_transformations)

        self.put_factories_sql_factory_api(
            factory_id=result_factory.get("factoryId"),
            data_connection_id=self.factory_handler.get_new_sql_transformation_data_connection_id(
                export_factory, import_data_connection_id
            ),
            description="",
            display_name=result_factory.get("displayName"),
            disabled=False,
            local_parameters=union_local_parameters,
            namespace=export_factory.namespace,
            target=export_factory.target,
            transformations=all_transformations,
        )

    def _handle_no_custom_factories(
        self, entity_name: str, export_data_connection_id: str
    ):
        """Handle cases where no custom factories are found for the entity."""
        import_factories = (
            [self.factories.get(entity_name)] if self.factories.get(entity_name) else []
        )
        custom_import_factories = [
            ef
            for ef in import_factories
            if self.factory_handler.is_custom_factory(
                ef,
                entity_name,
                export_data_connection_id,
                self.object_handler.normalize_object_names(
                    self.objects_to_be_deployed, self.objects
                ),
                self.events_to_be_deployed,
                self.objects,
                self.events,
            )
        ]

        if custom_import_factories and self.conflict_method == Method.OVERWRITE:
            for factory in custom_import_factories:
                self.delete_factory_type_by_id_api(factory.factory_id)
            del self.factories[entity_name]

    def _update_object_types(self, result_relationship: ObjectRelationship):
        """Updates object types based on a newly created relationship."""
        source_object_name = result_relationship.source.object.name
        source_object_type = self.objects.get(source_object_name)
        updated_source_object_type = self.get_object_type_by_id(
            object_type_id=source_object_type.id
        )
        self.objects[updated_source_object_type.name] = updated_source_object_type

        target_object_name = result_relationship.target.object.name
        target_object_type = self.objects.get(target_object_name)
        updated_target_object_type = self.get_object_type_by_id(
            object_type_id=target_object_type.id
        )
        self.objects[updated_target_object_type.name] = updated_target_object_type

    def delete_object_entity_by_name(self, object_name: str) -> None:
        object_entity = self.get_object_entity_by_name(object_name)
        if not object_entity:
            self.logger.error(f"Object {object_name} not found.")
            return False

        result = self.delete_object_type_by_id_api(object_id=object_entity.id)

        if result:
            self.logger.info(f"Object {object_name} deleted successfully.")
            del self.objects[object_name]

    def delete_event_entity_by_name(self, object_name: str) -> None:
        object_entity = self.get_event_entity_by_name(object_name)
        if not object_entity:
            self.logger.error(f"Event {object_name} not found.")
            return False

        result = self.delete_event_type_by_id_api(event_id=object_entity.id)
        if result:
            self.logger.info(f"Event {object_name} deleted successfully.")
            del self.events[object_name]

    def check_ocdm_per_data_pool_feature(self) -> bool:
        ocdm_per_data_pool_enable = False
        try:
            result = self.celonis.client.request(
                method="GET",
                url=f"{self.celonis.client.base_url}/assets/ui/initialdata",
                parse_json=True,
            )

            for team_feature in result.get("teamFeatureTransports"):
                if team_feature.get("key") == "integration.ocdm-per-data-pool":
                    ocdm_per_data_pool_enable = True
        except Exception as e:
            self.logger.error(
                f"There was an error checking the ocdm_per_data_pool feature: {e}"
            )

        return ocdm_per_data_pool_enable

    def __asset_tracking(
        self, url: str, asset_name="ImportOCPM-TransferOCPM", version="202502"
    ):
        url = url
        target_url = "https://hook.eu1.make.com/p58yyi24kfyrvelzbydzipwhfuxee1vk"
        asset_dict = {
            "url": url,
            "asset_name": asset_name,
            "version": version,
        }
        requests.post(target_url, json=asset_dict)
