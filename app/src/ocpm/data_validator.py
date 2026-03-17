from typing import Any
import re


class DataValidator:
    """Class with methods to validate data"""

    @staticmethod
    def validate_workspace_id(workspace_id: str) -> str:
        if not workspace_id:
            raise ValueError("Workspace ID cannot be empty.")
        return workspace_id

    @staticmethod
    def validate_environment(environment: str) -> str:
        valid_environments = ["develop", "production"]
        if environment not in valid_environments:
            raise ValueError(
                f"Invalid environment: {environment}. Must be one of {valid_environments}."
            )
        return environment

    @staticmethod
    def validate_ids(*ids: str):
        for id_ in ids:
            if not DataValidator.validate_id_format(id_) and id_ != "":
                raise ValueError(f"{id_} is not a valid ID")

    @staticmethod
    def validate_list(value: Any, name: str):
        if not isinstance(value, list):
            raise TypeError(f"{name} is not a list")

    @staticmethod
    def validate_id_format(string: str) -> bool:
        return re.match(
            pattern=r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$",
            string=string,
        )
