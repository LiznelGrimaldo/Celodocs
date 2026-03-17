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
from app.src.meta_types.metaTypes import Process, Factory, Object, Event
from typing import Union, Dict, List

import sys
import os
import json

BusinessLandscapeDatatypes = Union[
    Process,
    FactoryListTransport,
    ObjectEntity,
    EventEntity,
    SqlFactoryTransport,
    Perspective,
]


class Namespace:
    CUSTOM = ["custom"]
    CELONIS = ["celonis", "DuplicateInvoiceChecker"]


class JsonHandler:
    """Class to handle the backup into JSON format for an ExportOCPM class"""

    def load_json_file(
        self, folder_path: str, json_path: str
    ) -> Union[
        Process,
        FactoryListTransport,
        ObjectEntity,
        EventEntity,
        SqlFactoryTransport,
        Perspective,
    ]:
        sys.path.append(folder_path)
        file_path = os.path.join(folder_path, json_path)

        with open(file_path, "r") as file:
            try:
                loaded_object = json.load(file)
                if "catalog_processes" in json_path:
                    loaded_instance = bl_Process(**loaded_object)
                if "object_" in json_path:
                    loaded_instance = ObjectEntity(**loaded_object)
                if "event_" in json_path:
                    loaded_instance = EventEntity(**loaded_object)
                if "factories_" in json_path:
                    if isinstance(loaded_object, list):
                        loaded_instance = [
                            FactoryListTransport(**loaded) for loaded in loaded_object
                        ]
                    else:
                        loaded_instance = FactoryListTransport(**loaded_object)
                if "perspective_" in json_path:
                    loaded_instance = Perspective(**loaded_object)
                if "template_factories_" in json_path:
                    if isinstance(loaded_object, list):
                        loaded_instance = [
                            UserFactoryTemplateListTransport(**loaded)
                            for loaded in loaded_object
                        ]
                    else:
                        loaded_instance = UserFactoryTemplateListTransport(
                            **loaded_object
                        )
                if "templates_" in json_path:
                    if isinstance(loaded_object, list):
                        loaded_instance = [
                            UserFactoryTemplateTransport(**loaded)
                            for loaded in loaded_object
                        ]
                    else:
                        loaded_instance = UserFactoryTemplateTransport(**loaded_object)
                if "environments_" in json_path:
                    loaded_instance = Environment(**loaded_object)
                if "process_" in json_path:
                    loaded_instance = Process(**loaded_object)
                if "sql_statement" in json_path:
                    if isinstance(loaded_object, list):
                        loaded_instance = [
                            SqlFactoryTransport(**loaded) for loaded in loaded_object
                        ]
                    else:
                        loaded_instance = SqlFactoryTransport(**loaded_object)
                return loaded_instance

            except Exception as e:
                print(f"Failed to load data from {file_path}: {e}")

    def get_custom_instances_paths(
        self, folder_path: str, type_of_backup: str
    ) -> List[str]:
        if not os.path.exists(folder_path):
            print(f"The folder '{folder_path}' does not exist.")
            return []
        else:
            pkl_files = [
                file
                for file in os.listdir(folder_path)
                if file.endswith(f".{type_of_backup}")
            ]
            return pkl_files

    def recreate_object_dictionary_from_json(
        self, folder_path: str
    ) -> Dict[
        str,
        Union[
            Process,
            FactoryListTransport,
            ObjectEntity,
            EventEntity,
            SqlFactoryTransport,
            Perspective,
        ],
    ]:
        object_dict = {}
        json_files = self.get_custom_instances_paths(folder_path, type_of_backup="json")
        object_dict = {
            json_name.split("_")[-1].replace(".json", ""): self.load_json_file(
                folder_path, json_name
            )
            for json_name in json_files
        }
        return object_dict

    def serialize_instances_to_json(
        self,
        instances: Dict[str, BusinessLandscapeDatatypes],
        root_path: str,
        folder_path: str,
        file_prefix: str,
    ) -> None:
        folder_name = f"{root_path}/{folder_path}"
        if not os.path.exists(folder_name):
            os.mkdir(folder_name)

        for instance_name, instance in instances.items():
            file_name = f"{folder_name}/{file_prefix}_{instance_name}.json"
            with open(file_name, "w") as file:
                if isinstance(instance, list):
                    instance_list = [json.loads(i.json()) for i in instance]
                    json.dump(instance_list, file)
                else:
                    try:
                        json.dump(json.loads(instance.json()), file)
                        file.close()
                    except Exception as e:
                        if isinstance(instance, Process):
                            process_dict = {
                                "name": instance.name,
                                "columns": [],
                                "objects": [
                                    object_instance.name
                                    if isinstance(object_instance, Object)
                                    or isinstance(object_instance, ObjectEntity)
                                    else object_instance
                                    for object_instance in instance.objects
                                ],
                                "events": [
                                    event_instance.name
                                    if isinstance(event_instance, Event)
                                    or isinstance(event_instance, EventEntity)
                                    else event_instance
                                    for event_instance in instance.events
                                ],
                            }
                            json.dump(process_dict, file)

                        file.close()
