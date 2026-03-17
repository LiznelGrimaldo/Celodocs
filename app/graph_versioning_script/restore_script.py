import sys
from pycelonis import get_celonis
from app.src.import_ocpm.import_ocpm import ImportOCPM
from app.src.export_ocpm.export_ocpm import ExportOCPM
import os
from colorama import Fore, Style
from app.transfer_script import config
import argparse
import json
from pathlib import Path
from app.src.tools.log_formatter import reset_logger

reset_logger("ImportOCPM")
reset_logger("ExportOCPM")


def get_data_connection_ids_from_file(file_path):
    data_connection_ids = set()
    with open(file_path, "r") as file:
        try:
            data = json.load(file)
            for item in data:
                if "data_connection_id" in item:
                    data_connection_ids.add(item["data_connection_id"])
        except json.JSONDecodeError:
            print(f"Error decoding JSON in file: {file_path}")
    return data_connection_ids


def get_all_data_connection_ids(path):
    factories_folder = Path(path) / "factories"
    if not factories_folder.exists():
        print("No data_connection_ids found in the given path.")
        return []

    all_data_connection_ids = set()
    all_data_connection_ids.add("")
    for root, dirs, files in os.walk(factories_folder):
        for file in files:
            file_path = os.path.join(root, file)
            data_connection_ids = get_data_connection_ids_from_file(file_path)
            all_data_connection_ids.update(data_connection_ids)

    return list(all_data_connection_ids)


# Function to print colored text
def color_print(text, color=Fore.WHITE, style=Style.NORMAL):
    print(style + color + text + Style.RESET_ALL)


# Get environment variables
config_ = config.read_toml_config(filename="restore_config.toml")

BACKUP_PATH = config_["backup"]["path"]
TARGET_TEAM_URL = config_["target"]["team_url"]
TARGET_API_TOKEN = config_["target"]["api_token"]
NAME_OF_TARGET_DATA_POOL = config_["target"]["data_pool"]

SELECTED_OBJECTS = config_.get("processing", {}).get("selected_objects", "").split(", ")
SELECTED_EVENTS = config_.get("processing", {}).get("selected_events", "").split(", ")
SELECTED_PERSPECTIVES = (
    config_.get("processing", {}).get("selected_perspectives", "").split(", ")
)
COPY_ALL_CONTENT = (
    True
    if config_.get("processing", {}).get("copy_all_content", "") == "True"
    else False
)

color_print("Target Team Configuration", Fore.YELLOW, Style.BRIGHT)
color_print("-" * 25, Fore.YELLOW)
print(f"{Style.BRIGHT}Target Team URL:{Style.RESET_ALL} {TARGET_TEAM_URL}")
print(f"{Style.BRIGHT}Target API Token:{Style.RESET_ALL} {TARGET_API_TOKEN}")
print()

print(f"{Style.BRIGHT}Target Data Pool:{Style.RESET_ALL} {NAME_OF_TARGET_DATA_POOL}")

source_data_pool = None
source_workspace = None

celonis = get_celonis(base_url=TARGET_TEAM_URL, api_token=TARGET_API_TOKEN)
color_print(f"Connected to {celonis.client.base_url}", Fore.GREEN, Style.BRIGHT)

try:
    source_data_pool = celonis.data_integration.get_data_pools().find(
        NAME_OF_TARGET_DATA_POOL
    )
except Exception as e:
    print(f'ERROR: Fail to get source_data_pool with name "{NAME_OF_TARGET_DATA_POOL}"')
    print("Error message:", e)


source_workspace = ExportOCPM(
    celonis=celonis,
    load_from_path=BACKUP_PATH,
    workspace_id=None,
    environment=None,
    type_of_backup="json",
)

unique_data_connection_ids = get_all_data_connection_ids(BACKUP_PATH)
print(unique_data_connection_ids)

target_data_pool = None
try:
    target_data_pool = celonis.data_integration.get_data_pools().find(
        NAME_OF_TARGET_DATA_POOL
    )
    TARGET_WORKSPACE_ID = target_data_pool.id
except Exception as e:
    print(f'ERROR: Fail to get target_data_pool with name "{NAME_OF_TARGET_DATA_POOL}"')
    print("Error message:", e)


if target_data_pool:
    target_workspace = ImportOCPM(
        celonis=celonis,
        environment="develop",
        ocpm_export=source_workspace,
        workspace_id=TARGET_WORKSPACE_ID,
        conflict_method="overwrite",
        copy_all_content=True,
    )

    for process, process_config in source_workspace.catalog_processes.items():
        if process_config.enabled:
            for data_connection_process in process_config.data_source_connections:
                if data_connection_process.enabled:
                    target_workspace.enable_needed_processes(
                        processes_to_deploy=[process_config.name],
                        data_connection_id=data_connection_process.data_source_id,
                        transformation_type=data_connection_process.transformation_type,
                    )

    if COPY_ALL_CONTENT:
        SELECTED_PERSPECTIVES.extend(
            [
                perspective_name
                for perspective_name in source_workspace.perspectives
                if perspective_name
            ]
        )
    target_workspace.define_object_names_to_be_deployed_from_perspectives(
        selected_perspective=SELECTED_PERSPECTIVES
    )

    if COPY_ALL_CONTENT:
        SELECTED_OBJECTS.extend([obj.name for obj in source_workspace.objects.values()])
    target_workspace.define_object_names_to_be_deployed(object_names=SELECTED_OBJECTS)

    if COPY_ALL_CONTENT:
        SELECTED_EVENTS.extend(
            [event.name for event in source_workspace.events.values()]
        )
    target_workspace.define_event_names_to_be_deployed(event_names=SELECTED_EVENTS)

    target_workspace.import_entities(SELECTED_PERSPECTIVES)
    target_workspace.get_content_from_source_team()

    for data_connection_id in unique_data_connection_ids:
        target_workspace.import_transformations(data_connection_id, data_connection_id)

    target_workspace.delete_overwrite_objects()
