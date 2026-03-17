import os
import toml


def generate_backup_config(filename="backup_config.toml"):
    # Prepare the configuration data
    config_data = {
        "source": {
            "team_url": os.environ.get("SOURCE_TEAM_URL"),
            "api_token": os.environ.get("SOURCE_API_TOKEN"),
            "data_pool": os.environ.get("NAME_OF_SOURCE_DATA_POOL"),
            "environment_version": os.environ.get("ENVIRONMENT_VERSION"),
        }
    }

    # Write the configuration to a TOML file
    with open(filename, "w") as configfile:
        toml.dump(config_data, configfile)
    print(f"Config file '{filename}' has been created")


def generate_restore_config(filename="restore_config.toml"):
    # Prepare the configuration data
    config_data = {
        "backup": {"path": os.environ.get("BACKUP_PATH")},
        "target": {
            "team_url": os.environ.get("TARGET_TEAM_URL"),
            "api_token": os.environ.get("TARGET_API_TOKEN"),
            "data_pool": os.environ.get("NAME_OF_TARGET_DATA_POOL"),
        },
        "processing": {
            "conflict_method": os.environ.get("CONFLICT_METHOD"),
            "selected_objects": os.environ.get("SELECTED_OBJECTS"),
            "selected_events": os.environ.get("SELECTED_EVENTS"),
            "selected_perspectives": os.environ.get("SELECTED_PERSPECTIVES"),
            "copy_all_content": os.environ.get("COPY_ALL_CONTENT"),
        },
    }

    # Write the configuration to a TOML file
    with open(filename, "w") as configfile:
        toml.dump(config_data, configfile)
    print(f"Config file '{filename}' has been created")


def read_toml_config(filename="config.toml"):
    # Load the TOML file content
    print("reading config.toml file")
    with open(filename, "r") as config_file:
        config_data = toml.load(config_file)

    return config_data
