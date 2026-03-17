import re
import sqlglot
from typing import List, Optional, Set
from app.src.business_landscape_pycelonis.service import (
    SqlFactoryTransport,
    SqlFactoryDataset,
    SqlFactoryTransformationTransport,
)


class CustomSQLFactoryScriptJoiner:
    """
    This class combines SQL scripts from two SqlFactoryTransport objects (target and source).
    It extracts relevant property names, and finally produces a consolidated query that includes:
        - Two Common Table Expressions (CTEs): one for the target scripts, one for the source scripts.
        - A FULL OUTER JOIN between those CTEs on the "ID" column.
        - A block comment containing the original SQL scripts from the source factory.
    """

    def __init__(
        self,
        target_sql_factory: SqlFactoryTransformationTransport,
        source_sql_factory: SqlFactoryTransformationTransport,
    ):
        """
        Initialize with two SqlFactoryTransport instances.

        Args:
            target_sql_factory (SqlFactoryTransport): The 'target' SQL transformations.
            source_sql_factory (SqlFactoryTransport): The 'source' SQL transformations.
        """
        self.target_sql_factory = target_sql_factory
        self.source_sql_factory = source_sql_factory

    def _extract_sql_scripts(
        self, sql_factory: SqlFactoryTransformationTransport, namespace: str = "custom"
    ) -> List[str]:
        """
        Extract SQL scripts from all transformations of a given namespace.

        Args:
            sql_factory (SqlFactoryTransport): The SQL factory to extract from.
            namespace (str, optional): The namespace to filter on. Defaults to 'custom'.

        Returns:
            List[str]: List of SQL query strings.
        """
        return [
            dataset.sql
            for dataset in (sql_factory.property_sql_factory_datasets or [])
            if sql_factory.namespace == namespace
        ]

    def _extract_property_sql_factory_datasets(
        self, sql_factory: SqlFactoryTransformationTransport, namespace: str = "custom"
    ) -> List[SqlFactoryDataset]:
        """
        Extract SqlFactoryDataset objects from all transformations of a given namespace.

        Args:
            sql_factory (SqlFactoryTransport): The SQL factory to extract from.
            namespace (str, optional): The namespace to filter on. Defaults to 'custom'.

        Returns:
            List[SqlFactoryDataset]: List of dataset objects.
        """
        return [
            dataset
            for dataset in (sql_factory.property_sql_factory_datasets or [])
            if sql_factory.namespace == namespace
        ]

    def _extract_property_names(
        self, sql_factory: SqlFactoryTransformationTransport, namespace: str = "custom"
    ) -> List[str]:
        """
        Extract property names from transformations, excluding 'ID'.

        Args:
            sql_factory (SqlFactoryTransport): The SQL factory to extract from.
            namespace (str, optional): The namespace to filter on. Defaults to 'custom'.

        Returns:
            List[str]: Property names found in the transformations.
        """
        return [
            p
            for p in (sql_factory.property_names or [])
            if sql_factory.namespace == namespace and p.lower() != "id"
        ]

    def _extract_foreign_key_names(
        self, sql_factory: SqlFactoryTransformationTransport
    ) -> List[str]:
        """
        Extract all foreign key names from the transformations.

        Args:
            sql_factory (SqlFactoryTransport): The SQL factory to extract from.

        Returns:
            List[str]: Foreign key names across all transformations.
        """
        return [fk for fk in (sql_factory.foreign_keys or [])]

    def remove_parameters_from_sql(self, sql: str) -> str:
        """
        Remove or replace template placeholders from a SQL script (e.g., <%...%>, <$...>).

        Args:
            sql (str): The original SQL string with placeholders.

        Returns:
            str: The cleaned SQL string.
        """
        # Convert ((...)); => (...)
        sql = re.sub(r"^\(\((.*)\)\);$", r"(\1);", sql, flags=re.DOTALL)

        # Replace Celonis-like placeholders
        sql = re.sub(r"<%\s*=\s*DATASOURCE\s*:\s*(.*?)\s*%>", r'"DATASOURCE_\1"', sql)
        sql = re.sub(r"<%\s*=\s*(\w+)\s*%>", " '' ", sql)
        sql = re.sub(r"<%\s*=(\w+)\s*%>", " '' ", sql)
        sql = re.sub(r"<\$\s*(\w+)\s*>", r" \1 ", sql, flags=re.IGNORECASE)

        return sql + "\n"  # Ensure a trailing newline

    def extract_mapped_properties_from_scripts(
        self, sql_scripts: List[str]
    ) -> Set[str]:
        """
        Parse each SQL script with sqlglot and collect aliased column names.

        Args:
            sql_scripts (List[str]): SQL scripts to parse.

        Returns:
            Set[str]: Unique set of aliases found in the scripts.
        """
        aliases_found = set()

        for original_sql in sql_scripts:
            cleaned_sql = self.remove_parameters_from_sql(original_sql)
            try:
                parsed = sqlglot.parse_one(cleaned_sql)
                # If parse succeeds, gather all aliases
                if parsed:
                    for alias in parsed.find_all(sqlglot.exp.Alias):
                        aliases_found.add(alias.alias)
            except Exception as e:
                print(f"[WARNING] Error parsing SQL script: {e}")

        return aliases_found

    def extract_property_names(
        self, sql_factory: SqlFactoryTransformationTransport
    ) -> Set[str]:
        """
        Extract property names from the transformations and intersect with aliases found in the scripts.

        Args:
            sql_factory (SqlFactoryTransport): The SQL factory to process.

        Returns:
            Set[str]: The intersection of declared property names and aliased columns in scripts.
        """
        scripts = self._extract_sql_scripts(sql_factory)
        declared = self._extract_property_names(sql_factory)
        found_in_scripts = self.extract_mapped_properties_from_scripts(scripts)
        return set(declared).intersection(found_in_scripts)

    def union_all_scripts(
        self, sql_scripts: List[str], cte_name: str = "CTE_Union"
    ) -> str:
        """
        Combine multiple SQL statements into a single CTE via UNION ALL.

        Args:
            sql_scripts (List[str]): List of SQL statements to union.
            cte_name (str, optional): Name of the CTE. Defaults to "CTE_Union".

        Returns:
            str: The CTE definition with all statements UNION ALL'ed.
        """
        if not sql_scripts:
            # Return a dummy CTE if no scripts exist
            return f"{cte_name} AS (SELECT NULL)"
        return f"{cte_name} AS (\n" + "\nUNION ALL\n".join(sql_scripts) + "\n)"

    def create_scripts_in_comments(
        self, factory_datasets: List[SqlFactoryDataset]
    ) -> str:
        """
        Wrap original scripts in a block comment for reference.

        Args:
            factory_datasets (List[SqlFactoryDataset]): Dataset objects containing original SQL.

        Returns:
            str: A block comment with each script prefixed by '-- Original <id>'.
        """
        lines = []
        for ds in factory_datasets:
            lines.append(f"-- Original {ds.id}")
            lines.append(ds.sql)
        joined = "\n".join(lines)
        return f"/**\n{joined}\n**/"

    def join_property_names(self, properties: List[str], table_name: str) -> List[str]:
        """
        Build SELECT-expressions for each property from the specified table/CTE.

        Args:
            properties (List[str]): Properties (column aliases) to select.
            table_name (str): The CTE or table alias.

        Returns:
            List[str]: SQL fragments like `"CTE"."Prop" AS "Prop"`.
        """
        return [f'"{table_name}"."{prop}" as "{prop}"' for prop in properties]

    def join_foreign_key_names(
        self, foreign_keys: List[str], table_names: List[str]
    ) -> List[str]:
        """
        Build COALESCE expressions for foreign keys from multiple tables.

        Args:
            foreign_keys (List[str]): A list of FK column names.
            table_names (List[str]): Tables or CTEs to search for these columns.

        Returns:
            List[str]: A list of COALESCE(...) expressions, each aliased by the foreign key name.
        """
        coalesced_fks = []
        for fk in foreign_keys:
            inner = ", ".join(f'"{table}"."{fk}"' for table in table_names)
            coalesced_fks.append(f'COALESCE({inner}) as "{fk}"')
        return coalesced_fks

    def generate_script(self, cte_name_target: str, cte_name_source: str) -> str:
        """
        Produce the final SQL script that includes:
            1) Two CTEs (for target and source scripts).
            2) A FULL OUTER JOIN on "ID".
            3) Original source scripts commented out at the top.

        Args:
            cte_name_target (str): Name for the target CTE.
            cte_name_source (str): Name for the source CTE.

        Returns:
            str: The complete SQL script.
        """
        # Gather scripts
        target_sql = self._extract_sql_scripts(self.target_sql_factory)
        source_sql = self._extract_sql_scripts(self.source_sql_factory)

        # Gather property names
        target_props = self.extract_property_names(self.target_sql_factory)
        source_props = self.extract_property_names(self.source_sql_factory)

        # Create CTE definitions
        target_cte = self.union_all_scripts(target_sql, cte_name=cte_name_target)
        source_cte = self.union_all_scripts(source_sql, cte_name=cte_name_source)

        # Put original source scripts in comments
        source_datasets = self._extract_property_sql_factory_datasets(
            self.source_sql_factory
        )
        commented_sql = self.create_scripts_in_comments(source_datasets)

        # Build SELECT expressions
        select_expressions = []
        select_expressions.extend(
            self.join_property_names(list(target_props), cte_name_target)
        )
        select_expressions.extend(
            self.join_property_names(list(source_props), cte_name_source)
        )

        if select_expressions:
            select_expressions_sql = ",\n\t".join(select_expressions)
        else:
            # If no mapped properties at all, at least return "ID"
            select_expressions_sql = '"ID"'

        final_sql = f"""WITH 
{target_cte},
{source_cte}
SELECT 
    COALESCE({cte_name_target}.ID, {cte_name_source}.ID) as "ID",
    {select_expressions_sql}
FROM {cte_name_target}
FULL OUTER JOIN {cte_name_source}
    ON {cte_name_target}.ID = {cte_name_source}.ID
"""

        return f"{commented_sql}\n\n{final_sql}"
