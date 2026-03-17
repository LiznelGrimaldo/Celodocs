from typing import Any, Callable, Dict, List, Optional, Union
import logging
from app.src.business_landscape_pycelonis.service import (
    BusinessLandscapePycelonis,
    ObjectEntity,
    EventEntity,
    SqlFactoryTransport,
    Perspective,
    FactoryListTransport,
    PageObjectEntity,
    PageEventEntity,
    SqlFactoryRequestOptions,
    ObjectEntityRequestOptions,
    EventEntityRequestOptions,
    PerspectiveRequestOptions,
    ObjectRelationshipRequestOptions,
    DataSourceConnectionRequestOptions,
    ProcessUpdateOptions,
    PageFactoryListTransport,
    PagePerspective,
    FactoryTarget,
    FactoryDataSourceTransport,
    Process,
    PageProcess,
    DataSourceConnection,
    Environment,
    EnvironmentRequestOptions,
    PageUserFactoryTemplateListTransport,
    UserFactoryTemplateTransport,
    UserFactoryTemplateRequestOptions,
)
from app.src.tools.log_formatter import format_exception_for_logging
from pycelonis_core.client.client import Client
from app.src.tools.colored_formatter import ColoredFormatter
from colorama import Fore, Back, Style
import os
import datetime
import sys


