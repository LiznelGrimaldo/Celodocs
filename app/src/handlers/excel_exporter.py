from typing import Dict, Any, List, Union
import json
import pandas as pd
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

BusinessLandscapeDatatypes = Union[
    Process,
    FactoryListTransport,
    ObjectEntity,
    EventEntity,
    SqlFactoryTransport,
    Perspective,
]


class ExcelExporter:
    """Class to handle the excel backup method"""

    def generate_excel_writer(file_path: str) -> pd.ExcelWriter:
        return pd.ExcelWriter(file_path)

    def flatten_dict(
        self, d: Dict[str, Any], parent_key: str = "", sep: str = "."
    ) -> Dict[str, Any]:
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self.flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                items.append((new_key, v))
            else:
                items.append((new_key, v))
        return dict(items)

    def dataclass_to_dict(self, instance: BusinessLandscapeDatatypes):
        if isinstance(instance, list):
            return [json.loads(item.json()) for item in instance]
        return json.loads(instance.json())

    def convert_to_dataframe(
        self, instances: List[BusinessLandscapeDatatypes]
    ) -> pd.DataFrame:
        flat_data = []
        for instance in instances:
            instance_dict = self.dataclass_to_dict(instance)
            if isinstance(instance_dict, list):
                for item in instance_dict:
                    flat_instance = self.flatten_dict(item)
                    flat_data.append(flat_instance)
            else:
                flat_instance = self.flatten_dict(instance_dict)
                flat_data.append(flat_instance)
        return pd.DataFrame(flat_data)

    def handle_list_property(
        self,
        instances: List[
            Union[BusinessLandscapeDatatypes, List[BusinessLandscapeDatatypes]]
        ],
        parent_type: str,
        property_name: str,
        writer: pd.ExcelWriter,
    ) -> None:
        data = []
        for instance in instances:
            if isinstance(instance, list):
                for instance_ in instance:
                    instance_dict = json.loads(instance_.json())
                    parent_id = instance_dict.get(
                        "id", instance_dict.get("factory_id", "unknown")
                    )
                    parent_name = instance_dict.get(
                        "name", instance_dict.get("display_name", "unknown")
                    )
                    if property_name in instance_dict:
                        for item in instance_dict[property_name]:
                            item_flat = dict()
                            item_flat["id"] = parent_id
                            item_flat["parent_name"] = parent_name
                            item_flat.update(self.flatten_dict(item))
                            data.append(item_flat)
            else:
                instance_dict = json.loads(instance.json())
                parent_id = instance_dict.get(
                    "id", instance_dict.get("factory_id", "unknown")
                )
                parent_name = instance_dict.get(
                    "name", instance_dict.get("display_name", "unknown")
                )
                if property_name in instance_dict:
                    for item in instance_dict[property_name]:
                        item_flat = dict()
                        item_flat["id"] = parent_id
                        item_flat["parent_name"] = parent_name
                        item_flat.update(self.flatten_dict(item))
                        data.append(item_flat)

        if data:
            df = pd.DataFrame(data)
            df.to_excel(
                writer,
                sheet_name=f"{parent_type}.{property_name.capitalize()}",
                index=False,
            )

    def export_sheet_to_excel(
        writer: pd.ExcelWriter, df: pd.DataFrame, sheet_name, index: bool = False
    ) -> None:
        df.to_excel(writer, sheet_name=sheet_name, index=index)
