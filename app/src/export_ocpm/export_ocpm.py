from app.src.business_landscape_pycelonis.service import (
    BusinessLandscapePycelonis,
    Perspective,
    ObjectEntity,
    EventEntity,
    Process as bl_Process,
    FactoryListTransport,
    SqlFactoryTransport,
    Environment,
    UserFactoryTemplateListTransport,
    UserFactoryTemplateTransport,
)
from app.src.meta_types.metaTypes import Process, Factory, Object
from app.src.tools.logger_setup import setup_logger
from app.src.handlers import VersionHandler, ExcelExporter, JsonHandler, PickleHandler
from app.src.ocpm.business_graph_api import BusinessGraphAPI
from app.src.ocpm import Namespace, EnvironmentName, DataValidator


import os
import re
import sys
import datetime
import logging
import sys
import pycelonis
import pandas as pd
import requests
from typing import List, Dict, Union, Optional, DefaultDict
from colorama import Fore, Back, Style
from collections import defaultdict


class ExportOCPM:
    """
    Class for exporting and backing up Celonis OCPM content.
    """

    logger = logging.getLogger("ExportOCPM")

    def __init__(
        self,
        celonis: Optional[pycelonis.Celonis],
        workspace_id: str,
        environment: str,
        load_from_path: str = None,
        type_of_backup: str = None,
        logger_level: str = "INFO",
    ) -> None:
        """
        Initialize ExportOCPM instance.

        Args:
            celonis (Optional[pycelonis.Celonis]): An optional Celonis instance.
            environment (str): The environment, either "develop" or "production".
            load_from_path (str, optional): Path to load content from (used for backup). Defaults to None.
            type_of_backup (str, optional): Type of backup ("pkl" or "json"). Defaults to None.

        Returns:
            None
        """
        self.logger = setup_logger("ExportOCPM", "export_ocpm", logger_level)
        self.logger.info("Initializing ExportOCPM module")

        if not load_from_path:
            if not DataValidator().validate_id_format(workspace_id):
                raise ValueError("workspace_id not a valid ID")
            self.celonis: pycelonis.Celonis = celonis
            self.workspace_id: str = workspace_id
            self.environment: str = (
                environment
                if environment
                in [EnvironmentName.DEVELOPMENT, EnvironmentName.PRODUCTION]
                else EnvironmentName.PRODUCTION
            )
            self.api = BusinessGraphAPI(
                celonis.client, self.environment, self.workspace_id
            )
            self.__asset_tracking(url=celonis.client.base_url)
            self.tags: List[str] = []
            self.processes: Dict[str, Process] = {}
            self.factories: Dict[str, List[FactoryListTransport]] = {}
            self.objects: Dict[str, ObjectEntity] = {}
            self.events: Dict[str, EventEntity] = {}
            self.sql_statements: Dict[str, List[SqlFactoryTransport]] = {}
            self.objects_with_factories: Dict[str, Object] = {}
            self.perspectives: Dict[str, Perspective] = {}
            self.catalog_processes: List[bl_Process] = []
            self.environments: Dict[str, Environment] = {}
            self.template_factories: DefaultDict[
                List[UserFactoryTemplateListTransport]
            ] = defaultdict(list)
            self.templates: DefaultDict[
                List[UserFactoryTemplateTransport]
            ] = defaultdict(list)
            self.ocdm_per_data_pool_feature = self.check_ocdm_per_data_pool_feature()

        else:
            self.celonis: Optional[pycelonis.Celonis] = None
            self.bl: Optional[BusinessLandscapePycelonis] = None
            self.tags: List[str] = []
            self.recreate_objects(
                load_from_path=load_from_path, type_of_backup=type_of_backup
            )

    def export_content(self) -> None:
        self.get_bl_processes()
        self.get_environments()
        # Objects
        self.logger.info("Getting all Custom Object Entities")
        self.get_all_object_entities(namespace=Namespace.CUSTOM)
        self.logger.info("Getting all Object Entities")
        self.get_all_object_entities(namespace=Namespace.CELONIS)

        # Events
        self.logger.info("Getting all Celonis Event Entities")
        self.get_event_entities(namespace=Namespace.CELONIS)
        self.logger.info("Getting all Custom Event Entities")
        self.get_event_entities(namespace=Namespace.CUSTOM)

        # Factories
        self.logger.info("Getting all Factory Entities")
        self.get_factories_entities()

        # SQL Statements
        self.logger.info("Getting all SQL Statements")
        self.get_sql_statements_from_object_factories()
        self.get_sql_statements_from_event_factories()

        # Template Factories
        self.get_template_factories()

        # Templates
        self.logger.info("Getting Template SQL Statements")
        self.get_sql_statements_from_template_factories()

        # Perspectives
        self.logger.info("Get Perspectives")
        self.get_perspectives()
        self.logger.info("Create Processes instance")
        self.create_processes_instances()

    def backup_content_pkl(self) -> None:
        if not os.path.exists("backup_workspaces"):
            os.mkdir("backup_workspaces")

        root_folder = re.findall(
            "https:\/\/([-A-Za-z0-9]+.[-A-Za-z0-9]+).celonis.cloud",
            self.celonis.client.base_url,
        )[0]
        root_folder = f"backup_workspaces/{root_folder}"
        if not os.path.exists(root_folder):
            os.mkdir(root_folder)
        root_folder_v2 = f"{root_folder}/{self.workspace_id}"
        if not os.path.exists(root_folder_v2):
            os.mkdir(root_folder_v2)

        self.serialize_instances_to_pkl(
            instances=self.objects,
            root_path=root_folder_v2,
            folder_path="objects",
            file_prefix="object",
        )
        self.serialize_instances_to_pkl(
            instances=self.events,
            root_path=root_folder_v2,
            folder_path="events",
            file_prefix="event",
        )
        self.serialize_instances_to_pkl(
            instances=self.factories,
            root_path=root_folder_v2,
            folder_path="factories",
            file_prefix="factories",
        )
        self.serialize_instances_to_pkl(
            instances=self.sql_statements,
            root_path=root_folder_v2,
            folder_path="sql_statement",
            file_prefix="sql_statement",
        )
        self.serialize_instances_to_pkl(
            instances=self.template_factories,
            root_path=root_folder_v2,
            folder_path="template_factories",
            file_prefix="template_factories",
        )
        self.serialize_instances_to_pkl(
            instances=self.templates,
            root_path=root_folder_v2,
            folder_path="templates",
            file_prefix="templates",
        )
        self.serialize_instances_to_pkl(
            instances=self.perspectives,
            root_path=root_folder_v2,
            folder_path="perspectives",
            file_prefix="perspective",
        )
        self.serialize_instances_to_pkl(
            instances=self.processes,
            root_path=root_folder_v2,
            folder_path="processes",
            file_prefix="process",
        )

    def backup_content_json(self) -> None:
        if not os.path.exists("backup_workspaces"):
            os.mkdir("backup_workspaces")

        root_folder = re.findall(
            "https:\/\/([-A-Za-z0-9]+.[-A-Za-z0-9]+).celonis.cloud",
            self.celonis.client.base_url,
        )[0]
        root_folder = f"backup_workspaces/{root_folder}"
        if not os.path.exists(root_folder):
            os.mkdir(root_folder)
        root_folder_v2 = f"{root_folder}/{self.workspace_id}"
        if not os.path.exists(root_folder_v2):
            os.mkdir(root_folder_v2)

        self.serialize_instances_to_json(
            instances=self.objects,
            root_path=root_folder_v2,
            folder_path="objects",
            file_prefix="object",
        )
        self.serialize_instances_to_json(
            instances=self.events,
            root_path=root_folder_v2,
            folder_path="events",
            file_prefix="event",
        )
        self.serialize_instances_to_json(
            instances=self.factories,
            root_path=root_folder_v2,
            folder_path="factories",
            file_prefix="factories",
        )
        self.serialize_instances_to_json(
            instances=self.sql_statements,
            root_path=root_folder_v2,
            folder_path="sql_statements",
            file_prefix="sql_statement",
        )
        self.serialize_instances_to_json(
            instances=self.template_factories,
            root_path=root_folder_v2,
            folder_path="template_factories",
            file_prefix="template_factories",
        )
        self.serialize_instances_to_json(
            instances=self.templates,
            root_path=root_folder_v2,
            folder_path="templates",
            file_prefix="templates",
        )
        self.serialize_instances_to_json(
            instances=self.perspectives,
            root_path=root_folder_v2,
            folder_path="perspectives",
            file_prefix="perspective",
        )
        self.serialize_instances_to_json(
            instances=self.processes,
            root_path=root_folder_v2,
            folder_path="processes",
            file_prefix="process",
        )
        self.serialize_instances_to_json(
            instances=self.catalog_processes,
            root_path=root_folder_v2,
            folder_path="catalog_processes",
            file_prefix="catalog_processes",
        )

        self.serialize_instances_to_json(
            instances=self.environments,
            root_path=root_folder_v2,
            folder_path="environments",
            file_prefix="environments",
        )

    def backup_content_json_version(self) -> None:
        if not os.path.exists("graph_versioning"):
            os.mkdir("graph_versioning")

        root_folder = re.findall(
            "https:\/\/([-A-Za-z0-9]+.[-A-Za-z0-9]+).celonis.cloud",
            self.celonis.client.base_url,
        )[0]
        root_folder = f"graph_versioning/{root_folder}"
        if not os.path.exists(root_folder):
            os.mkdir(root_folder)
        root_folder_v2 = f"{root_folder}/{self.workspace_id}"
        if not os.path.exists(root_folder_v2):
            os.mkdir(root_folder_v2)

        temp_folder = "temp_backup"
        if not os.path.exists(temp_folder):
            os.mkdir(temp_folder)

        self.serialize_instances_to_json(
            instances=self.objects,
            root_path=temp_folder,
            folder_path="objects",
            file_prefix="object",
        )
        self.serialize_instances_to_json(
            instances=self.events,
            root_path=temp_folder,
            folder_path="events",
            file_prefix="event",
        )
        self.serialize_instances_to_json(
            instances=self.factories,
            root_path=temp_folder,
            folder_path="factories",
            file_prefix="factories",
        )
        self.serialize_instances_to_json(
            instances=self.sql_statements,
            root_path=temp_folder,
            folder_path="sql_statements",
            file_prefix="sql_statement",
        )
        self.serialize_instances_to_json(
            instances=self.template_factories,
            root_path=root_folder_v2,
            folder_path="template_factories",
            file_prefix="template_factories",
        )
        self.serialize_instances_to_json(
            instances=self.templates,
            root_path=root_folder_v2,
            folder_path="templates",
            file_prefix="templates",
        )
        self.serialize_instances_to_json(
            instances=self.perspectives,
            root_path=temp_folder,
            folder_path="perspectives",
            file_prefix="perspective",
        )
        self.serialize_instances_to_json(
            instances=self.processes,
            root_path=temp_folder,
            folder_path="processes",
            file_prefix="process",
        )
        self.serialize_instances_to_json(
            instances=self.catalog_processes,
            root_path=temp_folder,
            folder_path="catalog_processes",
            file_prefix="catalog_processes",
        )
        self.serialize_instances_to_json(
            instances=self.environments,
            root_path=temp_folder,
            folder_path="environments",
            file_prefix="environments",
        )

        # Check if there are changes from the last version
        version_handler = VersionHandler()
        version_folder = version_handler.generate_version_folder(
            root_folder=root_folder_v2, temp_folder=temp_folder
        )
        if version_folder:
            self.logger.info(f'Version backed up in folder "{version_folder}"')
        else:
            self.logger.info(f"No changes found from the latest stored version")

    def recreate_objects(
        self,
        load_from_path: str,
        type_of_backup: str = "json",
    ):
        if type_of_backup == "pkl":
            self.recreate_objects_from_pkl(load_from_path=load_from_path)
        if type_of_backup == "json":
            self.recreate_objects_from_json(load_from_path=load_from_path)

    def recreate_objects_from_json(self, load_from_path: str):
        json_handler = JsonHandler()
        self.catalog_processes: Dict[
            str, bl_Process
        ] = json_handler.recreate_object_dictionary_from_json(
            f"{load_from_path}/catalog_processes"
        )
        self.logger.info(
            f"Loaded data from {load_from_path}/catalog_processes successfully"
        )

        self.processes: Dict[
            str, Process
        ] = json_handler.recreate_object_dictionary_from_json(
            f"{load_from_path}/processes"
        )
        self.logger.info(f"Loaded data from {load_from_path}/processes successfully")

        self.factories: Dict[
            str, List[FactoryListTransport]
        ] = json_handler.recreate_object_dictionary_from_json(
            f"{load_from_path}/factories"
        )
        self.logger.info(f"Loaded data from {load_from_path}/factories successfully")

        self.objects: Dict[
            str, ObjectEntity
        ] = json_handler.recreate_object_dictionary_from_json(
            f"{load_from_path}/objects"
        )
        self.logger.info(f"Loaded data from {load_from_path}/objects successfully")

        self.events: Dict[
            str, EventEntity
        ] = json_handler.recreate_object_dictionary_from_json(
            f"{load_from_path}/events"
        )
        self.logger.info(f"Loaded data from {load_from_path}/events successfully")

        self.sql_statements: Dict[
            str, List[SqlFactoryTransport]
        ] = json_handler.recreate_object_dictionary_from_json(
            f"{load_from_path}/sql_statements"
        )
        self.logger.info(
            f"Loaded data from {load_from_path}/sql_statements successfully"
        )

        self.template_factories: DefaultDict[
            List[UserFactoryTemplateListTransport]
        ] = json_handler.recreate_object_dictionary_from_json(
            f"{load_from_path}/template_factories"
        )
        self.logger.info(
            f"Loaded data from {load_from_path}/template_factories successfully"
        )
        self.templates: DefaultDict[
            List[UserFactoryTemplateTransport]
        ] = json_handler.recreate_object_dictionary_from_json(
            f"{load_from_path}/templates"
        )
        self.logger.info(f"Loaded data from {load_from_path}/templates successfully")

        self.perspectives: Dict[
            str, Perspective
        ] = json_handler.recreate_object_dictionary_from_json(
            f"{load_from_path}/perspectives"
        )
        self.logger.info(f"Loaded data from {load_from_path}/perspectives successfully")

        self.environments: Dict[
            str, Environment
        ] = json_handler.recreate_object_dictionary_from_json(
            f"{load_from_path}/environments"
        )
        self.logger.info(f"Loaded data from {load_from_path}/environments successfully")

    def recreate_objects_from_pkl(self, load_from_path: str):
        pickle_handler = PickleHandler()
        self.processes: Dict[
            str, Process
        ] = pickle_handler.recreate_object_dictionary_from_pickle(
            f"{load_from_path}/processes"
        )
        self.logger.info(f"Loaded data from {load_from_path}/processes successfully")

        self.factories: Dict[
            str, List[FactoryListTransport]
        ] = pickle_handler.recreate_object_dictionary_from_pickle(
            f"{load_from_path}/factories"
        )
        self.logger.info(f"Loaded data from {load_from_path}/factories successfully")

        self.objects: Dict[
            str, ObjectEntity
        ] = pickle_handler.recreate_object_dictionary_from_pickle(
            f"{load_from_path}/objects"
        )
        self.logger.info(f"Loaded data from {load_from_path}/objects successfully")

        self.events: Dict[
            str, EventEntity
        ] = pickle_handler.recreate_object_dictionary_from_pickle(
            f"{load_from_path}/events"
        )
        self.logger.info(f"Loaded data from {load_from_path}/events successfully")

        self.sql_statements: Dict[
            str, List[SqlFactoryTransport]
        ] = pickle_handler.recreate_object_dictionary_from_pickle(
            f"{load_from_path}/sql_statement"
        )
        self.logger.info(
            f"Loaded data from {load_from_path}/sql_statement successfully"
        )

        self.template_factories: DefaultDict[
            List[UserFactoryTemplateListTransport]
        ] = pickle_handler.recreate_object_dictionary_from_pickle(
            f"{load_from_path}/template_factories"
        )
        self.logger.info(
            f"Loaded data from {load_from_path}/template_factories successfully"
        )
        self.templates: DefaultDict[
            List[UserFactoryTemplateTransport]
        ] = pickle_handler.recreate_object_dictionary_from_pickle(
            f"{load_from_path}/templates"
        )
        self.logger.info(f"Loaded data from {load_from_path}/templates successfully")

        self.perspectives: Dict[
            str, Perspective
        ] = pickle_handler.recreate_object_dictionary_from_pickle(
            f"{load_from_path}/perspectives"
        )
        self.logger.info(f"Loaded data from {load_from_path}/perspectives successfully")

    def serialize_instances_to_pkl(
        self,
        instances: List[
            Union[
                ObjectEntity,
                EventEntity,
                List[FactoryListTransport],
                List[SqlFactoryTransport],
                Process,
                Perspective,
            ]
        ],
        root_path: str,
        folder_path: str,
        file_prefix: str,
    ) -> None:
        pkl_handler = PickleHandler()
        self.logger.info(f"Backing up content in {folder_path}")
        pkl_handler.serialize_instances(instances, root_path, folder_path, file_prefix)
        self.logger.info(f"Finish backing up content in {folder_path}")

    def serialize_instances_to_json(
        self,
        instances: List[
            Union[
                ObjectEntity,
                EventEntity,
                List[FactoryListTransport],
                List[SqlFactoryTransport],
                Process,
                Perspective,
            ]
        ],
        root_path: str,
        folder_path: str,
        file_prefix: str,
    ):
        json_handler = JsonHandler()
        self.logger.info(f"Backing up content in {folder_path}")
        json_handler.serialize_instances_to_json(
            instances, root_path, folder_path, file_prefix
        )
        self.logger.info(f"Finish backing up content in {folder_path}")

    def export_to_excel(self, file_path: str):
        excel_exporter = ExcelExporter()
        with pd.ExcelWriter(file_path) as writer:
            if self.objects:
                objects_df = excel_exporter.convert_to_dataframe(
                    list(self.objects.values())
                )
                objects_df = objects_df.drop("categories", axis=1)
                objects_df = objects_df.drop("fields", axis=1)
                objects_df = objects_df.drop("relationships", axis=1)
                objects_df.to_excel(
                    writer, sheet_name="Objects", index=False
                )  # convert to function in ExcelExporter
                excel_exporter.handle_list_property(
                    list(self.objects.values()), "Objects", "categories", writer
                )
                excel_exporter.handle_list_property(
                    list(self.objects.values()), "Objects", "fields", writer
                )
                excel_exporter.handle_list_property(
                    list(self.objects.values()), "Objects", "relationships", writer
                )

            if self.factories:
                factories_df = excel_exporter.convert_to_dataframe(
                    list(self.factories.values())
                )
                factories_df.to_excel(writer, sheet_name="Factories", index=False)
            
            if self.template_factories:
                factories_df = excel_exporter.convert_to_dataframe(
                    list(self.template_factories.values())
                )
                factories_df.to_excel(writer, sheet_name="TemplateFactories", index=False)
            
            if self.templates:
                templates_df = excel_exporter.convert_to_dataframe(
                    list(self.templates.values())
                )
                templates_df = templates_df.drop("transformations", axis=1)
                templates_df.to_excel(
                    writer, sheet_name="Templates", index=False
                )
                excel_exporter.handle_list_property(
                    list(self.templates.values()),
                    "Templates",
                    "transformations",
                    writer,
                )

            if self.sql_statements:
                sql_statements_df = excel_exporter.convert_to_dataframe(
                    list(self.sql_statements.values())
                )
                sql_statements_df = sql_statements_df.drop("transformations", axis=1)
                sql_statements_df.to_excel(
                    writer, sheet_name="SQLStatements", index=False
                )
                excel_exporter.handle_list_property(
                    list(self.sql_statements.values()),
                    "SQLStatements",
                    "transformations",
                    writer,
                )

            if self.events:
                events_df = excel_exporter.convert_to_dataframe(
                    list(self.events.values())
                )
                events_df = events_df.drop("fields", axis=1)
                events_df = events_df.drop("relationships", axis=1)
                events_df.to_excel(writer, sheet_name="Events", index=False)
                excel_exporter.handle_list_property(
                    list(self.events.values()), "Events", "fields", writer
                )
                excel_exporter.handle_list_property(
                    list(self.events.values()), "Events", "relationships", writer
                )

            if self.perspectives:
                perspectives_df = excel_exporter.convert_to_dataframe(
                    list(self.perspectives.values())
                )
                perspectives_df = perspectives_df.drop("objects", axis=1)
                perspectives_df = perspectives_df.drop("projections", axis=1)
                perspectives_df.to_excel(writer, sheet_name="Perspectives", index=False)
                excel_exporter.handle_list_property(
                    list(self.perspectives.values()), "Perspectives", "objects", writer
                )
                excel_exporter.handle_list_property(
                    list(self.perspectives.values()),
                    "Perspectives",
                    "projections",
                    writer,
                )

            if self.catalog_processes:
                catalog_processes_df = excel_exporter.convert_to_dataframe(
                    list(self.catalog_processes.values())
                )
                catalog_processes_df.drop("data_source_connections", axis=1)
                catalog_processes_df.to_excel(writer, sheet_name="Catalog", index=False)
                excel_exporter.handle_list_property(
                    list(self.catalog_processes.values()),
                    "Catalog",
                    "data_source_connections",
                    writer,
                )

        self.logger.info(f"Data exported to {file_path}")

    def get_all_object_entities(self, namespace: Namespace):
        self.objects = self.api.get_object_entities(self.objects, namespace)

    def get_factories_entities(self) -> None:
        return self.api.get_all_factories_entities(self.factories)

    def get_event_entities(self, namespace: Namespace) -> None:
        self.events = self.api.get_event_entities(self.events, namespace)

    def get_perspectives(self) -> None:
        perspectives = self.api.get_perspectives()
        self.perspectives = {p.name: p for p in perspectives.content}

    def add_celonis_tags(self) -> None:
        tags_response = self.api.get_celonis_tags()
        self.tags.extend(tags_response)

    def get_bl_processes(self) -> None:
        catalog_processes = self.api.get_bl_processes()
        self.catalog_processes = {p.name: p for p in catalog_processes.content}

    def get_environment(self, name: str) -> Environment:
        environments = self.api.get_environments()
        for env in environments:
            if env.name == name:
                return env

    def get_environments(self) -> None:
        self.environments = {e.name: e for e in self.api.get_environments()}

    def get_template_factories(self) -> None:
        template_factories_response = self.api.get_template_factories()
        for t in template_factories_response.content or []:
            self.template_factories[t.target.entity_ref.name].append(t)

    def get_object_factory_by_entity_name(
        self, entity_name
    ) -> List[FactoryListTransport]:
        return self.factories.get(entity_name)

    def get_template_factory_by_entity_name(
        self, entity_name
    ) -> List[UserFactoryTemplateListTransport]:
        return self.template_factories.get(entity_name)

    def _get_sql_scripts_from_factory_base(
        self, url_path: str, factory_id: str
    ) -> SqlFactoryTransport:
        query = f"environment={self.environment}"
        sql_factory = self.celonis.client.request(
            method="GET",
            url=f"{url_path}/{factory_id}?{query}",
            parse_json=True,
            type_=SqlFactoryTransport,
        )
        return sql_factory

    def get_sql_scripts_from_factory(
        self, factory_id: str, data_connection_id: str
    ) -> SqlFactoryTransport:
        return self.api.get_sql_transform_from_factory(factory_id)

    def get_sql_scripts_from_template_factory(
        self, template_id: str
    ) -> UserFactoryTemplateTransport:
        return self.api.get_sql_transform_template_from_template_id(template_id)

    def get_sql_statements_from_object_factories(self) -> None:
        self.logger.info("Getting Object SQL Statement from Factories")
        for object_name in self.objects:
            self.logger.debug(f"Getting SQL Statements for {object_name}")
            factories_obj = self.get_object_factory_by_entity_name(
                entity_name=object_name
            )
            if factories_obj:
                for factory_obj in factories_obj:
                    if factory_obj:
                        factory_id, data_connection_id = (
                            factory_obj.factory_id,
                            factory_obj.data_connection_id,
                        )
                    else:
                        factory_id = data_connection_id = None
                    new_object = Object(
                        name=object_name,
                        factory=Factory(
                            factory_id=factory_id, data_connection_id=data_connection_id
                        ),
                    )
                    if factory_id:
                        sql_statements = self.get_sql_scripts_from_factory(
                            factory_id, data_connection_id
                        )
                        if object_name not in self.sql_statements:
                            self.sql_statements[object_name] = [sql_statements]
                        else:
                            self.sql_statements[object_name].append(sql_statements)

                    if object_name not in self.objects_with_factories:
                        self.objects_with_factories[object_name] = new_object

    def get_sql_statements_from_event_factories(self) -> None:
        self.logger.info("Getting Event SQL statements from Factories")
        for event_name in self.events:
            self.logger.debug(f"Getting SQL Statements for {event_name}")
            factories_obj = self.get_object_factory_by_entity_name(
                entity_name=event_name
            )
            if factories_obj:
                for factory_obj in factories_obj:
                    if factory_obj:
                        factory_id, data_connection_id = (
                            factory_obj.factory_id,
                            factory_obj.data_connection_id,
                        )
                    else:
                        factory_id = data_connection_id = None

                    if factory_id:
                        sql_statements = self.get_sql_scripts_from_factory(
                            factory_id, data_connection_id
                        )
                        if event_name not in self.sql_statements:
                            self.sql_statements[event_name] = [sql_statements]
                        else:
                            self.sql_statements[event_name].append(sql_statements)

    def get_sql_statements_from_template_factories(self) -> None:
        for object_name in self.objects:
            template_factories = self.get_template_factory_by_entity_name(
                entity_name=object_name
            )
            if template_factories:
                for template in template_factories:
                    template_id = template.id if template.id else None

                    if template_id:
                        sql_statements = self.get_sql_scripts_from_template_factory(
                            template_id=template_id
                        )
                        self.templates[object_name].append(sql_statements)

        for event_name in self.events:
            template_factories = self.get_template_factory_by_entity_name(
                entity_name=event_name
            )
            if template_factories:
                for template in template_factories:
                    template_id =  template.id if template else None

                    if template_id:
                        sql_statements = self.get_sql_scripts_from_template_factory(
                            template_id = template_id
                        )
                        self.templates[event_name].append(sql_statements)

    def get_object_with_factory(self, object_name: str) -> Object:
        return self.objects_with_factories.get(object_name)

    def create_processes_instances(self) -> None:
        self.logger.info("Creating Celonis Process Perspective objects")
        perspectives_objects_dict = dict()
        perspectives_events_dict = dict()
        for perspective_name, perspective in self.perspectives.items():
            object_perspective = [
                Object(
                    name=obj.name, factory=Factory(factory_id="", data_connection_id="")
                )
                for obj in perspective.objects
                if self.objects.get(obj.name)
            ]
            events_perspective = []
            for obj in perspective.objects:
                object_entity = self.objects.get(obj.name)
                if not object_entity:
                    self.logger.warning(
                        f"Object {obj.name} is not enabled, not adding in process {perspective.name}"
                    )
                    continue
                for relationship in obj.relationships or []:
                    if relationship.strategy == "EMBED":
                        object_relationships = object_entity.relationships or []
                        mapping_relationships = {
                            r.name: r.target.object_ref.name
                            for r in object_relationships
                            if r
                        }
                        object_ref = mapping_relationships.get(relationship.name)
                        object_perspective.append(
                            Object(
                                name=object_ref,
                                factory=Factory(factory_id="", data_connection_id=""),
                            )
                        )

                for event_name, event_entity in self.events.items():
                    for event_rel in event_entity.relationships:
                        try:
                            object_name = event_rel.target.object_ref.name
                        except Exception:
                            pass
                        if object_entity.name == object_name:
                            events_perspective.append(event_name)

            perspectives_objects_dict[perspective_name] = object_perspective

            for projection in perspective.projections:
                for event in projection.events:
                    if event not in events_perspective:
                        events_perspective.append(self.events.get(event.name))

            perspectives_events_dict[perspective_name] = events_perspective

        for perspective, object_perspective in perspectives_objects_dict.items():
            clean_object_perspective = []
            for obj in object_perspective:
                if obj not in clean_object_perspective:
                    clean_object_perspective.append(obj)

            self.processes[perspective] = Process(
                name=perspective,
                objects=clean_object_perspective,
                events=perspectives_events_dict.get(perspective, []),
            )
            self.logger.info(
                f"Process with name {perspective} was created successfully"
            )

    def check_ocdm_per_data_pool_feature(self):
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

    def __asset_tracking(self, url: str, asset_name="ExportOCPM", version="202408"):
        url = url
        target_url = "https://hook.eu1.make.com/p58yyi24kfyrvelzbydzipwhfuxee1vk"
        asset_dict = {
            "url": url,
            "asset_name": asset_name,
            "version": version,
        }
        requests.post(target_url, json=asset_dict)