class BusinessGraphAPI:
    """Class to handle the BusinessLandscapePycelonis API requests"""

    OCPM_SCHEMA_ID = "00000000-0000-0000-0000-000000000000"

    def __init__(
        self,
        celonis_client: Client,
        environment: str,
        workspace_id: Optional[str] = None,
    ):
        self.bl = BusinessLandscapePycelonis
        self.client = celonis_client
        self.environment = environment
        self.workspace_id = workspace_id
        self.logger = self.configure_logger("INFO")
        self.ocdm_per_data_pool_feature = self.check_ocdm_per_data_pool_feature()

    def perform_api_call(self, api_method: Callable, *args, **kwargs) -> Any:
        """Generic method to perform an API call and handle exceptions."""
        try:
            return api_method(*args, **kwargs)
        except Exception as e:
            self._log_and_raise_error(f"API call failed for {api_method.__name__}", e)

    def _log_and_raise_error(self, message: str, exception: Exception) -> None:
        self.logger.error(message)
        formatted_message = format_exception_for_logging(exception)
        self.logger.error(formatted_message)

    def check_ocdm_per_data_pool_feature(self) -> bool:
        ocdm_per_data_pool_enable = False
        try:
            result = self.client.request(
                method="GET",
                url=f"{self.client.base_url}/assets/ui/initialdata",
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

    def initialize_categories(
        self, object: Union[EventEntity, ObjectEntity]
    ) -> Union[EventEntity, ObjectEntity]:
        if isinstance(object, ObjectEntity) or isinstance(object, EventEntity):
            if not isinstance(object.categories, list):
                object.categories = []
        return object

    def get_entities(
        self, entities: Dict, url_path: str, entity_type: Any, namespace: Any
    ) -> Dict[str, Any]:
        """Generic method to get entities from API."""
        page_num = 0
        not_last = True
        while not_last:
            query = f"?page={page_num}&environment={self.environment}"
            result = self.perform_api_call(
                self.client.request,
                url=f"{url_path}{query}",
                method="GET",
                parse_json=True,
                type_=entity_type,
            )
            if not result:
                raise Exception(f"Failed to fetch entities from {url_path}")
            page_num += 1
            not_last = not result.last
            entities.update(
                {
                    entity.name: self.initialize_categories(entity)
                    for entity in result.content
                    if entity.namespace in namespace
                }
            )
        return entities

    def get_factories_entities_api(
        self, entities: Dict, data_connection_id: str, url_path: str, target_kind: str
    ) -> None:
        not_last = True
        page_num = 0
        while not_last:
            query = f"requestMode=ALL&includeUserTemplateTransformations=true&environment={self.environment}&page={page_num}"
            result = self.client.request(
                url=f"{url_path}?{query}",
                method="GET",
                parse_json=True,
                type_=PageFactoryListTransport,
            )
            page_num += 1
            not_last = result.last == False
            factories: List[FactoryListTransport] = result.content
            factories: List[FactoryListTransport] = result.content
            entities.update(
                {
                    factory.target.entity_ref.name: factory
                    for factory in factories
                    if (
                        factory.data_connection_id == data_connection_id
                        or factory.data_connection_id == self.OCPM_SCHEMA_ID
                    )
                    and factory.target.kind == target_kind
                }
            )
            return entities

    def get_all_factories_entities_api(self, entities: Dict, url_path: str) -> None:
        not_last = True
        page_num = 0
        while not_last:
            query = f"requestMode=ALL&includeUserTemplateTransformations=true&environment={self.environment}&page={page_num}"
            result = self.client.request(
                url=f"{url_path}?{query}",
                method="GET",
                parse_json=True,
                type_=PageFactoryListTransport,
            )
            page_num += 1
            not_last = result.last == False
            factories: List[FactoryListTransport] = result.content
            for factory in factories:
                if factory.target.entity_ref.name in entities:
                    entities[factory.target.entity_ref.name].append(factory)
                else:
                    entities[factory.target.entity_ref.name] = [factory]

    def get_sql_entity_from_factory_id(
        self, url_path: str, factory_id: str
    ) -> SqlFactoryTransport:
        query = f"environment={self.environment}"
        sql_factory = self.client.request(
            method="GET",
            url=f"{url_path}/{factory_id}?{query}",
            parse_json=True,
            type_=SqlFactoryTransport,
        )
        return sql_factory

    def get_object_entities(
        self, entities: Dict[str, ObjectEntity], namespace: Any
    ) -> Dict[str, ObjectEntity]:
        url_path = (
            f"/bl/api/v2/workspaces/{self.workspace_id}/types/objects"
            if self.ocdm_per_data_pool_feature
            else "/bl/api/v1/types/objects"
        )
        return self.get_entities(entities, url_path, PageObjectEntity, namespace)

    def get_event_entities(
        self, entities: Dict[str, EventEntity], namespace: Any
    ) -> Dict[str, EventEntity]:
        url_path = (
            f"/bl/api/v2/workspaces/{self.workspace_id}/types/events"
            if self.ocdm_per_data_pool_feature
            else "/bl/api/v1/types/events"
        )
        return self.get_entities(entities, url_path, PageEventEntity, namespace)

    def get_factories_entities(
        self,
        entities: Dict[str, FactoryListTransport],
        data_connection_id: str,
        target_kind: str,
    ) -> Dict[str, FactoryListTransport]:
        url_path = (
            f"/bl/api/v2/workspaces/{self.workspace_id}/factories/sql"
            if self.ocdm_per_data_pool_feature
            else "/bl/api/v1/factories"
        )
        return self.get_factories_entities_api(
            entities, data_connection_id, url_path, target_kind
        )

    def get_all_factories_entities(
        self, entities: Dict[str, FactoryListTransport]
    ) -> Dict[str, FactoryListTransport]:
        url_path = (
            f"/bl/api/v2/workspaces/{self.workspace_id}/factories/sql"
            if self.ocdm_per_data_pool_feature
            else "/bl/api/v1/factories"
        )
        return self.get_all_factories_entities_api(entities, url_path)

    def get_sql_transform_from_factory(self, factory_id: str) -> SqlFactoryTransport:
        url_path = (
            f"/bl/api/v2/workspaces/{self.workspace_id}/factories/sql"
            if self.ocdm_per_data_pool_feature
            else "/bl/api/v1/factories/sql"
        )
        return self.get_sql_entity_from_factory_id(url_path, factory_id)

    def get_sql_transform_template_from_template_id(
        self, template_id: str
    ) -> UserFactoryTemplateTransport:
        return self.perform_api_call(
            self.bl.get_api_v2_workspaces_workspace_id_factories_sql_templates_template_id,
            workspace_id=self.workspace_id,
            template_id=template_id,
            client=self.client,
            environment=self.environment,
        )

    def get_perspectives(self) -> PagePerspective:
        if self.ocdm_per_data_pool_feature:
            return self.perform_api_call(
                self.bl.get_api_v2_workspaces_workspace_id_perspectives,
                workspace_id=self.workspace_id,
                client=self.client,
                environment=self.environment,
            )
        else:
            return self.perform_api_call(
                self.bl.get_api_v1_perspectives,
                client=self.client,
                environment=self.environment,
            )

    def get_template_factories(self) -> PageUserFactoryTemplateListTransport:
        return self.perform_api_call(
            self.bl.get_api_v2_workspaces_workspace_id_factories_sql_templates,
            workspace_id=self.workspace_id,
            client=self.client,
            environment=self.environment,
            )

    def get_factories_data_sources(self) -> List[Optional[FactoryDataSourceTransport]]:
        if self.ocdm_per_data_pool_feature:
            return self.perform_api_call(
                self.bl.get_api_v2_workspaces_workspace_id_execution_factories_data_sources,
                client=self.client,
                workspace_id=self.workspace_id,
                environment=self.environment,
            )
        else:
            return self.perform_api_call(
                self.bl.get_api_v1_execution_factories_data_sources,
                client=self.client,
                environment=self.environment,
            )

    def get_bl_processes(self) -> PageProcess:
        if self.ocdm_per_data_pool_feature:
            return self.perform_api_call(
                self.bl.get_api_v2_workspaces_workspace_id_processes,
                client=self.client,
                workspace_id=self.workspace_id,
                environment=self.environment,
            )
        else:
            return self.perform_api_call(
                self.bl.get_api_v1_processes,
                client=self.client,
                environment=self.environment,
            )

    def get_celonis_tags(self):
        if self.ocdm_per_data_pool_feature:
            return self.perform_api_call(
                self.bl.get_api_v1_tags,
                client=self.client,
                environment=self.environment,
            )
        else:
            return self.perform_api_call(
                self.bl.get_api_v1_tags,
                client=self.client,
                environment=self.environment,
            )

    def get_environments(self) -> List[Environment]:
        if self.ocdm_per_data_pool_feature:
            return self.perform_api_call(
                self.bl.get_api_v2_workspaces_workspace_id_environments,
                client=self.client,
                workspace_id=self.workspace_id,
            )
        else:
            return self.perform_api_call(
                self.bl.get_api_v1_environments,
                client=self.client,
            )

    def put_environment(self, environment_id, request_body: EnvironmentRequestOptions):
        if self.ocdm_per_data_pool_feature:
            return self.perform_api_call(
                self.bl.put_api_v2_workspaces_workspace_id_environments_environment_id,
                client=self.client,
                workspace_id=self.workspace_id,
                environment_id=environment_id,
                request_body=request_body,
            )
        else:
            return self.perform_api_call(
                self.bl.put_api_v1_environments_environment_id,
                client=self.client,
                environment_id=environment_id,
                request_body=request_body,
            )

    def post_object_type(
        self, request_body: ObjectEntityRequestOptions
    ) -> ObjectEntity:
        if self.ocdm_per_data_pool_feature:
            return self.perform_api_call(
                self.bl.post_api_v2_workspaces_workspace_id_types_objects,
                client=self.client,
                workspace_id=self.workspace_id,
                request_body=request_body,
                environment=self.environment,
            )
        else:
            return self.perform_api_call(
                self.bl.post_api_v1_types_objects,
                client=self.client,
                request_body=request_body,
                environment=self.environment,
            )

    def put_object_type(
        self, object_type_id: str, request_body: ObjectEntityRequestOptions
    ) -> ObjectEntity:
        if self.ocdm_per_data_pool_feature:
            return self.perform_api_call(
                self.bl.put_api_v2_workspaces_workspace_id_types_objects_object_type_id,
                client=self.client,
                workspace_id=self.workspace_id,
                object_type_id=object_type_id,
                request_body=request_body,
                environment=self.environment,
            )
        else:
            return self.perform_api_call(
                self.bl.put_api_v1_types_objects_object_type_id,
                client=self.client,
                object_type_id=object_type_id,
                request_body=request_body,
                environment=self.environment,
            )

    def put_factories_sql_factory(
        self, factory_id: str, request_body: SqlFactoryRequestOptions
    ) -> SqlFactoryTransport:
        if self.ocdm_per_data_pool_feature:
            response = self.perform_api_call(
                self.bl.put_api_v2_workspaces_workspace_id_factories_sql_factory_id,
                client=self.client,
                workspace_id=self.workspace_id,
                factory_id=factory_id,
                request_body=request_body,
                environment=self.environment,
            )
            if not response:
                self.logger.warning(
                    "Validation failed; attempting to save without validation"
                )
                request_body.save_mode = "SKIP_VALIDATION"
                response = self.perform_api_call(
                    self.bl.put_api_v2_workspaces_workspace_id_factories_sql_factory_id,
                    client=self.client,
                    workspace_id=self.workspace_id,
                    factory_id=factory_id,
                    request_body=request_body,
                    environment=self.environment,
                )
                if response:
                    target = request_body.target
                    object_name = str(target.entity_ref.name) if target else ""
                    self.logger.info(
                        f"Transformation for {object_name} was updated correctly by skipping the SQL validation"
                    )

                return response
        else:
            response = self.perform_api_call(
                self.bl.put_api_v1_factories_sql_factory_id,
                client=self.client,
                factory_id=factory_id,
                request_body=request_body,
                environment=self.environment,
            )
            if not response:
                self.logger.warning(
                    "Validation failed; attempting to save without validation"
                )
                request_body.save_mode = "SKIP_VALIDATION"
                self.perform_api_call(
                    self.bl.put_api_v1_factories_sql_factory_id,
                    client=self.client,
                    factory_id=factory_id,
                    request_body=request_body,
                    environment=self.environment,
                )

    def put_template(
        self, template_id: str, request_body: UserFactoryTemplateRequestOptions
    ) -> UserFactoryTemplateTransport:
        if self.ocdm_per_data_pool_feature:
            return self.perform_api_call(
                self.bl.put_api_v2_workspaces_workspace_id_factories_sql_templates_template_id,
                workspace_id=self.workspace_id,
                client=self.client,
                request_body=request_body,
                template_id=template_id,
                use_v2_manifest=True,
                environment=self.environment,
            )

    def create_factory_request_body(
        self,
        data_connection_id: str,
        target: FactoryTarget,
        display_name: str,
        user_template_name: str,
    ) -> dict:
        """Creates the request body for a factory API call."""
        return {
            "factoryId": "",
            "namespace": "custom",
            "dataConnectionId": data_connection_id,
            "target": target,
            "draft": True,
            "localParameters": [],
            "changedBy": {},
            "createdBy": {},
            "displayName": display_name,
            "userTemplateName": user_template_name,
        }

    def post_custom_factory(self, request_body: dict) -> Dict[str, Any]:
        url = (
            f"/bl/api/v2/workspaces/{self.workspace_id}/factories/sql?environment={self.environment}"
            if self.ocdm_per_data_pool_feature
            else f"/bl/api/v1/factories/sql?environment={self.environment}"
        )
        return self.perform_api_call(
            self.client.request,
            method="POST",
            url=url,
            request_body=request_body,
            parse_json=True,
        )

    def post_template_factory(self, request_body: UserFactoryTemplateRequestOptions):
        return self.perform_api_call(
            self.bl.post_api_v2_workspaces_workspace_id_factories_sql_templates,
            client=self.client,
            workspace_id=self.workspace_id,
            request_body=request_body,
            environment=self.environment,
            use_v2_manifest=True,
        )

    def post_perspective(self, request_body: PerspectiveRequestOptions) -> Perspective:
        if self.ocdm_per_data_pool_feature:
            return self.perform_api_call(
                self.bl.post_api_v2_workspaces_workspace_id_perspectives,
                client=self.client,
                workspace_id=self.workspace_id,
                request_body=request_body,
                environment=self.environment,
            )
        else:
            return self.perform_api_call(
                self.bl.post_api_v1_perspectives,
                client=self.client,
                request_body=request_body,
                environment=self.environment,
            )

    def put_perspective(
        self, perspective_id: str, request_body: PerspectiveRequestOptions
    ) -> Perspective:
        if self.ocdm_per_data_pool_feature:
            return self.perform_api_call(
                self.bl.put_api_v2_workspaces_workspace_id_perspectives_perspective_id,
                client=self.client,
                workspace_id=self.workspace_id,
                perspective_id=perspective_id,
                request_body=request_body,
                environment=self.environment,
            )
        else:
            return self.perform_api_call(
                self.bl.put_api_v1_perspectives_perspective_id,
                client=self.client,
                perspective_id=perspective_id,
                request_body=request_body,
                environment=self.environment,
            )

    def post_event_type(self, request_body: EventEntityRequestOptions) -> EventEntity:
        if self.ocdm_per_data_pool_feature:
            return self.perform_api_call(
                self.bl.post_api_v2_workspaces_workspace_id_types_events,
                client=self.client,
                workspace_id=self.workspace_id,
                request_body=request_body,
                environment=self.environment,
            )
        else:
            return self.perform_api_call(
                self.bl.post_api_v1_types_events,
                client=self.client,
                request_body=request_body,
                environment=self.environment,
            )

    def put_event_type(
        self, event_type_id: str, request_body: EventEntityRequestOptions
    ) -> EventEntity:
        if self.ocdm_per_data_pool_feature:
            return self.perform_api_call(
                self.bl.put_api_v2_workspaces_workspace_id_types_events_event_type_id,
                client=self.client,
                workspace_id=self.workspace_id,
                event_type_id=event_type_id,
                request_body=request_body,
                environment=self.environment,
            )
        else:
            return self.perform_api_call(
                self.bl.put_api_v1_types_events_event_type_id,
                client=self.client,
                event_type_id=event_type_id,
                request_body=request_body,
                environment=self.environment,
            )

    def post_object_relationship(
        self, request_body: ObjectRelationshipRequestOptions
    ) -> Any:
        if self.ocdm_per_data_pool_feature:
            return self.perform_api_call(
                self.bl.post_api_v2_workspaces_workspace_id_types_objects_relationships,
                client=self.client,
                workspace_id=self.workspace_id,
                request_body=request_body,
                environment=self.environment,
            )
        else:
            return self.perform_api_call(
                self.bl.post_api_v1_types_objects_relationships,
                client=self.client,
                request_body=request_body,
                environment=self.environment,
            )

    def delete_object_type(self, object_type_id: str) -> None:
        if self.ocdm_per_data_pool_feature:
            return self.perform_api_call(
                self.bl.delete_api_v2_workspaces_workspace_id_types_objects_object_type_id,
                client=self.client,
                workspace_id=self.workspace_id,
                object_type_id=object_type_id,
                environment=self.environment,
                force=True
            )
        else:
            return self.perform_api_call(
                self.bl.delete_api_v1_types_objects_object_type_id,
                client=self.client,
                object_type_id=object_type_id,
                environment=self.environment,
                force=True
            )

    def delete_event_type(self, event_type_id: str) -> None:
        if self.ocdm_per_data_pool_feature:
            return self.perform_api_call(
                self.bl.delete_api_v2_workspaces_workspace_id_types_events_event_type_id,
                client=self.client,
                workspace_id=self.workspace_id,
                event_type_id=event_type_id,
                environment=self.environment,
                force=True
            )
        else:
            return self.perform_api_call(
                self.bl.delete_api_v1_types_events_event_type_id,
                client=self.client,
                event_type_id=event_type_id,
                environment=self.environment,
                force=True
            )

    def delete_factory(self, factory_id: str) -> None:
        if self.ocdm_per_data_pool_feature:
            self.perform_api_call(
                self.bl.delete_api_v2_workspaces_workspace_id_factories_sql_factory_id,
                client=self.client,
                workspace_id=self.workspace_id,
                factory_id=factory_id,
                environment=self.environment,
            )
        else:
            self.perform_api_call(
                self.bl.delete_api_v1_factories_sql_factory_id,
                client=self.client,
                factory_id=factory_id,
                environment=self.environment,
            )

    def delete_perspective(self, perspective_id: str) -> None:
        if self.ocdm_per_data_pool_feature:
            self.perform_api_call(
                self.bl.delete_api_v2_workspaces_workspace_id_perspectives_perspective_id,
                client=self.client,
                workspace_id=self.workspace_id,
                perspective_id=perspective_id,
                environment=self.environment,
            )
        else:
            self.perform_api_call(
                self.bl.delete_api_v1_perspectives_perspective_id,
                client=self.client,
                perspective_id=perspective_id,
                environment=self.environment,
            )

    def enable_process(self, process_name: str) -> Process:
        if self.ocdm_per_data_pool_feature:
            result = self.perform_api_call(
                self.bl.post_api_v2_workspaces_workspace_id_processes_process_name_enable,
                client=self.client,
                workspace_id=self.workspace_id,
                process_name=process_name,
                environment=self.environment,
            )
        else:
            result = self.perform_api_call(
                self.bl.post_api_v1_processes_process_name_enable,
                client=self.client,
                process_name=process_name,
                environment=self.environment,
            )
        return result

    def deploy_catalog_process_transformations_api(
        self,
        process_name: str,
        request_body: ProcessUpdateOptions,
    ) -> None:
        return self.perform_api_call(
            self.bl.put_api_v2_workspaces_workspace_id_processes_process_name,
            client=self.client,
            workspace_id=self.workspace_id,
            process_name=process_name,
            request_body=request_body,
        )

    def configure_logger(self, level: str = "INFO") -> logging.Logger:
        """Configures the logger for the ImportOCPM class."""
        logger = logging.getLogger("BusinessGraphAPI")
        formatter = ColoredFormatter(
            "{asctime} |{color} {levelname:8} {reset}| {name} | {message}",
            style="{",
            datefmt="%Y-%m-%d %H:%M:%S",
            colors={
                "DEBUG": Fore.CYAN,
                "INFO": Fore.GREEN,
                "WARNING": Fore.YELLOW,
                "ERROR": Fore.RED,
                "CRITICAL": Fore.RED + Back.WHITE + Style.BRIGHT,
            },
        )

        log_folder = "logs/import_ocpm"
        if not os.path.exists(log_folder.split("/")[0]):
            os.makedirs(log_folder.split("/")[0])
        if not os.path.exists(log_folder):
            os.makedirs(log_folder)

        log_file_name = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".log"
        log_file_path = os.path.join(log_folder, log_file_name)

        if level == "INFO":
            logger.setLevel(logging.INFO)
        else:
            logger.setLevel(logging.DEBUG)

        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        return logger
