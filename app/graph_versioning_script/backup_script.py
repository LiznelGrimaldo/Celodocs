import sys
from pycelonis import get_celonis
from app.src.import_ocpm.import_ocpm import ImportOCPM
from app.src.export_ocpm.export_ocpm import ExportOCPM
import os
from colorama import Fore, Style
from app.transfer_script import config
import argparse
from app.src.tools.log_formatter import reset_logger

reset_logger("ImportOCPM")
reset_logger("ExportOCPM")

# parser = argparse.ArgumentParser()
# parser.add_argument('--skip', action='store_true', help='skip validation questions')
# args = parser.parse_args()


# Function to print colored text
def color_print(text, color=Fore.WHITE, style=Style.NORMAL):
    print(style + color + text + Style.RESET_ALL)


# Get environment variables
config_ = config.read_toml_config(filename="backup_config.toml")

SOURCE_TEAM_URL = config_["source"]["team_url"]
SOURCE_API_TOKEN = config_["source"]["api_token"]
NAME_OF_SOURCE_DATA_POOL = config_["source"]["data_pool"]
ENVIRONMENT_VERSION = (
    config_["source"]["environment_version"]
    if config_["source"]["environment_version"] in ("develop", "production")
    else "develop"
)

# Print formatted output
color_print("Source Team Configuration", Fore.BLUE, Style.BRIGHT)
color_print("-" * 20, Fore.BLUE)

print(f"{Style.BRIGHT}Source Team URL:{Style.RESET_ALL} {SOURCE_TEAM_URL}")
print(f"{Style.BRIGHT}Source API Token:{Style.RESET_ALL} {SOURCE_API_TOKEN}")
print()

print(f"{Style.BRIGHT}Source Data Pool:{Style.RESET_ALL} {NAME_OF_SOURCE_DATA_POOL}")
print()

source_data_pool = None
source_workspace = None

celonis = get_celonis(base_url=SOURCE_TEAM_URL, api_token=SOURCE_API_TOKEN)
color_print(f"Connected to {celonis.client.base_url}", Fore.GREEN, Style.BRIGHT)

try:
    source_data_pool = celonis.data_integration.get_data_pools().find(
        NAME_OF_SOURCE_DATA_POOL
    )
except Exception as e:
    print(f'ERROR: Fail to get source_data_pool with name "{NAME_OF_SOURCE_DATA_POOL}"')
    print("Error message:", e)

if source_data_pool:
    SOURCE_WORKSPACE_ID = source_data_pool.id

    source_workspace = ExportOCPM(
        celonis=celonis,
        workspace_id=SOURCE_WORKSPACE_ID,
        environment=ENVIRONMENT_VERSION,
    )
    source_workspace.export_content()

    source_workspace.backup_content_json_version()
else:
    raise ValueError(
        "Please check the values for NAME_OF_SOURCE_DATA_POOL and/or NAME_OF_SOURCE_DATA_CONNECTION"
    )
