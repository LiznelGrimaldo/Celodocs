import os
import re
import filecmp
import difflib
import shutil
from datetime import datetime


class VersionHandler:
    """Class to handle the versioning backup methods"""

    def generate_version_folder(self, root_folder: str, temp_folder: str):
        last_version_folder = self.get_last_version_folder(root_folder)
        if self.has_changes(root_folder, temp_folder):
            version_folder = self.get_next_version_folder(root_folder)
            os.mkdir(version_folder)
            self.generate_diff_file(last_version_folder, temp_folder, version_folder)
            self.move_contents(temp_folder, version_folder)
            self.generate_version_file(version_folder)
            return version_folder
        else:
            shutil.rmtree(temp_folder)

    def get_last_version_folder(self, root_folder_v2):
        existing_versions = [
            d
            for d in os.listdir(root_folder_v2)
            if os.path.isdir(os.path.join(root_folder_v2, d))
            and re.match(r"v\d+\.\d+\.\d+", d)
        ]

        if not existing_versions:
            return None

        existing_versions.sort(key=lambda s: list(map(int, s[1:].split("."))))
        last_version = existing_versions[-1]

        return os.path.join(root_folder_v2, last_version)

    def get_next_version_folder(self, root_folder):
        existing_versions = [
            d
            for d in os.listdir(root_folder)
            if os.path.isdir(os.path.join(root_folder, d))
            and re.match(r"v\d+\.\d+\.\d+", d)
        ]

        if not existing_versions:
            return os.path.join(root_folder, "v1.0.0")

        existing_versions.sort(key=lambda s: list(map(int, s[1:].split("."))))
        last_version = existing_versions[-1]
        major, minor, patch = map(int, last_version[1:].split("."))
        next_version = f"v{major}.{minor}.{patch + 1}"

        return os.path.join(root_folder, next_version)

    def has_changes(self, root_folder_v2, temp_folder):
        existing_versions = [
            d
            for d in os.listdir(root_folder_v2)
            if os.path.isdir(os.path.join(root_folder_v2, d))
            and re.match(r"v\d+\.\d+\.\d+", d)
        ]

        if not existing_versions:
            return True  # No previous versions, so changes are implied

        existing_versions.sort(key=lambda s: list(map(int, s[1:].split("."))))
        last_version_folder = os.path.join(root_folder_v2, existing_versions[-1])

        # Use filecmp.dircmp to compare directories
        comparison = filecmp.dircmp(last_version_folder, temp_folder)
        return not self.is_identical(comparison)

    def is_identical(self, dircmp):
        if (
            dircmp.left_only
            or dircmp.right_only
            or dircmp.diff_files
            or dircmp.funny_files
        ):
            return False

        for sub_dircmp in dircmp.subdirs.values():
            if not self.is_identical(sub_dircmp):
                return False

        return True

    def generate_version_file(self, current_path):
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        path = os.path.join(current_path, "version_date.txt")
        with open(path, "w") as file:
            file.write(current_date)

    def generate_diff_file(self, last_version_folder, temp_folder, new_version_folder):
        diff_file_path = os.path.join(new_version_folder, "diff.txt")
        with open(diff_file_path, "w") as diff_file:
            # Walk through the new temporary folder
            for root, _, files in os.walk(temp_folder):
                for file in files:
                    temp_file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(temp_file_path, temp_folder)
                    last_version_file_path = (
                        os.path.join(last_version_folder, relative_path)
                        if last_version_folder
                        else None
                    )

                    if last_version_file_path and os.path.exists(
                        last_version_file_path
                    ):
                        # If the file exists in the last version, compare contents
                        with open(last_version_file_path, "r") as last_file, open(
                            temp_file_path, "r"
                        ) as temp_file:
                            last_file_lines = last_file.readlines()
                            temp_file_lines = temp_file.readlines()
                            diff = difflib.unified_diff(
                                last_file_lines,
                                temp_file_lines,
                                fromfile=f"last/{relative_path}",
                                tofile=f"new/{relative_path}",
                                lineterm="",
                            )
                            diff_file.writelines(diff)
                    else:
                        # If the file is new or this is the first version, compare with an empty list
                        with open(temp_file_path, "r") as temp_file:
                            temp_file_lines = temp_file.readlines()
                            diff = difflib.unified_diff(
                                [""],
                                temp_file_lines,
                                fromfile=f"last/{relative_path}"
                                if last_version_file_path
                                else f"last/none",
                                tofile=f"new/{relative_path}",
                                lineterm="",
                            )
                            diff_file.writelines(diff)

            # Handle files that exist only in the last version folder
            if last_version_folder:
                for root, _, files in os.walk(last_version_folder):
                    for file in files:
                        last_version_file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(
                            last_version_file_path, last_version_folder
                        )
                        temp_file_path = os.path.join(temp_folder, relative_path)

                        if not os.path.exists(temp_file_path):
                            # If the file was deleted, compare with an empty list
                            with open(last_version_file_path, "r") as last_file:
                                last_file_lines = last_file.readlines()
                                diff = difflib.unified_diff(
                                    last_file_lines,
                                    [""],
                                    fromfile=f"last/{relative_path}",
                                    tofile=f"new/{relative_path}",
                                    lineterm="",
                                )
                                diff_file.writelines(diff)

    def move_contents(self, src_folder, dest_folder):
        for item in os.listdir(src_folder):
            s = os.path.join(src_folder, item)
            d = os.path.join(dest_folder, item)
            shutil.move(s, d)
        os.rmdir(src_folder)
