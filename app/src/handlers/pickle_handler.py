from app.src.business_landscape_pycelonis.service import (
    BusinessLandscapePycelonis,
    Perspective,
    ObjectEntity,
    EventEntity,
    Process as bl_Process,
    FactoryListTransport,
    SqlFactoryTransport,
)
from app.src.meta_types.metaTypes import Process

from typing import Union, Dict, List
import sys
import os
import pickle
import re

BusinessLandscapeDatatypes = Union[
    Process,
    FactoryListTransport,
    ObjectEntity,
    EventEntity,
    SqlFactoryTransport,
    Perspective,
]


class PickleHandler:
    """Class to handle the backup into Pickle format for an ExportOCPM class"""

    def get_custom_instances_paths(
        self, folder_path: str, type_of_backup: str
    ) -> List[str]:
        if not os.path.exists(folder_path):
            print(f"The folder '{folder_path}' does not exist.")
        else:
            pkl_files = [
                file
                for file in os.listdir(folder_path)
                if file.endswith(f".{type_of_backup}")
            ]
            return pkl_files

    def load_pickle_file(
        self, folder_path: str, pkl_path: str
    ) -> Union[
        Process,
        FactoryListTransport,
        ObjectEntity,
        EventEntity,
        SqlFactoryTransport,
        Perspective,
    ]:
        sys.path.append(folder_path)
        file_path = os.path.join(folder_path, pkl_path)

        with open(file_path, "rb") as file:
            try:
                loaded_object = pickle.load(file)
                return loaded_object

            except Exception as e:
                print(f"Failed to load data from {file_path}: {e}")

    def recreate_object_dictionary_from_pickle(
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
        pkl_files = self.get_custom_instances_paths(folder_path, type_of_backup="pkl")
        object_dict = {
            pkl_name.split("_")[-1].replace(".pkl", ""): self.load_pickle_file(
                folder_path, pkl_name
            )
            for pkl_name in pkl_files
        }
        return object_dict

    def serialize_instances(
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
            if not instance:
                pass
            else:
                file_name = f"{folder_name}/{file_prefix}_{instance_name}.pkl"
                with open(file_name, "wb") as file:
                    pickle.dump(instance, file)
