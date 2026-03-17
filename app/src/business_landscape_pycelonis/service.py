import logging
import uuid
from datetime import datetime
from io import BytesIO
from typing import Any, Dict, List, Literal, Optional, Union

from pycelonis_core.base.base_model import PyCelonisBaseEnum, PyCelonisBaseModel
from pycelonis_core.client.client import Client
from pycelonis_core.utils.ml_workbench import TRACKING_LOGGER

try:
    from pydantic.v1 import Field, StrictBool, StrictInt, StrictStr  # type: ignore
except ImportError:
    from pydantic import Field, StrictBool, StrictInt, StrictStr  # type: ignore


logger = logging.getLogger(TRACKING_LOGGER)


class Cause(PyCelonisBaseEnum):
    EMPTY_SQL = "EMPTY_SQL"
    PARSE_ERROR = "PARSE_ERROR"
    VALIDATE_ERROR = "VALIDATE_ERROR"
    MISSING_REQUIRED_ATTRIBUTE = "MISSING_REQUIRED_ATTRIBUTE"
    INVALID_TABLE_REFERENCE = "INVALID_TABLE_REFERENCE"
    TYPE_MISMATCH = "TYPE_MISMATCH"
    SOURCE_TABLE_TYPE_MISMATCH = "SOURCE_TABLE_TYPE_MISMATCH"
    ENTITY_TABLE_NOT_FOUND = "ENTITY_TABLE_NOT_FOUND"
    UNEXPECTED = "UNEXPECTED"


class ColumnType(PyCelonisBaseEnum):
    ATTRIBUTE = "ATTRIBUTE"
    PRIMARY_KEY = "PRIMARY_KEY"
    FOREIGN_KEY = "FOREIGN_KEY"


class DataLoadType(PyCelonisBaseEnum):
    FROM_CACHE = "FROM_CACHE"
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"


class DataModelLoadStatus(PyCelonisBaseEnum):
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    WARNING = "WARNING"
    LOST_CONNECTION = "LOST_CONNECTION"
    CANCELED = "CANCELED"
    CANCELLING = "CANCELLING"


class DataSetTarget(PyCelonisBaseEnum):
    BASE = "BASE"
    RELATIONSHIP = "RELATIONSHIP"
    CHANGE = "CHANGE"
    TABLE = "TABLE"


class DataType(PyCelonisBaseEnum):
    CT_BOOLEAN = "CT_BOOLEAN"
    CT_DOUBLE = "CT_DOUBLE"
    CT_INSTANT = "CT_INSTANT"
    CT_LONG = "CT_LONG"
    CT_UTF8_STRING = "CT_UTF8_STRING"


class EntityCategory(PyCelonisBaseEnum):
    OBJECT = "OBJECT"
    EVENT = "EVENT"
    CHANGE = "CHANGE"
    RELATIONSHIP = "RELATIONSHIP"


class EntityRelationshipCardinality(PyCelonisBaseEnum):
    HAS_ONE = "HAS_ONE"
    HAS_MANY = "HAS_MANY"


class EntityTypeNamespace(PyCelonisBaseEnum):
    CELONIS = "celonis"
    CUSTOM = "custom"


class EntityValidationErrorCode(PyCelonisBaseEnum):
    ID_FIELD_NOT_FOUND = "ID_FIELD_NOT_FOUND"
    TIME_FIELD_NOT_FOUND = "TIME_FIELD_NOT_FOUND"
    ID_FIELD_PROTECTED = "ID_FIELD_PROTECTED"
    OBJECT_REF_NOT_FOUND = "OBJECT_REF_NOT_FOUND"
    ENTITY_NOT_FOUND = "ENTITY_NOT_FOUND"
    RELATIONSHIP_NOT_FOUND = "RELATIONSHIP_NOT_FOUND"
    RELATIONSHIP_NOT_FOUND_IN_REFERENCE = "RELATIONSHIP_NOT_FOUND_IN_REFERENCE"
    DUPLICATE_FIELD = "DUPLICATE_FIELD"
    GLOBAL_FIELD_EXTENSION_NOT_FOUND = "GLOBAL_FIELD_EXTENSION_NOT_FOUND"
    GLOBAL_CATEGORY_EXTENSION_NOT_FOUND = "GLOBAL_CATEGORY_EXTENSION_NOT_FOUND"
    DUPLICATE_RELATIONSHIP = "DUPLICATE_RELATIONSHIP"
    DUPLICATE_RELATIONSHIP_TARGET_WITH_SAME_MAPPED_BY = (
        "DUPLICATE_RELATIONSHIP_TARGET_WITH_SAME_MAPPED_BY"
    )
    DUPLICATE_MAPPED_BY = "DUPLICATE_MAPPED_BY"
    ONLY_CUSTOM_RELATIONSHIPS_ALLOWED = "ONLY_CUSTOM_RELATIONSHIPS_ALLOWED"
    INVALID_COMBINATION_OF_MAPPED_BY = "INVALID_COMBINATION_OF_MAPPED_BY"
    INVALID_COMBINATION_OF_OBJECT_REF = "INVALID_COMBINATION_OF_OBJECT_REF"
    RELATIONSHIP_REFERENCED = "RELATIONSHIP_REFERENCED"
    DUPLICATE_CATEGORY_VALUES = "DUPLICATE_CATEGORY_VALUES"
    INVALID_CATEGORY_UPDATE = "INVALID_CATEGORY_UPDATE"
    INVALID_GLOBAL_DELETE = "INVALID_GLOBAL_DELETE"
    INVALID_GLOBAL_RENAME = "INVALID_GLOBAL_RENAME"
    INVALID_RELATIONSHIP_UPDATE = "INVALID_RELATIONSHIP_UPDATE"
    INVALID_FIELD_UPDATE = "INVALID_FIELD_UPDATE"
    CANNOT_UPDATE_ENTITY_NAME = "CANNOT_UPDATE_ENTITY_NAME"
    ALREADY_EXISTS = "ALREADY_EXISTS"
    INVALID_NAMESPACE_ON_FIELD = "INVALID_NAMESPACE_ON_FIELD"
    OBJECT_REFERENCED_IN_O2_O = "OBJECT_REFERENCED_IN_O2O"
    OBJECT_REFERENCED_IN_E2_O = "OBJECT_REFERENCED_IN_E2O"
    OBJECT_REFERENCED_IN_PERSPECTIVE = "OBJECT_REFERENCED_IN_PERSPECTIVE"
    OBJECT_REFERENCED_IN_PROJECTION = "OBJECT_REFERENCED_IN_PROJECTION"
    OBJECT_REFERENCED_IN_SQL_FACTORY = "OBJECT_REFERENCED_IN_SQL_FACTORY"
    EVENT_REFERENCED_IN_PROJECTION = "EVENT_REFERENCED_IN_PROJECTION"
    EVENT_REFERENCED_IN_PROJECTION_NO_RELATION_TO_LEAD_OBJECT = (
        "EVENT_REFERENCED_IN_PROJECTION_NO_RELATION_TO_LEAD_OBJECT"
    )
    EVENT_REFERENCED_IN_SQL_FACTORY = "EVENT_REFERENCED_IN_SQL_FACTORY"
    INVALID_COMBINATION_OF_FIELD_AND_RELATIONSHIP_NAME = (
        "INVALID_COMBINATION_OF_FIELD_AND_RELATIONSHIP_NAME"
    )
    INVALID_TAG = "INVALID_TAG"
    INVALID_CATEGORY = "INVALID_CATEGORY"
    INVALID_CATEGORY_VALUE = "INVALID_CATEGORY_VALUE"
    CATEGORY_VALUE_REFERENCED = "CATEGORY_VALUE_REFERENCED"
    INVALID_CATEGORY_DELETE_REFERENCED = "INVALID_CATEGORY_DELETE_REFERENCED"
    INVALID_CATEGORY_UPDATE_MISSING_VALUES = "INVALID_CATEGORY_UPDATE_MISSING_VALUES"
    SELF_LOOP_NOT_ALLOWED = "SELF_LOOP_NOT_ALLOWED"
    RESERVED_FIELD_NAME = "RESERVED_FIELD_NAME"
    RESERVED_VERTICA_KEYWORD = "RESERVED_VERTICA_KEYWORD"
    OBJECT_REFERENCED_IN_USER_FACTORY_TEMPLATE = (
        "OBJECT_REFERENCED_IN_USER_FACTORY_TEMPLATE"
    )
    EVENT_REFERENCED_IN_USER_FACTORY_TEMPLATE = (
        "EVENT_REFERENCED_IN_USER_FACTORY_TEMPLATE"
    )


class EnvironmentValidationErrorCode(PyCelonisBaseEnum):
    ENVIRONMENT_ALREADY_EXISTS = "ENVIRONMENT_ALREADY_EXISTS"
    ENVIRONMENT_READONLY = "ENVIRONMENT_READONLY"
    ENVIRONMENT_NOT_FOUND = "ENVIRONMENT_NOT_FOUND"
    CANNOT_UPDATE_ENVIRONMENT_NAME = "CANNOT_UPDATE_ENVIRONMENT_NAME"
    CANNOT_UPDATE_OR_DELETE_PROTECTED_ENVIRONMENT = (
        "CANNOT_UPDATE_OR_DELETE_PROTECTED_ENVIRONMENT"
    )
    CANNOT_UPDATE_PROTECTED_PROPERTIES = "CANNOT_UPDATE_PROTECTED_PROPERTIES"
    CANNOT_MODIFY_WITH_DIFFERENT_ENVIRONMENT = (
        "CANNOT_MODIFY_WITH_DIFFERENT_ENVIRONMENT"
    )


class ErrorResponseType(PyCelonisBaseEnum):
    PREVIEW = "PREVIEW"
    ENTITY_VALIDATION = "ENTITY_VALIDATION"
    PERSPECTIVE_VALIDATION = "PERSPECTIVE_VALIDATION"
    SQL_FACTORY_VALIDATION = "SQL_FACTORY_VALIDATION"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    GENERIC = "GENERIC"
    ENVIRONMENT = "ENVIRONMENT"
    PROMOTION_ERROR = "PROMOTION_ERROR"
    MESSAGE_NOT_READABLE = "MESSAGE_NOT_READABLE"
    USER_TEMPLATE = "USER_TEMPLATE"
    REQUEST_VALIDATION = "REQUEST_VALIDATION"


class ExecutionStatus(PyCelonisBaseEnum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    CANCEL = "CANCEL"
    FAIL = "FAIL"
    SKIPPED = "SKIPPED"


class FactoryValidationStatus(PyCelonisBaseEnum):
    VALID = "VALID"
    INVALID = "INVALID"
    NOT_VALIDATED = "NOT_VALIDATED"


class FunctionType(PyCelonisBaseEnum):
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    ADD = "ADD"
    SUBTRACT = "SUBTRACT"
    MULTIPLY = "MULTIPLY"
    DIVIDE = "DIVIDE"
    EQ = "EQ"
    NEQ = "NEQ"
    GT = "GT"
    GTE = "GTE"
    LT = "LT"
    LTE = "LTE"
    CONCAT = "CONCAT"
    IN = "IN"
    ISNOTNULL = "ISNOTNULL"
    ISNULL = "ISNULL"
    LIKE = "LIKE"
    ACCESS = "ACCESS"
    COALESCE = "COALESCE"
    DATEDIFF = "DATEDIFF"
    DAY = "DAY"
    HOUR = "HOUR"
    LENGTH = "LENGTH"
    LTRIM = "LTRIM"
    MINUTE = "MINUTE"
    MONTH = "MONTH"
    REPLACE = "REPLACE"
    RTRIM = "RTRIM"
    SUBSTRING = "SUBSTRING"
    TRIM = "TRIM"
    UUID_GENERATE = "UUID_GENERATE"
    YEAR = "YEAR"
    SHA256 = "SHA256"
    ARRAY = "ARRAY"
    ROW = "ROW"
    CEL_OVERLAPPING_CHECK = "CEL_OVERLAPPING_CHECK"


class HealthContextType(PyCelonisBaseEnum):
    SQL_CONTEXT = "SQL_CONTEXT"
    ENTITY_CONTEXT = "ENTITY_CONTEXT"
    DATA_JOB_EXECUTION_CONTEXT = "DATA_JOB_EXECUTION_CONTEXT"
    DATA_LOAD_HISTORY_CONTEXT = "DATA_LOAD_HISTORY_CONTEXT"


class Kind(PyCelonisBaseEnum):
    OBJECT_STARTER = "OBJECT_STARTER"
    CHANGE_STARTER = "CHANGE_STARTER"


class PaginationMode(PyCelonisBaseEnum):
    ALL = "ALL"
    PAGE = "PAGE"


class PerspectiveRelationshipStrategy(PyCelonisBaseEnum):
    EMBED = "EMBED"
    LINK = "LINK"


class PerspectiveValidationErrorCode(PyCelonisBaseEnum):
    DEFAULT_PROJECTION_NOT_FOUND = "DEFAULT_PROJECTION_NOT_FOUND"
    E2_O_PATH_NOT_FOUND = "E2O_PATH_NOT_FOUND"
    EVENT_REF_NOT_FOUND = "EVENT_REF_NOT_FOUND"
    EVENT_ATTRIBUTE_NOT_FOUND = "EVENT_ATTRIBUTE_NOT_FOUND"
    LEAD_OBJECT_NOT_IN_OBJECTS = "LEAD_OBJECT_NOT_IN_OBJECTS"
    MAPPED_BY_IN_RELATIONSHIP = "MAPPED_BY_IN_RELATIONSHIP"
    OBJECT_CYCLE_DETECTED = "OBJECT_CYCLE_DETECTED"
    OBJECT_REF_NOT_FOUND = "OBJECT_REF_NOT_FOUND"
    PROJECTION_WITHOUT_LEAD_OBJECT = "PROJECTION_WITHOUT_LEAD_OBJECT"
    RELATIONSHIP_NOT_FOUND = "RELATIONSHIP_NOT_FOUND"
    DUPLICATE_OBJECT = "DUPLICATE_OBJECT"
    DUPLICATE_OBJECT_RELATIONSHIP = "DUPLICATE_OBJECT_RELATIONSHIP"
    DUPLICATE_PROJECTION = "DUPLICATE_PROJECTION"
    DUPLICATE_PROJECTION_EVENT = "DUPLICATE_PROJECTION_EVENT"
    DUPLICATE_PERSPECTIVE_NAME = "DUPLICATE_PERSPECTIVE_NAME"
    BASE_REF_NOT_FOUND = "BASE_REF_NOT_FOUND"
    DUPLICATE_EVENT = "DUPLICATE_EVENT"
    UNRELATED_EVENT = "UNRELATED_EVENT"
    DUPLICATE_CUSTOM_ALIAS = "DUPLICATE_CUSTOM_ALIAS"


class PromotionErrorCode(PyCelonisBaseEnum):
    EXECUTION_SERVICE_ERROR = "EXECUTION_SERVICE_ERROR"
    CONTENT_PRE_RELEASE_FEATURE_DEACTIVATED = "CONTENT_PRE_RELEASE_FEATURE_DEACTIVATED"


class RelationshipCardinality(PyCelonisBaseEnum):
    ONE_TO_MANY = "ONE_TO_MANY"
    MANY_TO_ONE = "MANY_TO_ONE"
    MANY_TO_MANY = "MANY_TO_MANY"
    ONE_TO_ONE = "ONE_TO_ONE"


class RelationshipOwner(PyCelonisBaseEnum):
    SOURCE = "SOURCE"
    TARGET = "TARGET"


class ResourceKind(PyCelonisBaseEnum):
    OBJECT = "OBJECT"
    EVENT = "EVENT"
    FIELD_EXTENSION = "FIELD_EXTENSION"
    CATEGORY = "CATEGORY"
    CATEGORY_EXTENSION = "CATEGORY_EXTENSION"
    PERSPECTIVE = "PERSPECTIVE"
    FACTORY_TEMPLATE = "FACTORY_TEMPLATE"
    FACTORY_TEMPLATE_V2 = "FACTORY_TEMPLATE_V2"
    FACTORY_INSTANCE = "FACTORY_INSTANCE"


class SaveMode(PyCelonisBaseEnum):
    VALIDATE = "VALIDATE"
    SKIP_VALIDATION = "SKIP_VALIDATION"
    FORCE_SAVE = "FORCE_SAVE"


class SchemaType(PyCelonisBaseEnum):
    BUSINESS_GRAPH = "BUSINESS_GRAPH"
    GLOBAL = "GLOBAL"
    DATA_SOURCE = "DATA_SOURCE"


class SelectionMode(PyCelonisBaseEnum):
    SINGLE_SELECT = "SINGLE_SELECT"
    MULTI_SELECT = "MULTI_SELECT"


class SimpleIdentityType(PyCelonisBaseEnum):
    USER = "USER"
    APPLICATION = "APPLICATION"


class SqlFactoryValidationErrorCode(PyCelonisBaseEnum):
    SQL_FACTORY_ALREADY_EXISTS = "SQL_FACTORY_ALREADY_EXISTS"
    SQL_STATEMENT_ID_NOT_UNIQUE = "SQL_STATEMENT_ID_NOT_UNIQUE"
    SQL_STATEMENT_INVALID = "SQL_STATEMENT_INVALID"
    SQL_FACTORY_INVALID = "SQL_FACTORY_INVALID"
    CAN_NOT_CREATE_NON_CUSTOM_FACTORY = "CAN_NOT_CREATE_NON_CUSTOM_FACTORY"
    TEMPLATE_INSTANCE_SQL_FACTORY_HAS_SQL = "TEMPLATE_INSTANCE_SQL_FACTORY_HAS_SQL"
    SQL_FACTORY_ALREADY_HAS_TEMPLATE_REFERENCE = (
        "SQL_FACTORY_ALREADY_HAS_TEMPLATE_REFERENCE"
    )
    INVALID_DATA_CONNECTION_ID = "INVALID_DATA_CONNECTION_ID"
    SQL_FACTORY_NAME_WAS_NOT_UPDATED_BLANK = "SQL_FACTORY_NAME_WAS_NOT_UPDATED_BLANK"
    SQL_FACTORY_NAME_WAS_NOT_UPDATED_SAME = "SQL_FACTORY_NAME_WAS_NOT_UPDATED_SAME"
    SQL_FACTORY_DESCRIPTION_WAS_NOT_UPDATED_SAME = (
        "SQL_FACTORY_DESCRIPTION_WAS_NOT_UPDATED_SAME"
    )
    SQL_FACTORY_METADATA_WAS_NOT_UPDATED_NULL = (
        "SQL_FACTORY_METADATA_WAS_NOT_UPDATED_NULL"
    )
    VALIDATION_ERROR = "VALIDATION_ERROR"


class TaskCode(PyCelonisBaseEnum):
    INTEGRATION_ENTITY_JOB_TASK_FAILED = "INTEGRATION_ENTITY_JOB_TASK_FAILED"
    INTEGRATION_PERSPECTIVE_DATA_LOAD_FAILED = (
        "INTEGRATION_PERSPECTIVE_DATA_LOAD_FAILED"
    )
    FES_EMPTY_SQL = "FES_EMPTY_SQL"
    FES_PARSE_ERROR = "FES_PARSE_ERROR"
    FES_VALIDATE_ERROR = "FES_VALIDATE_ERROR"
    FES_MISSING_REQUIRED_ATTRIBUTE = "FES_MISSING_REQUIRED_ATTRIBUTE"
    FES_INVALID_TABLE_REFERENCE = "FES_INVALID_TABLE_REFERENCE"
    FES_TYPE_MISMATCH = "FES_TYPE_MISMATCH"
    FES_SOURCE_TABLE_TYPE_MISMATCH = "FES_SOURCE_TABLE_TYPE_MISMATCH"
    FES_ENTITY_TABLE_NOT_FOUND = "FES_ENTITY_TABLE_NOT_FOUND"
    FES_UNEXPECTED = "FES_UNEXPECTED"


class TaskGroup(PyCelonisBaseEnum):
    SQL_FACTORY_VALIDATION = "SQL_FACTORY_VALIDATION"
    PERSPECTIVE_DATA_LOAD = "PERSPECTIVE_DATA_LOAD"
    DATA_JOB_EXECUTION = "DATA_JOB_EXECUTION"


class TaskSeverity(PyCelonisBaseEnum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class TaskSource(PyCelonisBaseEnum):
    BUSINESS_LANDSCAPE_SERVICE = "BUSINESS_LANDSCAPE_SERVICE"
    FACTORY_EXECUTION_SERVICE = "FACTORY_EXECUTION_SERVICE"
    INTEGRATION_SERVICE = "INTEGRATION_SERVICE"


class TaskType(PyCelonisBaseEnum):
    BASE = "BASE"
    EXTENSION = "EXTENSION"
    EXTENSION_CHANGE = "EXTENSION_CHANGE"
    CHANGE = "CHANGE"


class Type(PyCelonisBaseEnum):
    CASE = "CASE"
    CAST = "CAST"
    CONSTANT = "CONSTANT"
    FIELD_REFERENCE = "FIELD_REFERENCE"
    ATTRIBUTE_PATH = "ATTRIBUTE_PATH"
    FUNCTION = "FUNCTION"


class UserTemplateExceptionErrorCode(PyCelonisBaseEnum):
    TEMPLATE_CANNOT_BE_DELETED = "TEMPLATE_CANNOT_BE_DELETED"
    TEMPLATE_ALREADY_EXISTS = "TEMPLATE_ALREADY_EXISTS"
    TRANSFORMATION_IS_NOT_A_TEMPLATE_INSTANCE = (
        "TRANSFORMATION_IS_NOT_A_TEMPLATE_INSTANCE"
    )


class AttributeDefinitionTransport(PyCelonisBaseModel):
    attribute_name: Optional["str"] = Field(None, alias="attributeName")
    namespace: Optional["str"] = Field(None, alias="namespace")
    relationship: Optional["bool"] = Field(None, alias="relationship")
    type_: Optional["DataType"] = Field(None, alias="type")


class AttributeMappingDefinition(PyCelonisBaseModel):
    expression: Optional["AttributePathExpression"] = Field(None, alias="expression")
    name: Optional["str"] = Field(None, alias="name")
    namespace: Optional["str"] = Field(None, alias="namespace")


class AttributePathExpression(PyCelonisBaseModel):
    segments: Optional["List[Optional[PathSegment]]"] = Field(None, alias="segments")
    starter: Optional["Starter"] = Field(None, alias="starter")
    type_: Optional["Type"] = Field(None, alias="type")


class BaseEntityTransport(PyCelonisBaseModel):
    categories: Optional["List[Optional[CategoryValueReference]]"] = Field(
        None, alias="categories"
    )
    change_date: Optional["float"] = Field(None, alias="changeDate")
    changed_by: Optional["IdentityTransport"] = Field(None, alias="changedBy")
    created_by: Optional["IdentityTransport"] = Field(None, alias="createdBy")
    creation_date: Optional["float"] = Field(None, alias="creationDate")
    description: Optional["str"] = Field(None, alias="description")
    fields: Optional["List[Optional[EntityField]]"] = Field(None, alias="fields")
    id: Optional["str"] = Field(None, alias="id")
    name: Optional["str"] = Field(None, alias="name")
    namespace: Optional["str"] = Field(None, alias="namespace")
    relationships: Optional["List[Optional[EntityRelationship]]"] = Field(
        None, alias="relationships"
    )
    tags: Optional["List[Optional[str]]"] = Field(None, alias="tags")


class BreakdownAttribute(PyCelonisBaseModel):
    metadata: Optional["EntityField"] = Field(None, alias="metadata")


class BusinessLandscapeLayout(PyCelonisBaseModel):
    edge_layouts: Optional["List[Optional[EdgeLayout]]"] = Field(
        None, alias="edgeLayouts"
    )
    node_layouts: Optional["List[Optional[NodeLayout]]"] = Field(
        None, alias="nodeLayouts"
    )


class BusinessLandscapeLayoutOptions(PyCelonisBaseModel):
    edge_layouts: Optional["List[Optional[EdgeLayout]]"] = Field(
        None, alias="edgeLayouts"
    )
    node_layouts: Optional["List[Optional[NodeLayout]]"] = Field(
        None, alias="nodeLayouts"
    )


class Category(PyCelonisBaseModel):
    change_date: Optional["float"] = Field(None, alias="changeDate")
    changed_by: Optional["IdentityTransport"] = Field(None, alias="changedBy")
    created_by: Optional["IdentityTransport"] = Field(None, alias="createdBy")
    creation_date: Optional["float"] = Field(None, alias="creationDate")
    description: Optional["str"] = Field(None, alias="description")
    display_name: Optional["str"] = Field(None, alias="displayName")
    id: Optional["str"] = Field(None, alias="id")
    name: Optional["str"] = Field(None, alias="name")
    namespace: Optional["str"] = Field(None, alias="namespace")
    selection_mode: Optional["SelectionMode"] = Field(None, alias="selectionMode")
    values: Optional["List[Optional[CategoryValue]]"] = Field(None, alias="values")


class CategoryRequestOptions(PyCelonisBaseModel):
    change_date: Optional["float"] = Field(None, alias="changeDate")
    description: Optional["str"] = Field(None, alias="description")
    display_name: Optional["str"] = Field(None, alias="displayName")
    name: Optional["str"] = Field(None, alias="name")
    selection_mode: Optional["SelectionMode"] = Field(None, alias="selectionMode")
    values: Optional["List[Optional[CategoryValueRequestOptions]]"] = Field(
        None, alias="values"
    )


class CategoryValue(PyCelonisBaseModel):
    description: Optional["str"] = Field(None, alias="description")
    display_name: Optional["str"] = Field(None, alias="displayName")
    name: Optional["str"] = Field(None, alias="name")
    namespace: Optional["str"] = Field(None, alias="namespace")


class CategoryValueReference(PyCelonisBaseModel):
    metadata: Optional["EntityMetadata"] = Field(None, alias="metadata")
    values: Optional["List[Optional[EntityMetadata]]"] = Field(None, alias="values")


class CategoryValueReferenceRequestOptions(PyCelonisBaseModel):
    metadata: Optional["EntityMetadata"] = Field(None, alias="metadata")
    values: Optional["List[Optional[CategoryValuesRequestOptions]]"] = Field(
        None, alias="values"
    )


class CategoryValueRequestOptions(PyCelonisBaseModel):
    description: Optional["str"] = Field(None, alias="description")
    display_name: Optional["str"] = Field(None, alias="displayName")
    name: Optional["str"] = Field(None, alias="name")
    namespace: Optional["str"] = Field(None, alias="namespace")


class CategoryValuesRequestOptions(PyCelonisBaseModel):
    display_name: Optional["str"] = Field(None, alias="displayName")
    name: Optional["str"] = Field(None, alias="name")
    namespace: Optional["str"] = Field(None, alias="namespace")


class ColumnDefinitionTransport(PyCelonisBaseModel):
    column_name: Optional["str"] = Field(None, alias="columnName")
    type_: Optional["DataType"] = Field(None, alias="type")


class ColumnToAttributeMapping(PyCelonisBaseModel):
    attribute_name: Optional["str"] = Field(None, alias="attributeName")
    column_name: Optional["str"] = Field(None, alias="columnName")
    column_type: Optional["ColumnType"] = Field(None, alias="columnType")


class Connector(PyCelonisBaseModel):
    id: Optional["str"] = Field(None, alias="id")
    position: Optional["Point"] = Field(None, alias="position")


class ConvertSqlFactoryToTemplateRequestOptions(PyCelonisBaseModel):
    description: Optional["str"] = Field(None, alias="description")
    display_name: Optional["str"] = Field(None, alias="displayName")


class CreateOrUpdateBusinessGraphResponse(PyCelonisBaseModel):
    data_job_id: Optional["str"] = Field(None, alias="dataJobId")
    entity_sql: Optional["Dict[str, Optional[str]]"] = Field(None, alias="entitySql")
    resource_errors: Optional["Dict[str, Optional[str]]"] = Field(
        None, alias="resourceErrors"
    )
    validation_errors: Optional[
        "List[Optional[Union[EventFactoryDataSetValidationError,SqlFactoryDataSetValidationError,None]]]"
    ] = Field(None, alias="validationErrors")


class DataSetTransport(PyCelonisBaseModel):
    attribute_definitions: Optional[
        "List[Optional[AttributeDefinitionTransport]]"
    ] = Field(None, alias="attributeDefinitions")
    columns: Optional["List[Optional[ColumnDefinitionTransport]]"] = Field(
        None, alias="columns"
    )
    rows: Optional["List[Optional[List[Optional[Any]]]]"] = Field(None, alias="rows")


class DataSourceConnection(PyCelonisBaseModel):
    custom_transformation_count: Optional["int"] = Field(
        None, alias="customTransformationCount"
    )
    data_source_id: Optional["str"] = Field(None, alias="dataSourceId")
    data_source_name: Optional["str"] = Field(None, alias="dataSourceName")
    data_source_type: Optional["str"] = Field(None, alias="dataSourceType")
    enabled: Optional["bool"] = Field(None, alias="enabled")
    global_transformation_count: Optional["int"] = Field(
        None, alias="globalTransformationCount"
    )
    mitigate_ccdm_differences: Optional["bool"] = Field(
        None, alias="mitigateCCDMDifferences"
    )
    transformation_type: Optional["str"] = Field(None, alias="transformationType")


class DataSourceConnectionRequestOptions(PyCelonisBaseModel):
    data_source_id: Optional["str"] = Field(None, alias="dataSourceId")
    enabled: Optional["bool"] = Field(None, alias="enabled")
    mitigate_ccdm_differences: Optional["bool"] = Field(
        None, alias="mitigateCCDMDifferences"
    )
    transformation_type: Optional["str"] = Field(None, alias="transformationType")


class DataSourceTransformationType(PyCelonisBaseModel):
    display_name: Optional["str"] = Field(None, alias="displayName")
    source_system: Optional["str"] = Field(None, alias="sourceSystem")
    transformation_type: Optional["str"] = Field(None, alias="transformationType")
    transformations_in_beta: Optional["bool"] = Field(
        None, alias="transformationsInBeta"
    )


class DuplicateSqlFactoryOptions(PyCelonisBaseModel):
    target: Optional["FactoryTarget"] = Field(None, alias="target")


class EdgeLayout(PyCelonisBaseModel):
    id: Optional["str"] = Field(None, alias="id")
    source_connector_id: Optional["str"] = Field(None, alias="sourceConnectorId")
    target_connector_id: Optional["str"] = Field(None, alias="targetConnectorId")
    waypoints: Optional["List[Optional[Point]]"] = Field(None, alias="waypoints")


class EntityField(PyCelonisBaseModel):
    data_type: Optional["DataType"] = Field(None, alias="dataType")
    name: Optional["str"] = Field(None, alias="name")
    namespace: Optional["str"] = Field(None, alias="namespace")


class EntityFieldRequestOptions(PyCelonisBaseModel):
    data_type: Optional["DataType"] = Field(None, alias="dataType")
    name: Optional["str"] = Field(None, alias="name")
    namespace: Optional["str"] = Field(None, alias="namespace")


class EntityFilterOptions(PyCelonisBaseModel):
    name: Optional["str"] = Field(None, alias="name")


class EntityMetadata(PyCelonisBaseModel):
    name: Optional["str"] = Field(None, alias="name")
    namespace: Optional["str"] = Field(None, alias="namespace")


class EntityPreviewRequest(PyCelonisBaseModel):
    entity_kind: Optional["ResourceKind"] = Field(None, alias="entityKind")
    entity_metadata: Optional["EntityMetadata"] = Field(None, alias="entityMetadata")
    row_count: Optional["int"] = Field(None, alias="rowCount")


class EntityPreviewResponse(PyCelonisBaseModel):
    attributes: Optional["DataSetTransport"] = Field(None, alias="attributes")
    changes: Optional["DataSetTransport"] = Field(None, alias="changes")


class EntityRelationship(PyCelonisBaseModel):
    cardinality: Optional["EntityRelationshipCardinality"] = Field(
        None, alias="cardinality"
    )
    name: Optional["str"] = Field(None, alias="name")
    namespace: Optional["str"] = Field(None, alias="namespace")
    target: Optional["EntityRelationshipTarget"] = Field(None, alias="target")


class EntityRelationshipRequestOptions(PyCelonisBaseModel):
    cardinality: Optional["EntityRelationshipCardinality"] = Field(
        None, alias="cardinality"
    )
    name: Optional["str"] = Field(None, alias="name")
    namespace: Optional["str"] = Field(None, alias="namespace")
    target: Optional["EntityRelationshipTarget"] = Field(None, alias="target")


class EntityRelationshipTarget(PyCelonisBaseModel):
    mapped_by: Optional["str"] = Field(None, alias="mappedBy")
    mapped_by_namespace: Optional["str"] = Field(None, alias="mappedByNamespace")
    object_ref: Optional["EntityMetadata"] = Field(None, alias="objectRef")


class EntityRenameRequestOptions(PyCelonisBaseModel):
    change_date: Optional["float"] = Field(None, alias="changeDate")
    name: Optional["str"] = Field(None, alias="name")


class EntityRequestOptions(PyCelonisBaseModel):
    categories: Optional[
        "List[Optional[CategoryValueReferenceRequestOptions]]"
    ] = Field(None, alias="categories")
    change_date: Optional["float"] = Field(None, alias="changeDate")
    description: Optional["str"] = Field(None, alias="description")
    fields: Optional["List[Optional[EntityFieldRequestOptions]]"] = Field(
        None, alias="fields"
    )
    name: Optional["str"] = Field(None, alias="name")
    relationships: Optional["List[Optional[EntityRelationshipRequestOptions]]"] = Field(
        None, alias="relationships"
    )
    tags: Optional["List[Optional[str]]"] = Field(None, alias="tags")


class EntityTypeIdentifier(PyCelonisBaseModel):
    category: Optional["EntityCategory"] = Field(None, alias="category")
    name: Optional["str"] = Field(None, alias="name")
    namespace: Optional["EntityTypeNamespace"] = Field(None, alias="namespace")


class EntityValidationError(PyCelonisBaseModel):
    data: Optional["EntityValidationErrorDetails"] = Field(None, alias="data")
    error_code: Optional["EntityValidationErrorCode"] = Field(None, alias="errorCode")
    message: Optional["str"] = Field(None, alias="message")


class EntityValidationErrorDetails(PyCelonisBaseModel):
    allowed_tags: Optional["List[Optional[str]]"] = Field(None, alias="allowedTags")
    category_value: Optional["EntityMetadata"] = Field(None, alias="categoryValue")
    entity: Optional["ResourceIdentifier"] = Field(None, alias="entity")
    field: Optional["EntityMetadata"] = Field(None, alias="field")
    global_extension_namespace: Optional["str"] = Field(
        None, alias="globalExtensionNamespace"
    )
    invalid_tags: Optional["List[Optional[str]]"] = Field(None, alias="invalidTags")
    lead_object: Optional["EntityMetadata"] = Field(None, alias="leadObject")
    missing_values: Optional["List[Optional[str]]"] = Field(None, alias="missingValues")
    projection_name: Optional["str"] = Field(None, alias="projectionName")
    reference_id: Optional["str"] = Field(None, alias="referenceId")
    referenced_by: Optional["ResourceIdentifier"] = Field(None, alias="referencedBy")
    referenced_by_relationship: Optional["EntityMetadata"] = Field(
        None, alias="referencedByRelationship"
    )
    relationship: Optional["EntityMetadata"] = Field(None, alias="relationship")
    relationship_target: Optional["EntityRelationshipTarget"] = Field(
        None, alias="relationshipTarget"
    )


class Environment(PyCelonisBaseModel):
    change_date: Optional["float"] = Field(None, alias="changeDate")
    changed_by: Optional["IdentityTransport"] = Field(None, alias="changedBy")
    content_tag: Optional["str"] = Field(None, alias="contentTag")
    created_by: Optional["IdentityTransport"] = Field(None, alias="createdBy")
    creation_date: Optional["float"] = Field(None, alias="creationDate")
    display_name: Optional["str"] = Field(None, alias="displayName")
    id: Optional["str"] = Field(None, alias="id")
    name: Optional["str"] = Field(None, alias="name")
    package_key: Optional["str"] = Field(None, alias="packageKey")
    package_version: Optional["str"] = Field(None, alias="packageVersion")
    readonly: Optional["bool"] = Field(None, alias="readonly")


class EnvironmentRequestOptions(PyCelonisBaseModel):
    change_date: Optional["float"] = Field(None, alias="changeDate")
    content_tag: Optional["str"] = Field(None, alias="contentTag")
    display_name: Optional["str"] = Field(None, alias="displayName")
    name: Optional["str"] = Field(None, alias="name")
    readonly: Optional["bool"] = Field(None, alias="readonly")


class EnvironmentValidationErrorDetails(PyCelonisBaseModel):
    entity_environment_name: Optional["str"] = Field(
        None, alias="entityEnvironmentName"
    )
    environment_name: Optional["str"] = Field(None, alias="environmentName")


class ErrorResponse(PyCelonisBaseModel):
    details: Optional["List[Optional[Any]]"] = Field(None, alias="details")
    error: Optional["str"] = Field(None, alias="error")
    message: Optional["str"] = Field(None, alias="message")
    status_code: Optional["int"] = Field(None, alias="statusCode")
    type_: Optional["ErrorResponseType"] = Field(None, alias="type")


class EventEntity(PyCelonisBaseModel):
    categories: Optional["List[Optional[CategoryValueReference]]"] = Field(
        None, alias="categories"
    )
    change_date: Optional["float"] = Field(None, alias="changeDate")
    changed_by: Optional["IdentityTransport"] = Field(None, alias="changedBy")
    created_by: Optional["IdentityTransport"] = Field(None, alias="createdBy")
    creation_date: Optional["float"] = Field(None, alias="creationDate")
    description: Optional["str"] = Field(None, alias="description")
    fields: Optional["List[Optional[EntityField]]"] = Field(None, alias="fields")
    id: Optional["str"] = Field(None, alias="id")
    name: Optional["str"] = Field(None, alias="name")
    namespace: Optional["str"] = Field(None, alias="namespace")
    relationships: Optional["List[Optional[EntityRelationship]]"] = Field(
        None, alias="relationships"
    )
    tags: Optional["List[Optional[str]]"] = Field(None, alias="tags")


class EventEntityRequestOptions(PyCelonisBaseModel):
    categories: Optional[
        "List[Optional[CategoryValueReferenceRequestOptions]]"
    ] = Field(None, alias="categories")
    change_date: Optional["float"] = Field(None, alias="changeDate")
    description: Optional["str"] = Field(None, alias="description")
    fields: Optional["List[Optional[EntityFieldRequestOptions]]"] = Field(
        None, alias="fields"
    )
    name: Optional["str"] = Field(None, alias="name")
    relationships: Optional["List[Optional[EntityRelationshipRequestOptions]]"] = Field(
        None, alias="relationships"
    )
    tags: Optional["List[Optional[str]]"] = Field(None, alias="tags")


class EventFactory(PyCelonisBaseModel):
    attribute_definitions: Optional[
        "List[Optional[AttributeMappingDefinition]]"
    ] = Field(None, alias="attributeDefinitions")
    change_date: Optional["float"] = Field(None, alias="changeDate")
    changed_by: Optional["IdentityTransport"] = Field(None, alias="changedBy")
    created_by: Optional["IdentityTransport"] = Field(None, alias="createdBy")
    creation_date: Optional["float"] = Field(None, alias="creationDate")
    description: Optional["str"] = Field(None, alias="description")
    disabled: Optional["bool"] = Field(None, alias="disabled")
    filter_expression: Optional[
        "Union[AttributePathExpression,CaseExpression,CastExpression,ConstantExpression,FieldReferenceExpression,FunctionExpression,None]"
    ] = Field(None, alias="filterExpression")
    id: Optional["str"] = Field(None, alias="id")
    id_expression: Optional[
        "Union[AttributePathExpression,CaseExpression,CastExpression,ConstantExpression,FieldReferenceExpression,FunctionExpression,None]"
    ] = Field(None, alias="idExpression")
    local_parameters: Optional["List[Optional[FactoryParameter]]"] = Field(
        None, alias="localParameters"
    )
    name: Optional["str"] = Field(None, alias="name")
    namespace: Optional["str"] = Field(None, alias="namespace")
    tags: Optional["List[Optional[str]]"] = Field(None, alias="tags")
    target: Optional["FactoryTarget"] = Field(None, alias="target")


class EventFactoryRequestOptions(PyCelonisBaseModel):
    attribute_definitions: Optional[
        "List[Optional[AttributeMappingDefinition]]"
    ] = Field(None, alias="attributeDefinitions")
    change_date: Optional["float"] = Field(None, alias="changeDate")
    description: Optional["str"] = Field(None, alias="description")
    disabled: Optional["bool"] = Field(None, alias="disabled")
    filter_expression: Optional[
        "Union[AttributePathExpression,CaseExpression,CastExpression,ConstantExpression,FieldReferenceExpression,FunctionExpression,None]"
    ] = Field(None, alias="filterExpression")
    id_expression: Optional[
        "Union[AttributePathExpression,CaseExpression,CastExpression,ConstantExpression,FieldReferenceExpression,FunctionExpression,None]"
    ] = Field(None, alias="idExpression")
    local_parameters: Optional["List[Optional[FactoryParameter]]"] = Field(
        None, alias="localParameters"
    )
    name: Optional["str"] = Field(None, alias="name")
    tags: Optional["List[Optional[str]]"] = Field(None, alias="tags")
    target: Optional["FactoryTarget"] = Field(None, alias="target")


class EventInfo(PyCelonisBaseModel):
    breakdown_attributes: Optional["List[Optional[BreakdownAttribute]]"] = Field(
        None, alias="breakdownAttributes"
    )
    name: Optional["str"] = Field(None, alias="name")
    namespace: Optional["str"] = Field(None, alias="namespace")


class ExecutionHistoryTransport(PyCelonisBaseModel):
    environment: Optional["str"] = Field(None, alias="environment")
    execution_id: Optional["str"] = Field(None, alias="executionId")
    execution_start_date: Optional["datetime"] = Field(None, alias="executionStartDate")
    execution_status: Optional["ExecutionStatus"] = Field(None, alias="executionStatus")
    job_id: Optional["str"] = Field(None, alias="jobId")
    timestamp: Optional["datetime"] = Field(None, alias="timestamp")
    type_execution_status_list: Optional[
        "List[Optional[TypeExecutionStatusTransport]]"
    ] = Field(None, alias="typeExecutionStatusList")


class Expression(PyCelonisBaseModel):
    type_: Optional["Type"] = Field(None, alias="type")


class FactoryDataSet(PyCelonisBaseModel):
    id: Optional["str"] = Field(None, alias="id")
    type_: Optional["str"] = Field(None, alias="type")


class FactoryDataSetPreviewResponse(PyCelonisBaseModel):
    data: Optional["PreviewTransport"] = Field(None, alias="data")
    error: Optional[
        "Union[EventFactoryDataSetValidationError,SqlFactoryDataSetValidationError,None]"
    ] = Field(None, alias="error")
    unmapped_attributes: Optional[
        "List[Optional[AttributeDefinitionTransport]]"
    ] = Field(None, alias="unmappedAttributes")


class FactoryDataSetValidationError(PyCelonisBaseModel):
    cause: Optional["Cause"] = Field(None, alias="cause")


class FactoryDataSetValidationResponse(PyCelonisBaseModel):
    error: Optional[
        "Union[EventFactoryDataSetValidationError,SqlFactoryDataSetValidationError,None]"
    ] = Field(None, alias="error")
    error_list: Optional[
        "List[Optional[Union[EventFactoryDataSetValidationError,SqlFactoryDataSetValidationError,None]]]"
    ] = Field(None, alias="errorList")
    unmapped_attributes: Optional[
        "List[Optional[AttributeDefinitionTransport]]"
    ] = Field(None, alias="unmappedAttributes")
    valid: Optional["bool"] = Field(None, alias="valid")


class FactoryDataSourceTransport(PyCelonisBaseModel):
    data_source_id: Optional["str"] = Field(None, alias="dataSourceId")
    data_source_type: Optional["str"] = Field(None, alias="dataSourceType")
    display_name: Optional["str"] = Field(None, alias="displayName")


class FactoryListTransport(PyCelonisBaseModel):
    change_date: Optional["float"] = Field(None, alias="changeDate")
    changed_by: Optional["IdentityTransport"] = Field(None, alias="changedBy")
    created_by: Optional["IdentityTransport"] = Field(None, alias="createdBy")
    creation_date: Optional["float"] = Field(None, alias="creationDate")
    data_connection_id: Optional["str"] = Field(None, alias="dataConnectionId")
    disabled: Optional["bool"] = Field(None, alias="disabled")
    display_name: Optional["str"] = Field(None, alias="displayName")
    factory_id: Optional["str"] = Field(None, alias="factoryId")
    has_overwrites: Optional["bool"] = Field(None, alias="hasOverwrites")
    name: Optional["str"] = Field(None, alias="name")
    namespace: Optional["str"] = Field(None, alias="namespace")
    target: Optional["FactoryTarget"] = Field(None, alias="target")
    user_factory_template_reference: Optional["EntityMetadata"] = Field(
        None, alias="userFactoryTemplateReference"
    )
    validation_status: Optional["FactoryValidationStatus"] = Field(
        None, alias="validationStatus"
    )


class FactoryParameter(PyCelonisBaseModel):
    name: Optional["str"] = Field(None, alias="name")
    value: Optional["str"] = Field(None, alias="value")


class FactorySourceTablesTransport(PyCelonisBaseModel):
    tables: Optional["List[Optional[TableDefinitionTransport]]"] = Field(
        None, alias="tables"
    )


class FactoryTarget(PyCelonisBaseModel):
    entity_ref: Optional["EntityMetadata"] = Field(None, alias="entityRef")
    kind: Optional["ResourceKind"] = Field(None, alias="kind")


class FactoryValidationError(PyCelonisBaseModel):
    attribute_name: Optional["str"] = Field(None, alias="attributeName")
    data_set_id: Optional["str"] = Field(None, alias="dataSetId")
    detailed_message: Optional["str"] = Field(None, alias="detailedMessage")
    factory: Optional["EntityMetadata"] = Field(None, alias="factory")
    factory_id: Optional["str"] = Field(None, alias="factoryId")
    overwrite: Optional["bool"] = Field(None, alias="overwrite")
    position: Optional["SqlPosition"] = Field(None, alias="position")


class GlobalParameter(PyCelonisBaseModel):
    change_date: Optional["float"] = Field(None, alias="changeDate")
    changed_by: Optional["IdentityTransport"] = Field(None, alias="changedBy")
    created_by: Optional["IdentityTransport"] = Field(None, alias="createdBy")
    creation_date: Optional["float"] = Field(None, alias="creationDate")
    id: Optional["str"] = Field(None, alias="id")
    namespace: Optional["str"] = Field(None, alias="namespace")
    parameter_key: Optional["str"] = Field(None, alias="parameterKey")
    value: Optional["str"] = Field(None, alias="value")


class GlobalParameterCreateOptions(PyCelonisBaseModel):
    namespace: Optional["str"] = Field(None, alias="namespace")
    parameter_key: Optional["str"] = Field(None, alias="parameterKey")
    value: Optional["str"] = Field(None, alias="value")


class GlobalParameterFilterOptions(PyCelonisBaseModel):
    namespace: Optional["str"] = Field(None, alias="namespace")
    parameter_key: Optional["str"] = Field(None, alias="parameterKey")


class GlobalParameterUpdateOptions(PyCelonisBaseModel):
    namespace: Optional["str"] = Field(None, alias="namespace")
    value: Optional["str"] = Field(None, alias="value")


class HealthContext(PyCelonisBaseModel):
    type_: Optional["HealthContextType"] = Field(None, alias="type")


class IdentityTransport(PyCelonisBaseModel):
    id: Optional["str"] = Field(None, alias="id")
    name: Optional["str"] = Field(None, alias="name")
    type_: Optional["SimpleIdentityType"] = Field(None, alias="type")


class Location(PyCelonisBaseModel):
    begin_column_number: Optional["int"] = Field(None, alias="beginColumnNumber")
    begin_line_number: Optional["int"] = Field(None, alias="beginLineNumber")
    end_column_number: Optional["int"] = Field(None, alias="endColumnNumber")
    end_line_number: Optional["int"] = Field(None, alias="endLineNumber")


class NodeLayout(PyCelonisBaseModel):
    connectors: Optional["List[Optional[Connector]]"] = Field(None, alias="connectors")
    height: Optional["float"] = Field(None, alias="height")
    id: Optional["str"] = Field(None, alias="id")
    width: Optional["float"] = Field(None, alias="width")
    x: Optional["float"] = Field(None, alias="x")
    y: Optional["float"] = Field(None, alias="y")


class ObjectEntity(PyCelonisBaseModel):
    categories: Optional["List[Optional[CategoryValueReference]]"] = Field(
        None, alias="categories"
    )
    change_date: Optional["float"] = Field(None, alias="changeDate")
    changed_by: Optional["IdentityTransport"] = Field(None, alias="changedBy")
    color: Optional["str"] = Field(None, alias="color")
    created_by: Optional["IdentityTransport"] = Field(None, alias="createdBy")
    creation_date: Optional["float"] = Field(None, alias="creationDate")
    description: Optional["str"] = Field(None, alias="description")
    fields: Optional["List[Optional[EntityField]]"] = Field(None, alias="fields")
    id: Optional["str"] = Field(None, alias="id")
    managed: Optional["bool"] = Field(None, alias="managed")
    multi_link: Optional["bool"] = Field(None, alias="multiLink")
    name: Optional["str"] = Field(None, alias="name")
    namespace: Optional["str"] = Field(None, alias="namespace")
    relationships: Optional["List[Optional[EntityRelationship]]"] = Field(
        None, alias="relationships"
    )
    tags: Optional["List[Optional[str]]"] = Field(None, alias="tags")


class ObjectEntityRequestOptions(PyCelonisBaseModel):
    categories: Optional[
        "List[Optional[CategoryValueReferenceRequestOptions]]"
    ] = Field(None, alias="categories")
    change_date: Optional["float"] = Field(None, alias="changeDate")
    color: Optional["str"] = Field(None, alias="color")
    description: Optional["str"] = Field(None, alias="description")
    fields: Optional["List[Optional[EntityFieldRequestOptions]]"] = Field(
        None, alias="fields"
    )
    name: Optional["str"] = Field(None, alias="name")
    relationships: Optional["List[Optional[EntityRelationshipRequestOptions]]"] = Field(
        None, alias="relationships"
    )
    tags: Optional["List[Optional[str]]"] = Field(None, alias="tags")


class ObjectFactorySourceTransport(PyCelonisBaseModel):
    data_connections: Optional["List[Optional[SourceDataConnectionTransport]]"] = Field(
        None, alias="dataConnections"
    )


class ObjectRelationship(PyCelonisBaseModel):
    bidirectional: Optional["bool"] = Field(None, alias="bidirectional")
    cardinality: Optional["RelationshipCardinality"] = Field(None, alias="cardinality")
    inactive: Optional["bool"] = Field(None, alias="inactive")
    owner: Optional["RelationshipOwner"] = Field(None, alias="owner")
    source: Optional["RelationshipIdentifier"] = Field(None, alias="source")
    target: Optional["RelationshipIdentifier"] = Field(None, alias="target")


class ObjectRelationshipRequestOptions(PyCelonisBaseModel):
    bidirectional: Optional["bool"] = Field(None, alias="bidirectional")
    cardinality: Optional["RelationshipCardinality"] = Field(None, alias="cardinality")
    source: Optional["RelationshipIdentifierRequestOptions"] = Field(
        None, alias="source"
    )
    target: Optional["RelationshipIdentifierRequestOptions"] = Field(
        None, alias="target"
    )


class PageCategory(PyCelonisBaseModel):
    content: Optional["List[Optional[Category]]"] = Field(None, alias="content")
    empty: Optional["bool"] = Field(None, alias="empty")
    first: Optional["bool"] = Field(None, alias="first")
    last: Optional["bool"] = Field(None, alias="last")
    page_number: Optional["int"] = Field(None, alias="pageNumber")
    page_size: Optional["int"] = Field(None, alias="pageSize")
    total_count: Optional["int"] = Field(None, alias="totalCount")
    total_pages: Optional["int"] = Field(None, alias="totalPages")


class PageEventEntity(PyCelonisBaseModel):
    content: Optional["List[Optional[EventEntity]]"] = Field(None, alias="content")
    empty: Optional["bool"] = Field(None, alias="empty")
    first: Optional["bool"] = Field(None, alias="first")
    last: Optional["bool"] = Field(None, alias="last")
    page_number: Optional["int"] = Field(None, alias="pageNumber")
    page_size: Optional["int"] = Field(None, alias="pageSize")
    total_count: Optional["int"] = Field(None, alias="totalCount")
    total_pages: Optional["int"] = Field(None, alias="totalPages")


class PageEventFactory(PyCelonisBaseModel):
    content: Optional["List[Optional[EventFactory]]"] = Field(None, alias="content")
    empty: Optional["bool"] = Field(None, alias="empty")
    first: Optional["bool"] = Field(None, alias="first")
    last: Optional["bool"] = Field(None, alias="last")
    page_number: Optional["int"] = Field(None, alias="pageNumber")
    page_size: Optional["int"] = Field(None, alias="pageSize")
    total_count: Optional["int"] = Field(None, alias="totalCount")
    total_pages: Optional["int"] = Field(None, alias="totalPages")


class PageFactoryListTransport(PyCelonisBaseModel):
    content: Optional["List[Optional[FactoryListTransport]]"] = Field(
        None, alias="content"
    )
    empty: Optional["bool"] = Field(None, alias="empty")
    first: Optional["bool"] = Field(None, alias="first")
    last: Optional["bool"] = Field(None, alias="last")
    page_number: Optional["int"] = Field(None, alias="pageNumber")
    page_size: Optional["int"] = Field(None, alias="pageSize")
    total_count: Optional["int"] = Field(None, alias="totalCount")
    total_pages: Optional["int"] = Field(None, alias="totalPages")


class PageGlobalParameter(PyCelonisBaseModel):
    content: Optional["List[Optional[GlobalParameter]]"] = Field(None, alias="content")
    empty: Optional["bool"] = Field(None, alias="empty")
    first: Optional["bool"] = Field(None, alias="first")
    last: Optional["bool"] = Field(None, alias="last")
    page_number: Optional["int"] = Field(None, alias="pageNumber")
    page_size: Optional["int"] = Field(None, alias="pageSize")
    total_count: Optional["int"] = Field(None, alias="totalCount")
    total_pages: Optional["int"] = Field(None, alias="totalPages")


class PageObjectEntity(PyCelonisBaseModel):
    content: Optional["List[Optional[ObjectEntity]]"] = Field(None, alias="content")
    empty: Optional["bool"] = Field(None, alias="empty")
    first: Optional["bool"] = Field(None, alias="first")
    last: Optional["bool"] = Field(None, alias="last")
    page_number: Optional["int"] = Field(None, alias="pageNumber")
    page_size: Optional["int"] = Field(None, alias="pageSize")
    total_count: Optional["int"] = Field(None, alias="totalCount")
    total_pages: Optional["int"] = Field(None, alias="totalPages")


class PageObjectRelationship(PyCelonisBaseModel):
    content: Optional["List[Optional[ObjectRelationship]]"] = Field(
        None, alias="content"
    )
    empty: Optional["bool"] = Field(None, alias="empty")
    first: Optional["bool"] = Field(None, alias="first")
    last: Optional["bool"] = Field(None, alias="last")
    page_number: Optional["int"] = Field(None, alias="pageNumber")
    page_size: Optional["int"] = Field(None, alias="pageSize")
    total_count: Optional["int"] = Field(None, alias="totalCount")
    total_pages: Optional["int"] = Field(None, alias="totalPages")


class PagePerspective(PyCelonisBaseModel):
    content: Optional["List[Optional[Perspective]]"] = Field(None, alias="content")
    empty: Optional["bool"] = Field(None, alias="empty")
    first: Optional["bool"] = Field(None, alias="first")
    last: Optional["bool"] = Field(None, alias="last")
    page_number: Optional["int"] = Field(None, alias="pageNumber")
    page_size: Optional["int"] = Field(None, alias="pageSize")
    total_count: Optional["int"] = Field(None, alias="totalCount")
    total_pages: Optional["int"] = Field(None, alias="totalPages")


class PageProcess(PyCelonisBaseModel):
    content: Optional["List[Optional[Process]]"] = Field(None, alias="content")
    empty: Optional["bool"] = Field(None, alias="empty")
    first: Optional["bool"] = Field(None, alias="first")
    last: Optional["bool"] = Field(None, alias="last")
    page_number: Optional["int"] = Field(None, alias="pageNumber")
    page_size: Optional["int"] = Field(None, alias="pageSize")
    total_count: Optional["int"] = Field(None, alias="totalCount")
    total_pages: Optional["int"] = Field(None, alias="totalPages")


class PageTaskGroupReport(PyCelonisBaseModel):
    content: Optional["List[Optional[TaskGroupReport]]"] = Field(None, alias="content")
    empty: Optional["bool"] = Field(None, alias="empty")
    first: Optional["bool"] = Field(None, alias="first")
    last: Optional["bool"] = Field(None, alias="last")
    page_number: Optional["int"] = Field(None, alias="pageNumber")
    page_size: Optional["int"] = Field(None, alias="pageSize")
    total_count: Optional["int"] = Field(None, alias="totalCount")
    total_pages: Optional["int"] = Field(None, alias="totalPages")


class PageUserFactoryTemplateListTransport(PyCelonisBaseModel):
    content: Optional["List[Optional[UserFactoryTemplateListTransport]]"] = Field(
        None, alias="content"
    )
    empty: Optional["bool"] = Field(None, alias="empty")
    first: Optional["bool"] = Field(None, alias="first")
    last: Optional["bool"] = Field(None, alias="last")
    page_number: Optional["int"] = Field(None, alias="pageNumber")
    page_size: Optional["int"] = Field(None, alias="pageSize")
    total_count: Optional["int"] = Field(None, alias="totalCount")
    total_pages: Optional["int"] = Field(None, alias="totalPages")


class PageWorkspaceUsage(PyCelonisBaseModel):
    content: Optional["List[Optional[WorkspaceUsage]]"] = Field(None, alias="content")
    empty: Optional["bool"] = Field(None, alias="empty")
    first: Optional["bool"] = Field(None, alias="first")
    last: Optional["bool"] = Field(None, alias="last")
    page_number: Optional["int"] = Field(None, alias="pageNumber")
    page_size: Optional["int"] = Field(None, alias="pageSize")
    total_count: Optional["int"] = Field(None, alias="totalCount")
    total_pages: Optional["int"] = Field(None, alias="totalPages")


class Pagination(PyCelonisBaseModel):
    page: Optional["int"] = Field(None, alias="page")
    request_mode: Optional["PaginationMode"] = Field(None, alias="requestMode")
    size: Optional["int"] = Field(None, alias="size")


class PathSegment(PyCelonisBaseModel):
    name: Optional["str"] = Field(None, alias="name")
    namespace: Optional["str"] = Field(None, alias="namespace")


class Perspective(PyCelonisBaseModel):
    base_ref: Optional["EntityMetadata"] = Field(None, alias="baseRef")
    categories: Optional["List[Optional[CategoryValueReference]]"] = Field(
        None, alias="categories"
    )
    change_date: Optional["float"] = Field(None, alias="changeDate")
    changed_by: Optional["IdentityTransport"] = Field(None, alias="changedBy")
    created_by: Optional["IdentityTransport"] = Field(None, alias="createdBy")
    creation_date: Optional["float"] = Field(None, alias="creationDate")
    default_projection: Optional["str"] = Field(None, alias="defaultProjection")
    description: Optional["str"] = Field(None, alias="description")
    events: Optional["List[Optional[PerspectiveSpecEvent]]"] = Field([], alias="events")
    id: Optional["str"] = Field(None, alias="id")
    name: Optional["str"] = Field(None, alias="name")
    namespace: Optional["str"] = Field(None, alias="namespace")
    objects: Optional["List[Optional[PerspectiveSpecObject]]"] = Field(
        [], alias="objects"
    )
    projections: Optional["List[Optional[Projection]]"] = Field(
        None, alias="projections"
    )
    tags: Optional["List[Optional[str]]"] = Field(None, alias="tags")


class PerspectiveFilterOptions(PyCelonisBaseModel):
    name: Optional["str"] = Field(None, alias="name")


class PerspectiveRequestOptions(PyCelonisBaseModel):
    base_ref: Optional["EntityMetadata"] = Field(None, alias="baseRef")
    categories: Optional[
        "List[Optional[CategoryValueReferenceRequestOptions]]"
    ] = Field(None, alias="categories")
    change_date: Optional["float"] = Field(None, alias="changeDate")
    default_projection: Optional["str"] = Field(None, alias="defaultProjection")
    description: Optional["str"] = Field(None, alias="description")
    # events: Optional['List[Optional[PerspectiveSpecEvent]]'] = Field(None, alias="events")
    name: Optional["str"] = Field(None, alias="name")
    objects: Optional["List[Optional[PerspectiveSpecObject]]"] = Field(
        None, alias="objects"
    )
    projections: Optional["List[Optional[Projection]]"] = Field(
        None, alias="projections"
    )
    tags: Optional["List[Optional[str]]"] = Field(None, alias="tags")


class PerspectiveSpecEvent(PyCelonisBaseModel):
    custom_alias: Optional["str"] = Field(None, alias="customAlias")
    default_alias: Optional["str"] = Field(None, alias="defaultAlias")
    entity_metadata: Optional["EntityMetadata"] = Field(None, alias="entityMetadata")
    name: Optional["str"] = Field(None, alias="name")
    namespace: Optional["str"] = Field(None, alias="namespace")


class PerspectiveSpecObject(PyCelonisBaseModel):
    custom_alias: Optional["str"] = Field(None, alias="customAlias")
    default_alias: Optional["str"] = Field(None, alias="defaultAlias")
    entity_metadata: Optional["EntityMetadata"] = Field(None, alias="entityMetadata")
    name: Optional["str"] = Field(None, alias="name")
    namespace: Optional["str"] = Field(None, alias="namespace")
    origin_ref: Optional["EntityMetadata"] = Field(None, alias="originRef")
    relationships: Optional[
        "List[Optional[PerspectiveSpecObjectRelationship]]"
    ] = Field(None, alias="relationships")


class PerspectiveSpecObjectRelationship(PyCelonisBaseModel):
    name: Optional["str"] = Field(None, alias="name")
    namespace: Optional["str"] = Field(None, alias="namespace")
    origin_ref: Optional["EntityMetadata"] = Field(None, alias="originRef")
    strategy: Optional["PerspectiveRelationshipStrategy"] = Field(
        None, alias="strategy"
    )


class PerspectiveValidationError(PyCelonisBaseModel):
    data: Optional["PerspectiveValidationErrorDetails"] = Field(None, alias="data")
    error_code: Optional["PerspectiveValidationErrorCode"] = Field(
        None, alias="errorCode"
    )
    message: Optional["str"] = Field(None, alias="message")


class PerspectiveValidationErrorDetails(PyCelonisBaseModel):
    attribute: Optional["EntityMetadata"] = Field(None, alias="attribute")
    base_ref: Optional["EntityMetadata"] = Field(None, alias="baseRef")
    custom_alias: Optional["str"] = Field(None, alias="customAlias")
    default_projection: Optional["str"] = Field(None, alias="defaultProjection")
    event: Optional["EntityMetadata"] = Field(None, alias="event")
    lead_object: Optional["EntityMetadata"] = Field(None, alias="leadObject")
    object: Optional["EntityMetadata"] = Field(None, alias="object")
    perspective: Optional["EntityMetadata"] = Field(None, alias="perspective")
    projection_name: Optional["str"] = Field(None, alias="projectionName")
    relationship: Optional["EntityMetadata"] = Field(None, alias="relationship")


class Point(PyCelonisBaseModel):
    x: Optional["float"] = Field(None, alias="x")
    y: Optional["float"] = Field(None, alias="y")


class PreviewTransport(PyCelonisBaseModel):
    result: Optional["DataSetTransport"] = Field(None, alias="result")
    sample_size: Optional["int"] = Field(None, alias="sampleSize")


class Process(PyCelonisBaseModel):
    change_date: Optional["float"] = Field(None, alias="changeDate")
    changed_by: Optional["IdentityTransport"] = Field(None, alias="changedBy")
    created_by: Optional["IdentityTransport"] = Field(None, alias="createdBy")
    creation_date: Optional["float"] = Field(None, alias="creationDate")
    data_source_connections: Optional["List[Optional[DataSourceConnection]]"] = Field(
        None, alias="dataSourceConnections"
    )
    description: Optional["str"] = Field(None, alias="description")
    display_name: Optional["str"] = Field(None, alias="displayName")
    enable_date: Optional["float"] = Field(None, alias="enableDate")
    enabled: Optional["bool"] = Field(None, alias="enabled")
    event_count: Optional["int"] = Field(None, alias="eventCount")
    name: Optional["str"] = Field(None, alias="name")
    object_count: Optional["int"] = Field(None, alias="objectCount")


class ProcessCreateOptions(PyCelonisBaseModel):
    data_source_connections: Optional["List[Optional[DataSourceConnection]]"] = Field(
        None, alias="dataSourceConnections"
    )
    description: Optional["str"] = Field(None, alias="description")
    display_name: Optional["str"] = Field(None, alias="displayName")


class ProcessUpdateOptions(PyCelonisBaseModel):
    data_source_connections: Optional[
        "List[Optional[DataSourceConnectionRequestOptions]]"
    ] = Field(None, alias="dataSourceConnections")
    description: Optional["str"] = Field(None, alias="description")
    display_name: Optional["str"] = Field(None, alias="displayName")


class Projection(PyCelonisBaseModel):
    event_list: Optional["List[Optional[EventInfo]]"] = Field(None, alias="eventList")
    events: Optional["List[Optional[EntityMetadata]]"] = Field(None, alias="events")
    lead_object: Optional["EntityMetadata"] = Field(None, alias="leadObject")
    name: Optional["str"] = Field(None, alias="name")
    origin_ref: Optional["EntityMetadata"] = Field(None, alias="originRef")


class PromotionErrorDetails(PyCelonisBaseModel):
    content_version: Optional["str"] = Field(None, alias="contentVersion")
    execution_exception_message: Optional["str"] = Field(
        None, alias="executionExceptionMessage"
    )


class QualifiedName(PyCelonisBaseModel):
    name: Optional["str"] = Field(None, alias="name")
    schema_: Optional["str"] = Field(None, alias="schema")


class RelationshipIdentifier(PyCelonisBaseModel):
    object: Optional["EntityMetadata"] = Field(None, alias="object")
    processes: Optional["List[Optional[str]]"] = Field(None, alias="processes")
    relationship: Optional["EntityMetadata"] = Field(None, alias="relationship")


class RelationshipIdentifierRequestOptions(PyCelonisBaseModel):
    object: Optional["EntityMetadata"] = Field(None, alias="object")
    relationship: Optional["str"] = Field(None, alias="relationship")


class ResourceIdentifier(PyCelonisBaseModel):
    factory_source_system: Optional["str"] = Field(None, alias="factorySourceSystem")
    kind: Optional["ResourceKind"] = Field(None, alias="kind")
    name: Optional["str"] = Field(None, alias="name")
    namespace: Optional["str"] = Field(None, alias="namespace")


class ResourceNotFoundErrorDetails(PyCelonisBaseModel):
    class_name: Optional["str"] = Field(None, alias="className")
    id: Optional["str"] = Field(None, alias="id")


class SchemaIdentifier(PyCelonisBaseModel):
    data_source_id: Optional["str"] = Field(None, alias="dataSourceId")
    pool_id: Optional["str"] = Field(None, alias="poolId")
    type_: Optional["SchemaType"] = Field(None, alias="type")


class SourceDataConnectionTransport(PyCelonisBaseModel):
    data_source_id: Optional["str"] = Field(None, alias="dataSourceId")
    data_source_name: Optional["str"] = Field(None, alias="dataSourceName")
    data_source_type: Optional["str"] = Field(None, alias="dataSourceType")
    tables: Optional["List[Optional[TableDefinitionTransport]]"] = Field(
        None, alias="tables"
    )


class SqlDataSetOverwrite(PyCelonisBaseModel):
    attribute_names: Optional["List[Optional[str]]"] = Field(
        None, alias="attributeNames"
    )
    sql: Optional["str"] = Field(None, alias="sql")


class SqlFactoryChangeStateManyRequest(PyCelonisBaseModel):
    disabled: Optional["bool"] = Field(None, alias="disabled")
    ids: Optional["List[Optional[str]]"] = Field(None, alias="ids")


class SqlFactoryDataConnection(PyCelonisBaseModel):
    data_connection_id: Optional["str"] = Field(None, alias="dataConnectionId")
    data_connection_type: Optional["str"] = Field(None, alias="dataConnectionType")
    display_name: Optional["str"] = Field(None, alias="displayName")


class SqlFactoryDataSetPreviewRequest(PyCelonisBaseModel):
    based_on_factory_template: Optional["bool"] = Field(
        None, alias="basedOnFactoryTemplate"
    )
    data_connection_id: Optional["str"] = Field(None, alias="dataConnectionId")
    data_set_target: Optional["DataSetTarget"] = Field(None, alias="dataSetTarget")
    dataset: Optional["SqlFactoryDataset"] = Field(None, alias="dataset")
    local_parameters: Optional["List[Optional[FactoryParameter]]"] = Field(
        None, alias="localParameters"
    )
    namespace: Optional["str"] = Field(None, alias="namespace")
    relationship_name: Optional["str"] = Field(None, alias="relationshipName")
    show_overwrite: Optional["bool"] = Field(None, alias="showOverwrite")
    target: Optional["FactoryTarget"] = Field(None, alias="target")


class SqlFactoryFilterOptions(PyCelonisBaseModel):
    include_user_template_transformations: Optional["bool"] = Field(
        None, alias="includeUserTemplateTransformations"
    )
    kind: Optional["ResourceKind"] = Field(None, alias="kind")
    name: Optional["str"] = Field(None, alias="name")
    namespace: Optional["str"] = Field(None, alias="namespace")


class SqlFactoryRelationshipTransformation(PyCelonisBaseModel):
    relationship_name: Optional["str"] = Field(None, alias="relationshipName")
    sql_factory_datasets: Optional[
        "List[Optional[Union[SqlFactoryDataset,None]]]"
    ] = Field(None, alias="sqlFactoryDatasets")


class SqlFactoryRequestOptions(PyCelonisBaseModel):
    change_date: Optional["float"] = Field(None, alias="changeDate")
    data_connection_id: Optional["str"] = Field(None, alias="dataConnectionId")
    description: Optional["str"] = Field(None, alias="description")
    disabled: Optional["bool"] = Field(None, alias="disabled")
    display_name: Optional["str"] = Field(None, alias="displayName")
    draft: Optional["bool"] = Field(None, alias="draft")
    local_parameters: Optional["List[Optional[FactoryParameter]]"] = Field(
        None, alias="localParameters"
    )
    namespace: Optional["str"] = Field(None, alias="namespace")
    save_mode: Optional["SaveMode"] = Field(None, alias="saveMode")
    target: Optional["FactoryTarget"] = Field(None, alias="target")
    transformations: Optional[
        "List[Optional[SqlFactoryTransformationTransport]]"
    ] = Field(None, alias="transformations")
    user_template_name: Optional["str"] = Field(None, alias="userTemplateName")


class SqlFactoryTransformationTransport(PyCelonisBaseModel):
    change_sql_factory_datasets: Optional[
        "List[Optional[Union[SqlFactoryDataset,None]]]"
    ] = Field(None, alias="changeSqlFactoryDatasets")
    foreign_key_names: Optional["List[Optional[str]]"] = Field(
        None, alias="foreignKeyNames"
    )
    namespace: Optional["str"] = Field(None, alias="namespace")
    property_names: Optional["List[Optional[str]]"] = Field(None, alias="propertyNames")
    property_sql_factory_datasets: Optional[
        "List[Optional[Union[SqlFactoryDataset,None]]]"
    ] = Field(None, alias="propertySqlFactoryDatasets")
    relationship_transformations: Optional[
        "List[Optional[SqlFactoryRelationshipTransformation]]"
    ] = Field(None, alias="relationshipTransformations")


class SqlFactoryTransport(PyCelonisBaseModel):
    change_date: Optional["float"] = Field(None, alias="changeDate")
    changed_by: Optional["IdentityTransport"] = Field(None, alias="changedBy")
    created_by: Optional["IdentityTransport"] = Field(None, alias="createdBy")
    creation_date: Optional["float"] = Field(None, alias="creationDate")
    data_connection_id: Optional["str"] = Field(None, alias="dataConnectionId")
    description: Optional["str"] = Field(None, alias="description")
    disabled: Optional["bool"] = Field(None, alias="disabled")
    display_name: Optional["str"] = Field(None, alias="displayName")
    draft: Optional["bool"] = Field(None, alias="draft")
    factory_id: Optional["str"] = Field(None, alias="factoryId")
    factory_validation_status: Optional["FactoryValidationStatus"] = Field(
        None, alias="factoryValidationStatus"
    )
    has_user_template: Optional["bool"] = Field(None, alias="hasUserTemplate")
    local_parameters: Optional["List[Optional[FactoryParameter]]"] = Field(
        None, alias="localParameters"
    )
    namespace: Optional["str"] = Field(None, alias="namespace")
    target: Optional["FactoryTarget"] = Field(None, alias="target")
    transformations: Optional[
        "List[Optional[SqlFactoryTransformationTransport]]"
    ] = Field(None, alias="transformations")


class SqlFactoryUpdateMetadataRequestOptions(PyCelonisBaseModel):
    change_date: Optional["float"] = Field(None, alias="changeDate")
    description: Optional["str"] = Field(None, alias="description")
    display_name: Optional["str"] = Field(None, alias="displayName")


class SqlFactoryValidationErrorDetails(PyCelonisBaseModel):
    errors: Optional["List[Optional[FactoryValidationError]]"] = Field(
        None, alias="errors"
    )


class SqlPosition(PyCelonisBaseModel):
    column: Optional["int"] = Field(None, alias="column")
    end_column: Optional["int"] = Field(None, alias="endColumn")
    end_line: Optional["int"] = Field(None, alias="endLine")
    line: Optional["int"] = Field(None, alias="line")


class Starter(PyCelonisBaseModel):
    entity_metadata: Optional["EntityMetadata"] = Field(None, alias="entityMetadata")
    kind: Optional["Kind"] = Field(None, alias="kind")


class TableDefinitionTransport(PyCelonisBaseModel):
    columns: Optional["List[Optional[ColumnDefinitionTransport]]"] = Field(
        None, alias="columns"
    )
    name: Optional["QualifiedName"] = Field(None, alias="name")


class TableIdentifier(PyCelonisBaseModel):
    schema_identifier: Optional["SchemaIdentifier"] = Field(
        None, alias="schemaIdentifier"
    )
    table_name: Optional["str"] = Field(None, alias="tableName")
    type_: Optional["Type"] = Field(None, alias="type")


class TableImportRequestOptions(PyCelonisBaseModel):
    qualified_name: Optional["QualifiedName"] = Field(None, alias="qualifiedName")


class TableImportTransport(PyCelonisBaseModel):
    column_to_attribute_mapping: Optional["Dict[str, Optional[str]]"] = Field(
        None, alias="columnToAttributeMapping"
    )
    column_to_attribute_mappings_list: Optional[
        "List[Optional[ColumnToAttributeMapping]]"
    ] = Field(None, alias="columnToAttributeMappingsList")
    entity_transport: Optional["BaseEntityTransport"] = Field(
        None, alias="entityTransport"
    )
    sql_factory_transport: Optional["SqlFactoryTransport"] = Field(
        None, alias="sqlFactoryTransport"
    )
    table_identifier: Optional["TableIdentifier"] = Field(None, alias="tableIdentifier")


class TableMappingRequestOptions(PyCelonisBaseModel):
    column_to_attribute_mapping: Optional["Dict[str, Optional[str]]"] = Field(
        None, alias="columnToAttributeMapping"
    )
    column_to_attribute_mappings_list: Optional[
        "List[Optional[ColumnToAttributeMapping]]"
    ] = Field(None, alias="columnToAttributeMappingsList")
    entity_request_options: Optional["EntityRequestOptions"] = Field(
        None, alias="entityRequestOptions"
    )
    table_identifier: Optional["TableIdentifier"] = Field(None, alias="tableIdentifier")


class TaskEntityFilterOptions(PyCelonisBaseModel):
    severity: Optional["TaskSeverity"] = Field(None, alias="severity")


class TaskExecutionStatusTransport(PyCelonisBaseModel):
    execution_start_date: Optional["datetime"] = Field(None, alias="executionStartDate")
    execution_status: Optional["ExecutionStatus"] = Field(None, alias="executionStatus")
    task_id: Optional["str"] = Field(None, alias="taskId")
    task_type: Optional["TaskType"] = Field(None, alias="taskType")


class TaskGroupReport(PyCelonisBaseModel):
    group: Optional["TaskGroup"] = Field(None, alias="group")
    task_transports: Optional["List[Optional[TaskTransport]]"] = Field(
        None, alias="taskTransports"
    )


class TaskTransport(PyCelonisBaseModel):
    code: Optional["TaskCode"] = Field(None, alias="code")
    context: Optional[
        "Union[DataJobExecutionContext,DataLoadHistoryContext,EntityContext,SqlContext,None]"
    ] = Field(None, alias="context")
    creation_date: Optional["float"] = Field(None, alias="creationDate")
    severity: Optional["TaskSeverity"] = Field(None, alias="severity")
    source: Optional["TaskSource"] = Field(None, alias="source")


class TypeExecutionStatusTransport(PyCelonisBaseModel):
    execution_status: Optional["ExecutionStatus"] = Field(None, alias="executionStatus")
    kind: Optional["ResourceKind"] = Field(None, alias="kind")
    name: Optional["str"] = Field(None, alias="name")
    namespace: Optional["str"] = Field(None, alias="namespace")
    task_execution_status_list: Optional[
        "List[Optional[TaskExecutionStatusTransport]]"
    ] = Field(None, alias="taskExecutionStatusList")


class UserFactoryTemplateListTransport(PyCelonisBaseModel):
    change_date: Optional["float"] = Field(None, alias="changeDate")
    changed_by: Optional["IdentityTransport"] = Field(None, alias="changedBy")
    created_by: Optional["IdentityTransport"] = Field(None, alias="createdBy")
    creation_date: Optional["float"] = Field(None, alias="creationDate")
    description: Optional["str"] = Field(None, alias="description")
    id: Optional["str"] = Field(None, alias="id")
    instance_names: Optional["List[Optional[str]]"] = Field(None, alias="instanceNames")
    instances_count: Optional["int"] = Field(None, alias="instancesCount")
    name: Optional["str"] = Field(None, alias="name")
    target: Optional["FactoryTarget"] = Field(None, alias="target")


class UserFactoryTemplateRequestOptions(PyCelonisBaseModel):
    change_date: Optional["float"] = Field(None, alias="changeDate")
    description: Optional["str"] = Field(None, alias="description")
    draft: Optional["bool"] = Field(None, alias="draft")
    local_parameters: Optional["List[Optional[FactoryParameter]]"] = Field(
        None, alias="localParameters"
    )
    name: Optional["str"] = Field(None, alias="name")
    target: Optional["FactoryTarget"] = Field(None, alias="target")
    transformations: Optional[
        "List[Optional[SqlFactoryTransformationTransport]]"
    ] = Field(None, alias="transformations")
    updated_sql_factories: Optional[
        "Dict[str, Optional[SqlFactoryRequestOptions]]"
    ] = Field(None, alias="updatedSqlFactories")


class UserFactoryTemplateTransport(PyCelonisBaseModel):
    change_date: Optional["float"] = Field(None, alias="changeDate")
    changed_by: Optional["IdentityTransport"] = Field(None, alias="changedBy")
    created_by: Optional["IdentityTransport"] = Field(None, alias="createdBy")
    creation_date: Optional["float"] = Field(None, alias="creationDate")
    description: Optional["str"] = Field(None, alias="description")
    draft: Optional["bool"] = Field(None, alias="draft")
    id: Optional["str"] = Field(None, alias="id")
    local_parameters: Optional["List[Optional[FactoryParameter]]"] = Field(
        None, alias="localParameters"
    )
    name: Optional["str"] = Field(None, alias="name")
    sql_factory_transports: Optional["List[Optional[SqlFactoryTransport]]"] = Field(
        None, alias="sqlFactoryTransports"
    )
    target: Optional["FactoryTarget"] = Field(None, alias="target")
    transformations: Optional[
        "List[Optional[SqlFactoryTransformationTransport]]"
    ] = Field(None, alias="transformations")


class WhenClause(PyCelonisBaseModel):
    condition: Optional["Expression"] = Field(None, alias="condition")
    then: Optional["Expression"] = Field(None, alias="then")


class WorkspaceUsage(PyCelonisBaseModel):
    last_usage_date: Optional["datetime"] = Field(None, alias="lastUsageDate")
    usage_count: Optional["int"] = Field(None, alias="usageCount")
    workspace_id: Optional["str"] = Field(None, alias="workspaceId")
    workspace_name: Optional["str"] = Field(None, alias="workspaceName")


class CaseExpression(Expression, PyCelonisBaseModel):
    else_expression: Optional["Expression"] = Field(None, alias="elseExpression")
    when_clauses: Optional["List[Optional[WhenClause]]"] = Field(
        None, alias="whenClauses"
    )


class CastExpression(Expression, PyCelonisBaseModel):
    expression: Optional["Expression"] = Field(None, alias="expression")
    target_type: Optional["DataType"] = Field(None, alias="targetType")


class ConstantExpression(Expression, PyCelonisBaseModel):
    data_type: Optional["DataType"] = Field(None, alias="dataType")
    value: Optional["Any"] = Field(None, alias="value")


class DataJobExecutionContext(HealthContext, PyCelonisBaseModel):
    execution_id: Optional["str"] = Field(None, alias="executionId")
    job_id: Optional["str"] = Field(None, alias="jobId")
    kind: Optional["ResourceKind"] = Field(None, alias="kind")
    name: Optional["str"] = Field(None, alias="name")
    namespace: Optional["str"] = Field(None, alias="namespace")
    task_id: Optional["str"] = Field(None, alias="taskId")
    task_type: Optional["TaskType"] = Field(None, alias="taskType")


class DataLoadHistoryContext(HealthContext, PyCelonisBaseModel):
    data_load_id: Optional["str"] = Field(None, alias="dataLoadId")
    data_model_id: Optional["str"] = Field(None, alias="dataModelId")
    kind: Optional["ResourceKind"] = Field(None, alias="kind")
    load_status: Optional["DataModelLoadStatus"] = Field(None, alias="loadStatus")
    load_type: Optional["DataLoadType"] = Field(None, alias="loadType")
    name: Optional["str"] = Field(None, alias="name")
    namespace: Optional["str"] = Field(None, alias="namespace")
    status_message: Optional["str"] = Field(None, alias="statusMessage")


class EntityContext(HealthContext, PyCelonisBaseModel):
    kind: Optional["ResourceKind"] = Field(None, alias="kind")
    name: Optional["str"] = Field(None, alias="name")
    namespace: Optional["str"] = Field(None, alias="namespace")


class EntityValidationErrorResponse(ErrorResponse, PyCelonisBaseModel):
    errors: Optional["List[Optional[EntityValidationError]]"] = Field(
        None, alias="errors"
    )


class EnvironmentValidationErrorResponse(ErrorResponse, PyCelonisBaseModel):
    error_code: Optional["EnvironmentValidationErrorCode"] = Field(
        None, alias="errorCode"
    )
    error_details: Optional["EnvironmentValidationErrorDetails"] = Field(
        None, alias="errorDetails"
    )


class EventFactoryDataSetValidationError(
    FactoryDataSetValidationError, PyCelonisBaseModel
):
    attribute_name: Optional["str"] = Field(None, alias="attributeName")
    data_set_id: Optional["str"] = Field(None, alias="dataSetId")
    factory_id: Optional["str"] = Field(None, alias="factoryId")
    message: Optional["str"] = Field(None, alias="message")


class FactoryDatasetRef(FactoryDataSet, PyCelonisBaseModel):
    pass


class FieldReferenceExpression(Expression, PyCelonisBaseModel):
    field: Optional["str"] = Field(None, alias="field")
    parent: Optional["str"] = Field(None, alias="parent")


class FunctionExpression(Expression, PyCelonisBaseModel):
    args: Optional["List[Optional[Expression]]"] = Field(None, alias="args")
    name: Optional["FunctionType"] = Field(None, alias="name")


class GenericErrorResponse(ErrorResponse, PyCelonisBaseModel):
    pass


class MessageNotReadableErrorResponse(ErrorResponse, PyCelonisBaseModel):
    pass


class PerspectiveValidationErrorResponse(ErrorResponse, PyCelonisBaseModel):
    errors: Optional["List[Optional[PerspectiveValidationError]]"] = Field(
        None, alias="errors"
    )


class PreviewErrorResponse(ErrorResponse, PyCelonisBaseModel):
    location: Optional["Location"] = Field(None, alias="location")


class PromotionErrorResponse(ErrorResponse, PyCelonisBaseModel):
    error_code: Optional["PromotionErrorCode"] = Field(None, alias="errorCode")
    error_details: Optional["PromotionErrorDetails"] = Field(None, alias="errorDetails")


class ResourceNotFoundErrorResponse(ErrorResponse, PyCelonisBaseModel):
    error_details: Optional["ResourceNotFoundErrorDetails"] = Field(
        None, alias="errorDetails"
    )


class SqlContext(HealthContext, PyCelonisBaseModel):
    additional_info: Optional["str"] = Field(None, alias="additionalInfo")
    attribute_name: Optional["str"] = Field(None, alias="attributeName")
    column: Optional["int"] = Field(None, alias="column")
    data_set_id: Optional["str"] = Field(None, alias="dataSetId")
    end_column: Optional["int"] = Field(None, alias="endColumn")
    end_line: Optional["int"] = Field(None, alias="endLine")
    factory_id: Optional["str"] = Field(None, alias="factoryId")
    kind: Optional["ResourceKind"] = Field(None, alias="kind")
    line: Optional["int"] = Field(None, alias="line")
    name: Optional["str"] = Field(None, alias="name")
    namespace: Optional["str"] = Field(None, alias="namespace")
    overwrite: Optional["bool"] = Field(None, alias="overwrite")
    schema_identifier: Optional["SchemaIdentifier"] = Field(
        None, alias="schemaIdentifier"
    )


class SqlFactoryDataSetValidationError(
    FactoryDataSetValidationError, PyCelonisBaseModel
):
    attribute_name: Optional["str"] = Field(None, alias="attributeName")
    data_set_id: Optional["str"] = Field(None, alias="dataSetId")
    factory: Optional["EntityMetadata"] = Field(None, alias="factory")
    factory_id: Optional["str"] = Field(None, alias="factoryId")
    message: Optional["str"] = Field(None, alias="message")
    overwrite: Optional["bool"] = Field(None, alias="overwrite")
    position: Optional["SqlPosition"] = Field(None, alias="position")
    schema_identifier: Optional["SchemaIdentifier"] = Field(
        None, alias="schemaIdentifier"
    )


class SqlFactoryDataset(FactoryDataSet, PyCelonisBaseModel):
    complete_overwrite: Optional["bool"] = Field(None, alias="completeOverwrite")
    disabled: Optional["bool"] = Field(None, alias="disabled")
    materialise_cte: Optional["bool"] = Field(None, alias="materialiseCte")
    overwrite: Optional["SqlDataSetOverwrite"] = Field(None, alias="overwrite")
    sql: Optional["str"] = Field(None, alias="sql")


class SqlFactoryValidationErrorResponse(ErrorResponse, PyCelonisBaseModel):
    error_code: Optional["SqlFactoryValidationErrorCode"] = Field(
        None, alias="errorCode"
    )
    error_details: Optional["SqlFactoryValidationErrorDetails"] = Field(
        None, alias="errorDetails"
    )


class UserTemplateErrorResponse(ErrorResponse, PyCelonisBaseModel):
    error_code: Optional["UserTemplateExceptionErrorCode"] = Field(
        None, alias="errorCode"
    )


AttributeDefinitionTransport.update_forward_refs()
AttributeMappingDefinition.update_forward_refs()
AttributePathExpression.update_forward_refs()
BaseEntityTransport.update_forward_refs()
BreakdownAttribute.update_forward_refs()
BusinessLandscapeLayout.update_forward_refs()
BusinessLandscapeLayoutOptions.update_forward_refs()
Category.update_forward_refs()
CategoryRequestOptions.update_forward_refs()
CategoryValue.update_forward_refs()
CategoryValueReference.update_forward_refs()
CategoryValueReferenceRequestOptions.update_forward_refs()
CategoryValueRequestOptions.update_forward_refs()
CategoryValuesRequestOptions.update_forward_refs()
ColumnDefinitionTransport.update_forward_refs()
ColumnToAttributeMapping.update_forward_refs()
Connector.update_forward_refs()
ConvertSqlFactoryToTemplateRequestOptions.update_forward_refs()
CreateOrUpdateBusinessGraphResponse.update_forward_refs()
DataSetTransport.update_forward_refs()
DataSourceConnection.update_forward_refs()
DataSourceConnectionRequestOptions.update_forward_refs()
DataSourceTransformationType.update_forward_refs()
DuplicateSqlFactoryOptions.update_forward_refs()
EdgeLayout.update_forward_refs()
EntityField.update_forward_refs()
EntityFieldRequestOptions.update_forward_refs()
EntityFilterOptions.update_forward_refs()
EntityMetadata.update_forward_refs()
EntityPreviewRequest.update_forward_refs()
EntityPreviewResponse.update_forward_refs()
EntityRelationship.update_forward_refs()
EntityRelationshipRequestOptions.update_forward_refs()
EntityRelationshipTarget.update_forward_refs()
EntityRenameRequestOptions.update_forward_refs()
EntityRequestOptions.update_forward_refs()
EntityTypeIdentifier.update_forward_refs()
EntityValidationError.update_forward_refs()
EntityValidationErrorDetails.update_forward_refs()
Environment.update_forward_refs()
EnvironmentRequestOptions.update_forward_refs()
EnvironmentValidationErrorDetails.update_forward_refs()
ErrorResponse.update_forward_refs()
EventEntity.update_forward_refs()
EventEntityRequestOptions.update_forward_refs()
EventFactory.update_forward_refs()
EventFactoryRequestOptions.update_forward_refs()
EventInfo.update_forward_refs()
ExecutionHistoryTransport.update_forward_refs()
Expression.update_forward_refs()
FactoryDataSet.update_forward_refs()
FactoryDataSetPreviewResponse.update_forward_refs()
FactoryDataSetValidationError.update_forward_refs()
FactoryDataSetValidationResponse.update_forward_refs()
FactoryDataSourceTransport.update_forward_refs()
FactoryListTransport.update_forward_refs()
FactoryParameter.update_forward_refs()
FactorySourceTablesTransport.update_forward_refs()
FactoryTarget.update_forward_refs()
FactoryValidationError.update_forward_refs()
GlobalParameter.update_forward_refs()
GlobalParameterCreateOptions.update_forward_refs()
GlobalParameterFilterOptions.update_forward_refs()
GlobalParameterUpdateOptions.update_forward_refs()
HealthContext.update_forward_refs()
IdentityTransport.update_forward_refs()
Location.update_forward_refs()
NodeLayout.update_forward_refs()
ObjectEntity.update_forward_refs()
ObjectEntityRequestOptions.update_forward_refs()
ObjectFactorySourceTransport.update_forward_refs()
ObjectRelationship.update_forward_refs()
ObjectRelationshipRequestOptions.update_forward_refs()
PageCategory.update_forward_refs()
PageEventEntity.update_forward_refs()
PageEventFactory.update_forward_refs()
PageFactoryListTransport.update_forward_refs()
PageGlobalParameter.update_forward_refs()
PageObjectEntity.update_forward_refs()
PageObjectRelationship.update_forward_refs()
PagePerspective.update_forward_refs()
PageProcess.update_forward_refs()
PageTaskGroupReport.update_forward_refs()
PageUserFactoryTemplateListTransport.update_forward_refs()
PageWorkspaceUsage.update_forward_refs()
Pagination.update_forward_refs()
PathSegment.update_forward_refs()
Perspective.update_forward_refs()
PerspectiveFilterOptions.update_forward_refs()
PerspectiveRequestOptions.update_forward_refs()
PerspectiveSpecEvent.update_forward_refs()
PerspectiveSpecObject.update_forward_refs()
PerspectiveSpecObjectRelationship.update_forward_refs()
PerspectiveValidationError.update_forward_refs()
PerspectiveValidationErrorDetails.update_forward_refs()
Point.update_forward_refs()
PreviewTransport.update_forward_refs()
Process.update_forward_refs()
ProcessCreateOptions.update_forward_refs()
ProcessUpdateOptions.update_forward_refs()
Projection.update_forward_refs()
PromotionErrorDetails.update_forward_refs()
QualifiedName.update_forward_refs()
RelationshipIdentifier.update_forward_refs()
RelationshipIdentifierRequestOptions.update_forward_refs()
ResourceIdentifier.update_forward_refs()
ResourceNotFoundErrorDetails.update_forward_refs()
SchemaIdentifier.update_forward_refs()
SourceDataConnectionTransport.update_forward_refs()
SqlDataSetOverwrite.update_forward_refs()
SqlFactoryChangeStateManyRequest.update_forward_refs()
SqlFactoryDataConnection.update_forward_refs()
SqlFactoryDataSetPreviewRequest.update_forward_refs()
SqlFactoryFilterOptions.update_forward_refs()
SqlFactoryRelationshipTransformation.update_forward_refs()
SqlFactoryRequestOptions.update_forward_refs()
SqlFactoryTransformationTransport.update_forward_refs()
SqlFactoryTransport.update_forward_refs()
SqlFactoryUpdateMetadataRequestOptions.update_forward_refs()
SqlFactoryValidationErrorDetails.update_forward_refs()
SqlPosition.update_forward_refs()
Starter.update_forward_refs()
TableDefinitionTransport.update_forward_refs()
TableIdentifier.update_forward_refs()
TableImportRequestOptions.update_forward_refs()
TableImportTransport.update_forward_refs()
TableMappingRequestOptions.update_forward_refs()
TaskEntityFilterOptions.update_forward_refs()
TaskExecutionStatusTransport.update_forward_refs()
TaskGroupReport.update_forward_refs()
TaskTransport.update_forward_refs()
TypeExecutionStatusTransport.update_forward_refs()
UserFactoryTemplateListTransport.update_forward_refs()
UserFactoryTemplateRequestOptions.update_forward_refs()
UserFactoryTemplateTransport.update_forward_refs()
WhenClause.update_forward_refs()
WorkspaceUsage.update_forward_refs()
CaseExpression.update_forward_refs()
CastExpression.update_forward_refs()
ConstantExpression.update_forward_refs()
DataJobExecutionContext.update_forward_refs()
DataLoadHistoryContext.update_forward_refs()
EntityContext.update_forward_refs()
EntityValidationErrorResponse.update_forward_refs()
EnvironmentValidationErrorResponse.update_forward_refs()
EventFactoryDataSetValidationError.update_forward_refs()
FactoryDatasetRef.update_forward_refs()
FieldReferenceExpression.update_forward_refs()
FunctionExpression.update_forward_refs()
GenericErrorResponse.update_forward_refs()
MessageNotReadableErrorResponse.update_forward_refs()
PerspectiveValidationErrorResponse.update_forward_refs()
PreviewErrorResponse.update_forward_refs()
PromotionErrorResponse.update_forward_refs()
ResourceNotFoundErrorResponse.update_forward_refs()
SqlContext.update_forward_refs()
SqlFactoryDataSetValidationError.update_forward_refs()
SqlFactoryDataset.update_forward_refs()
SqlFactoryValidationErrorResponse.update_forward_refs()
UserTemplateErrorResponse.update_forward_refs()


class BusinessLandscapePycelonis:
    @staticmethod
    def get_api_v1_ccdm_versions(client: Client, **kwargs: Any) -> List[Optional[str]]:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v1/ccdm-versions'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v1/ccdm-versions",
                "tracking_type": "API_REQUEST",
            },
        )

        return client.request(
            method="GET",
            url=f"/bl/api/v1/ccdm-versions",
            parse_json=True,
            type_=List[Optional[str]],
            **kwargs,
        )

    @staticmethod
    def get_api_v1_environments(
        client: Client, **kwargs: Any
    ) -> List[Optional[Environment]]:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v1/environments'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v1/environments",
                "tracking_type": "API_REQUEST",
            },
        )

        return client.request(
            method="GET",
            url=f"/bl/api/v1/environments",
            parse_json=True,
            type_=List[Optional[Environment]],
            **kwargs,
        )

    @staticmethod
    def post_api_v1_environments(
        client: Client, request_body: EnvironmentRequestOptions, **kwargs: Any
    ) -> Environment:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v1/environments'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v1/environments",
                "tracking_type": "API_REQUEST",
            },
        )

        return client.request(
            method="POST",
            url=f"/bl/api/v1/environments",
            request_body=request_body,
            parse_json=True,
            type_=Environment,
            **kwargs,
        )

    @staticmethod
    def post_api_v1_environments_init(client: Client, **kwargs: Any) -> None:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v1/environments/init'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v1/environments/init",
                "tracking_type": "API_REQUEST",
            },
        )

        return client.request(
            method="POST", url=f"/bl/api/v1/environments/init", **kwargs
        )

    @staticmethod
    def post_api_v1_environments_promote(
        client: Client,
        environment: Optional["str"] = None,
        target_environment: Optional["str"] = None,
        include_user_template_transformations: Optional["bool"] = None,
        use_v2_manifest: Optional["bool"] = None,
        **kwargs: Any,
    ) -> None:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v1/environments/promote'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v1/environments/promote",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        if target_environment is not None:
            if isinstance(target_environment, PyCelonisBaseModel):
                params.update(target_environment.json_dict(by_alias=True))
            elif isinstance(target_environment, dict):
                params.update(target_environment)
            else:
                params["targetEnvironment"] = target_environment
        if include_user_template_transformations is not None:
            if isinstance(include_user_template_transformations, PyCelonisBaseModel):
                params.update(
                    include_user_template_transformations.json_dict(by_alias=True)
                )
            elif isinstance(include_user_template_transformations, dict):
                params.update(include_user_template_transformations)
            else:
                params[
                    "includeUserTemplateTransformations"
                ] = include_user_template_transformations
        if use_v2_manifest is not None:
            if isinstance(use_v2_manifest, PyCelonisBaseModel):
                params.update(use_v2_manifest.json_dict(by_alias=True))
            elif isinstance(use_v2_manifest, dict):
                params.update(use_v2_manifest)
            else:
                params["useV2Manifest"] = use_v2_manifest
        return client.request(
            method="POST",
            url=f"/bl/api/v1/environments/promote",
            params=params,
            **kwargs,
        )

    @staticmethod
    def get_api_v1_environments_environment_id(
        client: Client, environment_id: str, **kwargs: Any
    ) -> Environment:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v1/environments/{environment_id}'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v1/environments/{environment_id}",
                "tracking_type": "API_REQUEST",
            },
        )

        return client.request(
            method="GET",
            url=f"/bl/api/v1/environments/{environment_id}",
            parse_json=True,
            type_=Environment,
            **kwargs,
        )

    @staticmethod
    def put_api_v1_environments_environment_id(
        client: Client,
        environment_id: str,
        request_body: EnvironmentRequestOptions,
        **kwargs: Any,
    ) -> Environment:
        logger.debug(
            f"Request: 'PUT' -> '/bl/api/v1/environments/{environment_id}'",
            extra={
                "request_type": "PUT",
                "path": "/bl/api/v1/environments/{environment_id}",
                "tracking_type": "API_REQUEST",
            },
        )

        return client.request(
            method="PUT",
            url=f"/bl/api/v1/environments/{environment_id}",
            request_body=request_body,
            parse_json=True,
            type_=Environment,
            **kwargs,
        )

    @staticmethod
    def delete_api_v1_environments_environment_id(
        client: Client, environment_id: str, **kwargs: Any
    ) -> None:
        logger.debug(
            f"Request: 'DELETE' -> '/bl/api/v1/environments/{environment_id}'",
            extra={
                "request_type": "DELETE",
                "path": "/bl/api/v1/environments/{environment_id}",
                "tracking_type": "API_REQUEST",
            },
        )

        return client.request(
            method="DELETE", url=f"/bl/api/v1/environments/{environment_id}", **kwargs
        )

    @staticmethod
    def get_api_v1_execution_factories_data_source_tables(
        client: Client,
        data_source_id: Optional["str"] = None,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> List[Optional[TableDefinitionTransport]]:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v1/execution/factories/data-source-tables'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v1/execution/factories/data-source-tables",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if data_source_id is not None:
            if isinstance(data_source_id, PyCelonisBaseModel):
                params.update(data_source_id.json_dict(by_alias=True))
            elif isinstance(data_source_id, dict):
                params.update(data_source_id)
            else:
                params["dataSourceId"] = data_source_id
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v1/execution/factories/data-source-tables",
            params=params,
            parse_json=True,
            type_=List[Optional[TableDefinitionTransport]],
            **kwargs,
        )

    @staticmethod
    def get_api_v1_execution_factories_data_sources(
        client: Client, environment: Optional["str"] = None, **kwargs: Any
    ) -> List[Optional[FactoryDataSourceTransport]]:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v1/execution/factories/data-sources'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v1/execution/factories/data-sources",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v1/execution/factories/data-sources",
            params=params,
            parse_json=True,
            type_=List[Optional[FactoryDataSourceTransport]],
            **kwargs,
        )

    @staticmethod
    def post_api_v1_execution_factories_entity_preview(
        client: Client,
        request_body: EntityPreviewRequest,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> EntityPreviewResponse:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v1/execution/factories/entity/preview'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v1/execution/factories/entity/preview",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="POST",
            url=f"/bl/api/v1/execution/factories/entity/preview",
            params=params,
            request_body=request_body,
            parse_json=True,
            type_=EntityPreviewResponse,
            **kwargs,
        )

    @staticmethod
    def post_api_v1_execution_factories_events_execute(
        client: Client, environment: Optional["str"] = None, **kwargs: Any
    ) -> None:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v1/execution/factories/events/execute'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v1/execution/factories/events/execute",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="POST",
            url=f"/bl/api/v1/execution/factories/events/execute",
            params=params,
            **kwargs,
        )

    @staticmethod
    def post_api_v1_execution_factories_events_preview(
        client: Client, environment: Optional["str"] = None, **kwargs: Any
    ) -> PreviewTransport:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v1/execution/factories/events/preview'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v1/execution/factories/events/preview",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="POST",
            url=f"/bl/api/v1/execution/factories/events/preview",
            params=params,
            parse_json=True,
            type_=PreviewTransport,
            **kwargs,
        )

    @staticmethod
    def post_api_v1_execution_factories_events_source_preview(
        client: Client,
        request_body: EntityTypeIdentifier,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> PreviewTransport:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v1/execution/factories/events/source-preview'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v1/execution/factories/events/source-preview",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="POST",
            url=f"/bl/api/v1/execution/factories/events/source-preview",
            params=params,
            request_body=request_body,
            parse_json=True,
            type_=PreviewTransport,
            **kwargs,
        )

    @staticmethod
    def post_api_v1_execution_factories_objects_execute(
        client: Client, environment: Optional["str"] = None, **kwargs: Any
    ) -> None:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v1/execution/factories/objects/execute'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v1/execution/factories/objects/execute",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="POST",
            url=f"/bl/api/v1/execution/factories/objects/execute",
            params=params,
            **kwargs,
        )

    @staticmethod
    def post_api_v1_execution_factories_objects_preview(
        client: Client, environment: Optional["str"] = None, **kwargs: Any
    ) -> PreviewTransport:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v1/execution/factories/objects/preview'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v1/execution/factories/objects/preview",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="POST",
            url=f"/bl/api/v1/execution/factories/objects/preview",
            params=params,
            parse_json=True,
            type_=PreviewTransport,
            **kwargs,
        )

    @staticmethod
    def get_api_v1_execution_factories_objects_source_preview(
        client: Client,
        schema_name: Optional["str"] = None,
        table_name: Optional["str"] = None,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> PreviewTransport:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v1/execution/factories/objects/source-preview'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v1/execution/factories/objects/source-preview",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if schema_name is not None:
            if isinstance(schema_name, PyCelonisBaseModel):
                params.update(schema_name.json_dict(by_alias=True))
            elif isinstance(schema_name, dict):
                params.update(schema_name)
            else:
                params["schemaName"] = schema_name
        if table_name is not None:
            if isinstance(table_name, PyCelonisBaseModel):
                params.update(table_name.json_dict(by_alias=True))
            elif isinstance(table_name, dict):
                params.update(table_name)
            else:
                params["tableName"] = table_name
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v1/execution/factories/objects/source-preview",
            params=params,
            parse_json=True,
            type_=PreviewTransport,
            **kwargs,
        )

    @staticmethod
    def get_api_v1_execution_factories_objects_source_tables(
        client: Client, environment: Optional["str"] = None, **kwargs: Any
    ) -> ObjectFactorySourceTransport:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v1/execution/factories/objects/source-tables'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v1/execution/factories/objects/source-tables",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v1/execution/factories/objects/source-tables",
            params=params,
            parse_json=True,
            type_=ObjectFactorySourceTransport,
            **kwargs,
        )

    @staticmethod
    def get_api_v1_execution_factories_sources(
        client: Client,
        data_source_id: Optional["str"] = None,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> FactorySourceTablesTransport:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v1/execution/factories/sources'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v1/execution/factories/sources",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if data_source_id is not None:
            if isinstance(data_source_id, PyCelonisBaseModel):
                params.update(data_source_id.json_dict(by_alias=True))
            elif isinstance(data_source_id, dict):
                params.update(data_source_id)
            else:
                params["dataSourceId"] = data_source_id
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v1/execution/factories/sources",
            params=params,
            parse_json=True,
            type_=FactorySourceTablesTransport,
            **kwargs,
        )

    @staticmethod
    def get_api_v1_execution_factories_sql_data_sources(
        client: Client, environment: Optional["str"] = None, **kwargs: Any
    ) -> List[Optional[SqlFactoryDataConnection]]:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v1/execution/factories/sql/data-sources'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v1/execution/factories/sql/data-sources",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v1/execution/factories/sql/data-sources",
            params=params,
            parse_json=True,
            type_=List[Optional[SqlFactoryDataConnection]],
            **kwargs,
        )

    @staticmethod
    def post_api_v1_execution_factories_sql_dataset_preview(
        client: Client,
        request_body: SqlFactoryDataSetPreviewRequest,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> FactoryDataSetPreviewResponse:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v1/execution/factories/sql/dataset-preview'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v1/execution/factories/sql/dataset-preview",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="POST",
            url=f"/bl/api/v1/execution/factories/sql/dataset-preview",
            params=params,
            request_body=request_body,
            parse_json=True,
            type_=FactoryDataSetPreviewResponse,
            **kwargs,
        )

    @staticmethod
    def post_api_v1_execution_types_sync(
        client: Client,
        dry_run: Optional["bool"] = None,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> CreateOrUpdateBusinessGraphResponse:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v1/execution/types/sync'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v1/execution/types/sync",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if dry_run is not None:
            if isinstance(dry_run, PyCelonisBaseModel):
                params.update(dry_run.json_dict(by_alias=True))
            elif isinstance(dry_run, dict):
                params.update(dry_run)
            else:
                params["dryRun"] = dry_run
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="POST",
            url=f"/bl/api/v1/execution/types/sync",
            params=params,
            parse_json=True,
            type_=CreateOrUpdateBusinessGraphResponse,
            **kwargs,
        )

    @staticmethod
    def get_api_v1_factories(
        client: Client,
        filter_options: Optional["SqlFactoryFilterOptions"] = None,
        pagination: Optional["Pagination"] = None,
        environment: Optional["str"] = None,
        include_user_template_transformations: Optional["bool"] = None,
        **kwargs: Any,
    ) -> PageFactoryListTransport:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v1/factories'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v1/factories",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if filter_options is not None:
            if isinstance(filter_options, PyCelonisBaseModel):
                params.update(filter_options.json_dict(by_alias=True))
            elif isinstance(filter_options, dict):
                params.update(filter_options)
            else:
                params["filterOptions"] = filter_options
        if pagination is not None:
            if isinstance(pagination, PyCelonisBaseModel):
                params.update(pagination.json_dict(by_alias=True))
            elif isinstance(pagination, dict):
                params.update(pagination)
            else:
                params["pagination"] = pagination
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        if include_user_template_transformations is not None:
            if isinstance(include_user_template_transformations, PyCelonisBaseModel):
                params.update(
                    include_user_template_transformations.json_dict(by_alias=True)
                )
            elif isinstance(include_user_template_transformations, dict):
                params.update(include_user_template_transformations)
            else:
                params[
                    "includeUserTemplateTransformations"
                ] = include_user_template_transformations
        return client.request(
            method="GET",
            url=f"/bl/api/v1/factories",
            params=params,
            parse_json=True,
            type_=PageFactoryListTransport,
            **kwargs,
        )

    @staticmethod
    def get_api_v1_factories_event(
        client: Client,
        filter_options: Optional["EntityFilterOptions"] = None,
        pagination: Optional["Pagination"] = None,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> PageEventFactory:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v1/factories/event'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v1/factories/event",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if filter_options is not None:
            if isinstance(filter_options, PyCelonisBaseModel):
                params.update(filter_options.json_dict(by_alias=True))
            elif isinstance(filter_options, dict):
                params.update(filter_options)
            else:
                params["filterOptions"] = filter_options
        if pagination is not None:
            if isinstance(pagination, PyCelonisBaseModel):
                params.update(pagination.json_dict(by_alias=True))
            elif isinstance(pagination, dict):
                params.update(pagination)
            else:
                params["pagination"] = pagination
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v1/factories/event",
            params=params,
            parse_json=True,
            type_=PageEventFactory,
            **kwargs,
        )

    @staticmethod
    def post_api_v1_factories_event(
        client: Client,
        request_body: EventFactoryRequestOptions,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> EventFactory:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v1/factories/event'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v1/factories/event",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="POST",
            url=f"/bl/api/v1/factories/event",
            params=params,
            request_body=request_body,
            parse_json=True,
            type_=EventFactory,
            **kwargs,
        )

    @staticmethod
    def get_api_v1_factories_event_event_factory_id(
        client: Client,
        event_factory_id: str,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> EventFactory:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v1/factories/event/{event_factory_id}'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v1/factories/event/{event_factory_id}",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v1/factories/event/{event_factory_id}",
            params=params,
            parse_json=True,
            type_=EventFactory,
            **kwargs,
        )

    @staticmethod
    def put_api_v1_factories_event_event_factory_id(
        client: Client,
        event_factory_id: str,
        request_body: EventFactoryRequestOptions,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> EventFactory:
        logger.debug(
            f"Request: 'PUT' -> '/bl/api/v1/factories/event/{event_factory_id}'",
            extra={
                "request_type": "PUT",
                "path": "/bl/api/v1/factories/event/{event_factory_id}",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="PUT",
            url=f"/bl/api/v1/factories/event/{event_factory_id}",
            params=params,
            request_body=request_body,
            parse_json=True,
            type_=EventFactory,
            **kwargs,
        )

    @staticmethod
    def delete_api_v1_factories_event_event_factory_id(
        client: Client,
        event_factory_id: str,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> None:
        logger.debug(
            f"Request: 'DELETE' -> '/bl/api/v1/factories/event/{event_factory_id}'",
            extra={
                "request_type": "DELETE",
                "path": "/bl/api/v1/factories/event/{event_factory_id}",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="DELETE",
            url=f"/bl/api/v1/factories/event/{event_factory_id}",
            params=params,
            **kwargs,
        )

    @staticmethod
    def post_api_v1_factories_sql(
        client: Client,
        request_body: SqlFactoryRequestOptions,
        environment: Optional["str"] = None,
        use_v2_manifest: Optional["bool"] = None,
        **kwargs: Any,
    ) -> SqlFactoryTransport:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v1/factories/sql'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v1/factories/sql",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        if use_v2_manifest is not None:
            if isinstance(use_v2_manifest, PyCelonisBaseModel):
                params.update(use_v2_manifest.json_dict(by_alias=True))
            elif isinstance(use_v2_manifest, dict):
                params.update(use_v2_manifest)
            else:
                params["useV2Manifest"] = use_v2_manifest
        return client.request(
            method="POST",
            url=f"/bl/api/v1/factories/sql",
            params=params,
            request_body=request_body,
            parse_json=True,
            type_=SqlFactoryTransport,
            **kwargs,
        )

    @staticmethod
    def get_api_v1_factories_sql_celonis_factory_id(
        client: Client,
        factory_id: str,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> SqlFactoryTransport:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v1/factories/sql/celonis/{factory_id}'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v1/factories/sql/celonis/{factory_id}",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v1/factories/sql/celonis/{factory_id}",
            params=params,
            parse_json=True,
            type_=SqlFactoryTransport,
            **kwargs,
        )

    @staticmethod
    def get_api_v1_factories_sql_celonis_factory_id_data_connection_id(
        client: Client,
        factory_id: str,
        data_connection_id: str,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> SqlFactoryTransport:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v1/factories/sql/celonis/{factory_id}/{data_connection_id}'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v1/factories/sql/celonis/{factory_id}/{data_connection_id}",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v1/factories/sql/celonis/{factory_id}/{data_connection_id}",
            params=params,
            parse_json=True,
            type_=SqlFactoryTransport,
            **kwargs,
        )

    @staticmethod
    def put_api_v1_factories_sql_change_state(
        client: Client,
        request_body: SqlFactoryChangeStateManyRequest,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> List[Optional[FactoryListTransport]]:
        logger.debug(
            f"Request: 'PUT' -> '/bl/api/v1/factories/sql/change-state'",
            extra={
                "request_type": "PUT",
                "path": "/bl/api/v1/factories/sql/change-state",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="PUT",
            url=f"/bl/api/v1/factories/sql/change-state",
            params=params,
            request_body=request_body,
            parse_json=True,
            type_=List[Optional[FactoryListTransport]],
            **kwargs,
        )

    @staticmethod
    def get_api_v1_factories_sql_change_table_columns(
        client: Client, environment: Optional["str"] = None, **kwargs: Any
    ) -> List[Optional[EntityField]]:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v1/factories/sql/changeTableColumns'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v1/factories/sql/changeTableColumns",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v1/factories/sql/changeTableColumns",
            params=params,
            parse_json=True,
            type_=List[Optional[EntityField]],
            **kwargs,
        )

    @staticmethod
    def get_api_v1_factories_sql_custom_factory_id(
        client: Client,
        factory_id: str,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> SqlFactoryTransport:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v1/factories/sql/custom/{factory_id}'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v1/factories/sql/custom/{factory_id}",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v1/factories/sql/custom/{factory_id}",
            params=params,
            parse_json=True,
            type_=SqlFactoryTransport,
            **kwargs,
        )

    @staticmethod
    def get_api_v1_factories_sql_factory_id(
        client: Client,
        factory_id: str,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> SqlFactoryTransport:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v1/factories/sql/{factory_id}'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v1/factories/sql/{factory_id}",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v1/factories/sql/{factory_id}",
            params=params,
            parse_json=True,
            type_=SqlFactoryTransport,
            **kwargs,
        )

    @staticmethod
    def put_api_v1_factories_sql_factory_id(
        client: Client,
        factory_id: str,
        request_body: SqlFactoryRequestOptions,
        environment: Optional["str"] = None,
        use_v2_manifest: Optional["bool"] = None,
        **kwargs: Any,
    ) -> SqlFactoryTransport:
        logger.debug(
            f"Request: 'PUT' -> '/bl/api/v1/factories/sql/{factory_id}'",
            extra={
                "request_type": "PUT",
                "path": "/bl/api/v1/factories/sql/{factory_id}",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        if use_v2_manifest is not None:
            if isinstance(use_v2_manifest, PyCelonisBaseModel):
                params.update(use_v2_manifest.json_dict(by_alias=True))
            elif isinstance(use_v2_manifest, dict):
                params.update(use_v2_manifest)
            else:
                params["useV2Manifest"] = use_v2_manifest
        return client.request(
            method="PUT",
            url=f"/bl/api/v1/factories/sql/{factory_id}",
            params=params,
            request_body=request_body,
            parse_json=True,
            type_=SqlFactoryTransport,
            **kwargs,
        )

    @staticmethod
    def delete_api_v1_factories_sql_factory_id(
        client: Client,
        factory_id: str,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> None:
        logger.debug(
            f"Request: 'DELETE' -> '/bl/api/v1/factories/sql/{factory_id}'",
            extra={
                "request_type": "DELETE",
                "path": "/bl/api/v1/factories/sql/{factory_id}",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="DELETE",
            url=f"/bl/api/v1/factories/sql/{factory_id}",
            params=params,
            **kwargs,
        )

    @staticmethod
    def post_api_v1_factories_sql_factory_id_convert_to_template(
        client: Client,
        factory_id: str,
        request_body: ConvertSqlFactoryToTemplateRequestOptions,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> SqlFactoryTransport:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v1/factories/sql/{factory_id}/convert-to-template'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v1/factories/sql/{factory_id}/convert-to-template",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="POST",
            url=f"/bl/api/v1/factories/sql/{factory_id}/convert-to-template",
            params=params,
            request_body=request_body,
            parse_json=True,
            type_=SqlFactoryTransport,
            **kwargs,
        )

    @staticmethod
    def post_api_v1_factories_sql_factory_id_detach(
        client: Client,
        factory_id: str,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> SqlFactoryTransport:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v1/factories/sql/{factory_id}/detach'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v1/factories/sql/{factory_id}/detach",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="POST",
            url=f"/bl/api/v1/factories/sql/{factory_id}/detach",
            params=params,
            parse_json=True,
            type_=SqlFactoryTransport,
            **kwargs,
        )

    @staticmethod
    def post_api_v1_factories_sql_factory_id_duplicate(
        client: Client,
        factory_id: str,
        request_body: DuplicateSqlFactoryOptions,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> SqlFactoryTransport:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v1/factories/sql/{factory_id}/duplicate'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v1/factories/sql/{factory_id}/duplicate",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="POST",
            url=f"/bl/api/v1/factories/sql/{factory_id}/duplicate",
            params=params,
            request_body=request_body,
            parse_json=True,
            type_=SqlFactoryTransport,
            **kwargs,
        )

    @staticmethod
    def post_api_v1_factories_sql_factory_id_update_metadata(
        client: Client,
        factory_id: str,
        request_body: SqlFactoryUpdateMetadataRequestOptions,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> SqlFactoryTransport:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v1/factories/sql/{factory_id}/update-metadata'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v1/factories/sql/{factory_id}/update-metadata",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="POST",
            url=f"/bl/api/v1/factories/sql/{factory_id}/update-metadata",
            params=params,
            request_body=request_body,
            parse_json=True,
            type_=SqlFactoryTransport,
            **kwargs,
        )

    @staticmethod
    def get_api_v1_landscape_layout(
        client: Client, environment: Optional["str"] = None, **kwargs: Any
    ) -> BusinessLandscapeLayout:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v1/landscape/layout'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v1/landscape/layout",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v1/landscape/layout",
            params=params,
            parse_json=True,
            type_=BusinessLandscapeLayout,
            **kwargs,
        )

    @staticmethod
    def put_api_v1_landscape_layout(
        client: Client,
        request_body: BusinessLandscapeLayoutOptions,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> BusinessLandscapeLayout:
        logger.debug(
            f"Request: 'PUT' -> '/bl/api/v1/landscape/layout'",
            extra={
                "request_type": "PUT",
                "path": "/bl/api/v1/landscape/layout",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="PUT",
            url=f"/bl/api/v1/landscape/layout",
            params=params,
            request_body=request_body,
            parse_json=True,
            type_=BusinessLandscapeLayout,
            **kwargs,
        )

    @staticmethod
    def post_api_v1_landscape_layout(
        client: Client,
        request_body: BusinessLandscapeLayoutOptions,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> BusinessLandscapeLayout:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v1/landscape/layout'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v1/landscape/layout",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="POST",
            url=f"/bl/api/v1/landscape/layout",
            params=params,
            request_body=request_body,
            parse_json=True,
            type_=BusinessLandscapeLayout,
            **kwargs,
        )

    @staticmethod
    def get_api_v1_perspectives(
        client: Client,
        filter_options: Optional["PerspectiveFilterOptions"] = None,
        pagination: Optional["Pagination"] = None,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> PagePerspective:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v1/perspectives'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v1/perspectives",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if filter_options is not None:
            if isinstance(filter_options, PyCelonisBaseModel):
                params.update(filter_options.json_dict(by_alias=True))
            elif isinstance(filter_options, dict):
                params.update(filter_options)
            else:
                params["filterOptions"] = filter_options
        if pagination is not None:
            if isinstance(pagination, PyCelonisBaseModel):
                params.update(pagination.json_dict(by_alias=True))
            elif isinstance(pagination, dict):
                params.update(pagination)
            else:
                params["pagination"] = pagination
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v1/perspectives",
            params=params,
            parse_json=True,
            type_=PagePerspective,
            **kwargs,
        )

    @staticmethod
    def post_api_v1_perspectives(
        client: Client,
        request_body: PerspectiveRequestOptions,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> Perspective:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v1/perspectives'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v1/perspectives",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="POST",
            url=f"/bl/api/v1/perspectives",
            params=params,
            request_body=request_body,
            parse_json=True,
            type_=Perspective,
            **kwargs,
        )

    @staticmethod
    def get_api_v1_perspectives_perspective_id(
        client: Client,
        perspective_id: str,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> Perspective:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v1/perspectives/{perspective_id}'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v1/perspectives/{perspective_id}",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v1/perspectives/{perspective_id}",
            params=params,
            parse_json=True,
            type_=Perspective,
            **kwargs,
        )

    @staticmethod
    def put_api_v1_perspectives_perspective_id(
        client: Client,
        perspective_id: str,
        request_body: PerspectiveRequestOptions,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> Perspective:
        logger.debug(
            f"Request: 'PUT' -> '/bl/api/v1/perspectives/{perspective_id}'",
            extra={
                "request_type": "PUT",
                "path": "/bl/api/v1/perspectives/{perspective_id}",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="PUT",
            url=f"/bl/api/v1/perspectives/{perspective_id}",
            params=params,
            request_body=request_body,
            parse_json=True,
            type_=Perspective,
            **kwargs,
        )

    @staticmethod
    def delete_api_v1_perspectives_perspective_id(
        client: Client,
        perspective_id: str,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> None:
        logger.debug(
            f"Request: 'DELETE' -> '/bl/api/v1/perspectives/{perspective_id}'",
            extra={
                "request_type": "DELETE",
                "path": "/bl/api/v1/perspectives/{perspective_id}",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="DELETE",
            url=f"/bl/api/v1/perspectives/{perspective_id}",
            params=params,
            **kwargs,
        )

    @staticmethod
    def get_api_v1_processes(
        client: Client,
        pagination: Optional["Pagination"] = None,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> PageProcess:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v1/processes'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v1/processes",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if pagination is not None:
            if isinstance(pagination, PyCelonisBaseModel):
                params.update(pagination.json_dict(by_alias=True))
            elif isinstance(pagination, dict):
                params.update(pagination)
            else:
                params["pagination"] = pagination
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v1/processes",
            params=params,
            parse_json=True,
            type_=PageProcess,
            **kwargs,
        )

    @staticmethod
    def post_api_v1_processes(
        client: Client,
        request_body: ProcessCreateOptions,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> Process:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v1/processes'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v1/processes",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="POST",
            url=f"/bl/api/v1/processes",
            params=params,
            request_body=request_body,
            parse_json=True,
            type_=Process,
            **kwargs,
        )

    @staticmethod
    def get_api_v1_processes_transformation_types(
        client: Client, environment: Optional["str"] = None, **kwargs: Any
    ) -> List[Optional[DataSourceTransformationType]]:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v1/processes/transformation-types'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v1/processes/transformation-types",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v1/processes/transformation-types",
            params=params,
            parse_json=True,
            type_=List[Optional[DataSourceTransformationType]],
            **kwargs,
        )

    @staticmethod
    def get_api_v1_processes_process_name(
        client: Client,
        process_name: str,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> Process:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v1/processes/{process_name}'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v1/processes/{process_name}",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v1/processes/{process_name}",
            params=params,
            parse_json=True,
            type_=Process,
            **kwargs,
        )

    @staticmethod
    def put_api_v1_processes_process_name(
        client: Client,
        process_name: str,
        request_body: ProcessUpdateOptions,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> Process:
        logger.debug(
            f"Request: 'PUT' -> '/bl/api/v1/processes/{process_name}'",
            extra={
                "request_type": "PUT",
                "path": "/bl/api/v1/processes/{process_name}",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="PUT",
            url=f"/bl/api/v1/processes/{process_name}",
            params=params,
            request_body=request_body,
            parse_json=True,
            type_=Process,
            **kwargs,
        )

    @staticmethod
    def delete_api_v1_processes_process_name(
        client: Client,
        process_name: str,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> None:
        logger.debug(
            f"Request: 'DELETE' -> '/bl/api/v1/processes/{process_name}'",
            extra={
                "request_type": "DELETE",
                "path": "/bl/api/v1/processes/{process_name}",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="DELETE",
            url=f"/bl/api/v1/processes/{process_name}",
            params=params,
            **kwargs,
        )

    @staticmethod
    def post_api_v1_processes_process_name_disable(
        client: Client,
        process_name: str,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> Process:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v1/processes/{process_name}/disable'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v1/processes/{process_name}/disable",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="POST",
            url=f"/bl/api/v1/processes/{process_name}/disable",
            params=params,
            parse_json=True,
            type_=Process,
            **kwargs,
        )

    @staticmethod
    def post_api_v1_processes_process_name_enable(
        client: Client,
        process_name: str,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> Process:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v1/processes/{process_name}/enable'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v1/processes/{process_name}/enable",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="POST",
            url=f"/bl/api/v1/processes/{process_name}/enable",
            params=params,
            parse_json=True,
            type_=Process,
            **kwargs,
        )

    @staticmethod
    def get_api_v1_tags(
        client: Client, environment: Optional["str"] = None, **kwargs: Any
    ) -> List[Optional[str]]:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v1/tags'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v1/tags",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v1/tags",
            params=params,
            parse_json=True,
            type_=List[Optional[str]],
            **kwargs,
        )

    @staticmethod
    def get_api_v1_types_events(
        client: Client,
        filter_options: Optional["EntityFilterOptions"] = None,
        pagination: Optional["Pagination"] = None,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> PageEventEntity:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v1/types/events'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v1/types/events",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if filter_options is not None:
            if isinstance(filter_options, PyCelonisBaseModel):
                params.update(filter_options.json_dict(by_alias=True))
            elif isinstance(filter_options, dict):
                params.update(filter_options)
            else:
                params["filterOptions"] = filter_options
        if pagination is not None:
            if isinstance(pagination, PyCelonisBaseModel):
                params.update(pagination.json_dict(by_alias=True))
            elif isinstance(pagination, dict):
                params.update(pagination)
            else:
                params["pagination"] = pagination
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v1/types/events",
            params=params,
            parse_json=True,
            type_=PageEventEntity,
            **kwargs,
        )

    @staticmethod
    def post_api_v1_types_events(
        client: Client,
        request_body: EventEntityRequestOptions,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> EventEntity:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v1/types/events'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v1/types/events",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="POST",
            url=f"/bl/api/v1/types/events",
            params=params,
            request_body=request_body,
            parse_json=True,
            type_=EventEntity,
            **kwargs,
        )

    @staticmethod
    def get_api_v1_types_events_event_type_id(
        client: Client,
        event_type_id: str,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> EventEntity:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v1/types/events/{event_type_id}'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v1/types/events/{event_type_id}",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v1/types/events/{event_type_id}",
            params=params,
            parse_json=True,
            type_=EventEntity,
            **kwargs,
        )

    @staticmethod
    def put_api_v1_types_events_event_type_id(
        client: Client,
        event_type_id: str,
        request_body: EventEntityRequestOptions,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> EventEntity:
        logger.debug(
            f"Request: 'PUT' -> '/bl/api/v1/types/events/{event_type_id}'",
            extra={
                "request_type": "PUT",
                "path": "/bl/api/v1/types/events/{event_type_id}",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="PUT",
            url=f"/bl/api/v1/types/events/{event_type_id}",
            params=params,
            request_body=request_body,
            parse_json=True,
            type_=EventEntity,
            **kwargs,
        )

    @staticmethod
    def delete_api_v1_types_events_event_type_id(
        client: Client,
        event_type_id: str,
        force: Optional["bool"] = None,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> None:
        logger.debug(
            f"Request: 'DELETE' -> '/bl/api/v1/types/events/{event_type_id}'",
            extra={
                "request_type": "DELETE",
                "path": "/bl/api/v1/types/events/{event_type_id}",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if force is not None:
            if isinstance(force, PyCelonisBaseModel):
                params.update(force.json_dict(by_alias=True))
            elif isinstance(force, dict):
                params.update(force)
            else:
                params["force"] = force
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="DELETE",
            url=f"/bl/api/v1/types/events/{event_type_id}",
            params=params,
            **kwargs,
        )

    @staticmethod
    def get_api_v1_types_global_sync(
        client: Client,
        content_tag: Optional["str"] = None,
        force: Optional["bool"] = None,
        **kwargs: Any,
    ) -> None:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v1/types/global/sync'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v1/types/global/sync",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if content_tag is not None:
            if isinstance(content_tag, PyCelonisBaseModel):
                params.update(content_tag.json_dict(by_alias=True))
            elif isinstance(content_tag, dict):
                params.update(content_tag)
            else:
                params["contentTag"] = content_tag
        if force is not None:
            if isinstance(force, PyCelonisBaseModel):
                params.update(force.json_dict(by_alias=True))
            elif isinstance(force, dict):
                params.update(force)
            else:
                params["force"] = force
        return client.request(
            method="GET", url=f"/bl/api/v1/types/global/sync", params=params, **kwargs
        )

    @staticmethod
    def get_api_v1_types_objects(
        client: Client,
        filter_options: Optional["EntityFilterOptions"] = None,
        pagination: Optional["Pagination"] = None,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> PageObjectEntity:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v1/types/objects'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v1/types/objects",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if filter_options is not None:
            if isinstance(filter_options, PyCelonisBaseModel):
                params.update(filter_options.json_dict(by_alias=True))
            elif isinstance(filter_options, dict):
                params.update(filter_options)
            else:
                params["filterOptions"] = filter_options
        if pagination is not None:
            if isinstance(pagination, PyCelonisBaseModel):
                params.update(pagination.json_dict(by_alias=True))
            elif isinstance(pagination, dict):
                params.update(pagination)
            else:
                params["pagination"] = pagination
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v1/types/objects",
            params=params,
            parse_json=True,
            type_=PageObjectEntity,
            **kwargs,
        )

    @staticmethod
    def post_api_v1_types_objects(
        client: Client,
        request_body: ObjectEntityRequestOptions,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> ObjectEntity:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v1/types/objects'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v1/types/objects",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="POST",
            url=f"/bl/api/v1/types/objects",
            params=params,
            request_body=request_body,
            parse_json=True,
            type_=ObjectEntity,
            **kwargs,
        )

    @staticmethod
    def post_api_v1_types_objects_relationships(
        client: Client,
        request_body: ObjectRelationshipRequestOptions,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> ObjectRelationship:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v1/types/objects/relationships'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v1/types/objects/relationships",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="POST",
            url=f"/bl/api/v1/types/objects/relationships",
            params=params,
            request_body=request_body,
            parse_json=True,
            type_=ObjectRelationship,
            **kwargs,
        )

    @staticmethod
    def get_api_v1_types_objects_object_type_id(
        client: Client,
        object_type_id: str,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> ObjectEntity:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v1/types/objects/{object_type_id}'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v1/types/objects/{object_type_id}",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v1/types/objects/{object_type_id}",
            params=params,
            parse_json=True,
            type_=ObjectEntity,
            **kwargs,
        )

    @staticmethod
    def put_api_v1_types_objects_object_type_id(
        client: Client,
        object_type_id: str,
        request_body: ObjectEntityRequestOptions,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> ObjectEntity:
        logger.debug(
            f"Request: 'PUT' -> '/bl/api/v1/types/objects/{object_type_id}'",
            extra={
                "request_type": "PUT",
                "path": "/bl/api/v1/types/objects/{object_type_id}",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="PUT",
            url=f"/bl/api/v1/types/objects/{object_type_id}",
            params=params,
            request_body=request_body,
            parse_json=True,
            type_=ObjectEntity,
            **kwargs,
        )

    @staticmethod
    def delete_api_v1_types_objects_object_type_id(
        client: Client,
        object_type_id: str,
        force: Optional["bool"] = None,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> None:
        logger.debug(
            f"Request: 'DELETE' -> '/bl/api/v1/types/objects/{object_type_id}'",
            extra={
                "request_type": "DELETE",
                "path": "/bl/api/v1/types/objects/{object_type_id}",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if force is not None:
            if isinstance(force, PyCelonisBaseModel):
                params.update(force.json_dict(by_alias=True))
            elif isinstance(force, dict):
                params.update(force)
            else:
                params["force"] = force
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="DELETE",
            url=f"/bl/api/v1/types/objects/{object_type_id}",
            params=params,
            **kwargs,
        )

    @staticmethod
    def get_api_v1_types_objects_object_type_id_relationships(
        client: Client,
        object_type_id: str,
        pagination: Optional["Pagination"] = None,
        filter_bidirectional: Optional["bool"] = None,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> PageObjectRelationship:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v1/types/objects/{object_type_id}/relationships'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v1/types/objects/{object_type_id}/relationships",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if pagination is not None:
            if isinstance(pagination, PyCelonisBaseModel):
                params.update(pagination.json_dict(by_alias=True))
            elif isinstance(pagination, dict):
                params.update(pagination)
            else:
                params["pagination"] = pagination
        if filter_bidirectional is not None:
            if isinstance(filter_bidirectional, PyCelonisBaseModel):
                params.update(filter_bidirectional.json_dict(by_alias=True))
            elif isinstance(filter_bidirectional, dict):
                params.update(filter_bidirectional)
            else:
                params["filterBidirectional"] = filter_bidirectional
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v1/types/objects/{object_type_id}/relationships",
            params=params,
            parse_json=True,
            type_=PageObjectRelationship,
            **kwargs,
        )

    @staticmethod
    def get_api_v1_types_objects_object_type_id_relationships_incoming(
        client: Client,
        object_type_id: str,
        pagination: Optional["Pagination"] = None,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> PageObjectRelationship:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v1/types/objects/{object_type_id}/relationships/incoming'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v1/types/objects/{object_type_id}/relationships/incoming",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if pagination is not None:
            if isinstance(pagination, PyCelonisBaseModel):
                params.update(pagination.json_dict(by_alias=True))
            elif isinstance(pagination, dict):
                params.update(pagination)
            else:
                params["pagination"] = pagination
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v1/types/objects/{object_type_id}/relationships/incoming",
            params=params,
            parse_json=True,
            type_=PageObjectRelationship,
            **kwargs,
        )

    @staticmethod
    def get_api_v1_types_objects_object_type_id_relationships_outgoing(
        client: Client,
        object_type_id: str,
        pagination: Optional["Pagination"] = None,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> PageObjectRelationship:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v1/types/objects/{object_type_id}/relationships/outgoing'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v1/types/objects/{object_type_id}/relationships/outgoing",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if pagination is not None:
            if isinstance(pagination, PyCelonisBaseModel):
                params.update(pagination.json_dict(by_alias=True))
            elif isinstance(pagination, dict):
                params.update(pagination)
            else:
                params["pagination"] = pagination
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v1/types/objects/{object_type_id}/relationships/outgoing",
            params=params,
            parse_json=True,
            type_=PageObjectRelationship,
            **kwargs,
        )

    @staticmethod
    def delete_api_v1_types_objects_object_type_id_relationships_target_type_id(
        client: Client,
        object_type_id: str,
        target_type_id: str,
        relationship: Optional["str"] = None,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> None:
        logger.debug(
            f"Request: 'DELETE' -> '/bl/api/v1/types/objects/{object_type_id}/relationships/{target_type_id}'",
            extra={
                "request_type": "DELETE",
                "path": "/bl/api/v1/types/objects/{object_type_id}/relationships/{target_type_id}",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if relationship is not None:
            if isinstance(relationship, PyCelonisBaseModel):
                params.update(relationship.json_dict(by_alias=True))
            elif isinstance(relationship, dict):
                params.update(relationship)
            else:
                params["relationship"] = relationship
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="DELETE",
            url=f"/bl/api/v1/types/objects/{object_type_id}/relationships/{target_type_id}",
            params=params,
            **kwargs,
        )

    @staticmethod
    def get_api_v1_workspaces_usages_count(
        client: Client, pagination: Optional["Pagination"] = None, **kwargs: Any
    ) -> PageWorkspaceUsage:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v1/workspaces/usages/count'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v1/workspaces/usages/count",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if pagination is not None:
            if isinstance(pagination, PyCelonisBaseModel):
                params.update(pagination.json_dict(by_alias=True))
            elif isinstance(pagination, dict):
                params.update(pagination)
            else:
                params["pagination"] = pagination
        return client.request(
            method="GET",
            url=f"/bl/api/v1/workspaces/usages/count",
            params=params,
            parse_json=True,
            type_=PageWorkspaceUsage,
            **kwargs,
        )

    @staticmethod
    def get_api_v1_workspaces_usages_last(
        client: Client, pagination: Optional["Pagination"] = None, **kwargs: Any
    ) -> PageWorkspaceUsage:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v1/workspaces/usages/last'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v1/workspaces/usages/last",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if pagination is not None:
            if isinstance(pagination, PyCelonisBaseModel):
                params.update(pagination.json_dict(by_alias=True))
            elif isinstance(pagination, dict):
                params.update(pagination)
            else:
                params["pagination"] = pagination
        return client.request(
            method="GET",
            url=f"/bl/api/v1/workspaces/usages/last",
            params=params,
            parse_json=True,
            type_=PageWorkspaceUsage,
            **kwargs,
        )

    @staticmethod
    def put_api_v1_workspaces_usages_workspace_id(
        client: Client, workspace_id: str, **kwargs: Any
    ) -> WorkspaceUsage:
        logger.debug(
            f"Request: 'PUT' -> '/bl/api/v1/workspaces/usages/{workspace_id}'",
            extra={
                "request_type": "PUT",
                "path": "/bl/api/v1/workspaces/usages/{workspace_id}",
                "tracking_type": "API_REQUEST",
            },
        )

        return client.request(
            method="PUT",
            url=f"/bl/api/v1/workspaces/usages/{workspace_id}",
            parse_json=True,
            type_=WorkspaceUsage,
            **kwargs,
        )

    @staticmethod
    def get_api_v1_workspaces_workspace_id_categories(
        client: Client,
        workspace_id: str,
        pagination: Optional["Pagination"] = None,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> PageCategory:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v1/workspaces/{workspace_id}/categories'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v1/workspaces/{workspace_id}/categories",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if pagination is not None:
            if isinstance(pagination, PyCelonisBaseModel):
                params.update(pagination.json_dict(by_alias=True))
            elif isinstance(pagination, dict):
                params.update(pagination)
            else:
                params["pagination"] = pagination
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v1/workspaces/{workspace_id}/categories",
            params=params,
            parse_json=True,
            type_=PageCategory,
            **kwargs,
        )

    @staticmethod
    def post_api_v1_workspaces_workspace_id_categories(
        client: Client,
        workspace_id: str,
        request_body: CategoryRequestOptions,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> Category:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v1/workspaces/{workspace_id}/categories'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v1/workspaces/{workspace_id}/categories",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="POST",
            url=f"/bl/api/v1/workspaces/{workspace_id}/categories",
            params=params,
            request_body=request_body,
            parse_json=True,
            type_=Category,
            **kwargs,
        )

    @staticmethod
    def get_api_v1_workspaces_workspace_id_categories_category_id(
        client: Client,
        workspace_id: str,
        category_id: str,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> Category:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v1/workspaces/{workspace_id}/categories/{category_id}'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v1/workspaces/{workspace_id}/categories/{category_id}",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v1/workspaces/{workspace_id}/categories/{category_id}",
            params=params,
            parse_json=True,
            type_=Category,
            **kwargs,
        )

    @staticmethod
    def put_api_v1_workspaces_workspace_id_categories_category_id(
        client: Client,
        workspace_id: str,
        category_id: str,
        request_body: CategoryRequestOptions,
        environment: Optional["str"] = None,
        force_delete_removed_values: Optional["bool"] = None,
        **kwargs: Any,
    ) -> Category:
        logger.debug(
            f"Request: 'PUT' -> '/bl/api/v1/workspaces/{workspace_id}/categories/{category_id}'",
            extra={
                "request_type": "PUT",
                "path": "/bl/api/v1/workspaces/{workspace_id}/categories/{category_id}",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        if force_delete_removed_values is not None:
            if isinstance(force_delete_removed_values, PyCelonisBaseModel):
                params.update(force_delete_removed_values.json_dict(by_alias=True))
            elif isinstance(force_delete_removed_values, dict):
                params.update(force_delete_removed_values)
            else:
                params["forceDeleteRemovedValues"] = force_delete_removed_values
        return client.request(
            method="PUT",
            url=f"/bl/api/v1/workspaces/{workspace_id}/categories/{category_id}",
            params=params,
            request_body=request_body,
            parse_json=True,
            type_=Category,
            **kwargs,
        )

    @staticmethod
    def delete_api_v1_workspaces_workspace_id_categories_category_id(
        client: Client,
        workspace_id: str,
        category_id: str,
        environment: Optional["str"] = None,
        force_delete_category: Optional["bool"] = None,
        **kwargs: Any,
    ) -> None:
        logger.debug(
            f"Request: 'DELETE' -> '/bl/api/v1/workspaces/{workspace_id}/categories/{category_id}'",
            extra={
                "request_type": "DELETE",
                "path": "/bl/api/v1/workspaces/{workspace_id}/categories/{category_id}",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        if force_delete_category is not None:
            if isinstance(force_delete_category, PyCelonisBaseModel):
                params.update(force_delete_category.json_dict(by_alias=True))
            elif isinstance(force_delete_category, dict):
                params.update(force_delete_category)
            else:
                params["forceDeleteCategory"] = force_delete_category
        return client.request(
            method="DELETE",
            url=f"/bl/api/v1/workspaces/{workspace_id}/categories/{category_id}",
            params=params,
            **kwargs,
        )

    @staticmethod
    def get_api_v1_workspaces_workspace_id_execution_history_latest(
        client: Client,
        workspace_id: str,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> List[Optional[ExecutionHistoryTransport]]:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v1/workspaces/{workspace_id}/execution-history/latest'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v1/workspaces/{workspace_id}/execution-history/latest",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v1/workspaces/{workspace_id}/execution-history/latest",
            params=params,
            parse_json=True,
            type_=List[Optional[ExecutionHistoryTransport]],
            **kwargs,
        )

    @staticmethod
    def get_api_v1_workspaces_workspace_id_factories_parameters(
        client: Client,
        workspace_id: str,
        filter_options: Optional["GlobalParameterFilterOptions"] = None,
        pagination: Optional["Pagination"] = None,
        **kwargs: Any,
    ) -> PageGlobalParameter:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v1/workspaces/{workspace_id}/factories/parameters'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v1/workspaces/{workspace_id}/factories/parameters",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if filter_options is not None:
            if isinstance(filter_options, PyCelonisBaseModel):
                params.update(filter_options.json_dict(by_alias=True))
            elif isinstance(filter_options, dict):
                params.update(filter_options)
            else:
                params["filterOptions"] = filter_options
        if pagination is not None:
            if isinstance(pagination, PyCelonisBaseModel):
                params.update(pagination.json_dict(by_alias=True))
            elif isinstance(pagination, dict):
                params.update(pagination)
            else:
                params["pagination"] = pagination
        return client.request(
            method="GET",
            url=f"/bl/api/v1/workspaces/{workspace_id}/factories/parameters",
            params=params,
            parse_json=True,
            type_=PageGlobalParameter,
            **kwargs,
        )

    @staticmethod
    def post_api_v1_workspaces_workspace_id_factories_parameters(
        client: Client,
        workspace_id: str,
        request_body: GlobalParameterCreateOptions,
        **kwargs: Any,
    ) -> GlobalParameter:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v1/workspaces/{workspace_id}/factories/parameters'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v1/workspaces/{workspace_id}/factories/parameters",
                "tracking_type": "API_REQUEST",
            },
        )

        return client.request(
            method="POST",
            url=f"/bl/api/v1/workspaces/{workspace_id}/factories/parameters",
            request_body=request_body,
            parse_json=True,
            type_=GlobalParameter,
            **kwargs,
        )

    @staticmethod
    def get_api_v1_workspaces_workspace_id_factories_parameters_parameter_id(
        client: Client, workspace_id: str, parameter_id: str, **kwargs: Any
    ) -> GlobalParameter:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v1/workspaces/{workspace_id}/factories/parameters/{parameter_id}'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v1/workspaces/{workspace_id}/factories/parameters/{parameter_id}",
                "tracking_type": "API_REQUEST",
            },
        )

        return client.request(
            method="GET",
            url=f"/bl/api/v1/workspaces/{workspace_id}/factories/parameters/{parameter_id}",
            parse_json=True,
            type_=GlobalParameter,
            **kwargs,
        )

    @staticmethod
    def put_api_v1_workspaces_workspace_id_factories_parameters_parameter_id(
        client: Client,
        workspace_id: str,
        parameter_id: str,
        request_body: GlobalParameterUpdateOptions,
        **kwargs: Any,
    ) -> None:
        logger.debug(
            f"Request: 'PUT' -> '/bl/api/v1/workspaces/{workspace_id}/factories/parameters/{parameter_id}'",
            extra={
                "request_type": "PUT",
                "path": "/bl/api/v1/workspaces/{workspace_id}/factories/parameters/{parameter_id}",
                "tracking_type": "API_REQUEST",
            },
        )

        return client.request(
            method="PUT",
            url=f"/bl/api/v1/workspaces/{workspace_id}/factories/parameters/{parameter_id}",
            request_body=request_body,
            **kwargs,
        )

    @staticmethod
    def delete_api_v1_workspaces_workspace_id_factories_parameters_parameter_id(
        client: Client, workspace_id: str, parameter_id: str, **kwargs: Any
    ) -> None:
        logger.debug(
            f"Request: 'DELETE' -> '/bl/api/v1/workspaces/{workspace_id}/factories/parameters/{parameter_id}'",
            extra={
                "request_type": "DELETE",
                "path": "/bl/api/v1/workspaces/{workspace_id}/factories/parameters/{parameter_id}",
                "tracking_type": "API_REQUEST",
            },
        )

        return client.request(
            method="DELETE",
            url=f"/bl/api/v1/workspaces/{workspace_id}/factories/parameters/{parameter_id}",
            **kwargs,
        )

    @staticmethod
    def get_api_v1_workspaces_workspace_id_filters_namespaces(
        client: Client,
        workspace_id: str,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> List[Optional[str]]:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v1/workspaces/{workspace_id}/filters/namespaces'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v1/workspaces/{workspace_id}/filters/namespaces",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v1/workspaces/{workspace_id}/filters/namespaces",
            params=params,
            parse_json=True,
            type_=List[Optional[str]],
            **kwargs,
        )

    @staticmethod
    def get_api_v1_workspaces_workspace_id_health_tasks(
        client: Client,
        workspace_id: str,
        filter_options: Optional["TaskEntityFilterOptions"] = None,
        pagination: Optional["Pagination"] = None,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> PageTaskGroupReport:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v1/workspaces/{workspace_id}/health/tasks'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v1/workspaces/{workspace_id}/health/tasks",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if filter_options is not None:
            if isinstance(filter_options, PyCelonisBaseModel):
                params.update(filter_options.json_dict(by_alias=True))
            elif isinstance(filter_options, dict):
                params.update(filter_options)
            else:
                params["filterOptions"] = filter_options
        if pagination is not None:
            if isinstance(pagination, PyCelonisBaseModel):
                params.update(pagination.json_dict(by_alias=True))
            elif isinstance(pagination, dict):
                params.update(pagination)
            else:
                params["pagination"] = pagination
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v1/workspaces/{workspace_id}/health/tasks",
            params=params,
            parse_json=True,
            type_=PageTaskGroupReport,
            **kwargs,
        )

    @staticmethod
    def post_api_v2_execution_factories_sql_dataset_preview(
        client: Client,
        request_body: SqlFactoryDataSetPreviewRequest,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> FactoryDataSetPreviewResponse:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v2/execution/factories/sql/dataset-preview'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v2/execution/factories/sql/dataset-preview",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="POST",
            url=f"/bl/api/v2/execution/factories/sql/dataset-preview",
            params=params,
            request_body=request_body,
            parse_json=True,
            type_=FactoryDataSetPreviewResponse,
            **kwargs,
        )

    @staticmethod
    def post_api_v2_execution_types_sync(
        client: Client,
        environment: Optional["str"] = None,
        include_user_template_transformations: Optional["bool"] = None,
        use_v2_manifest: Optional["bool"] = None,
        **kwargs: Any,
    ) -> CreateOrUpdateBusinessGraphResponse:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v2/execution/types/sync'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v2/execution/types/sync",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        if include_user_template_transformations is not None:
            if isinstance(include_user_template_transformations, PyCelonisBaseModel):
                params.update(
                    include_user_template_transformations.json_dict(by_alias=True)
                )
            elif isinstance(include_user_template_transformations, dict):
                params.update(include_user_template_transformations)
            else:
                params[
                    "includeUserTemplateTransformations"
                ] = include_user_template_transformations
        if use_v2_manifest is not None:
            if isinstance(use_v2_manifest, PyCelonisBaseModel):
                params.update(use_v2_manifest.json_dict(by_alias=True))
            elif isinstance(use_v2_manifest, dict):
                params.update(use_v2_manifest)
            else:
                params["useV2Manifest"] = use_v2_manifest
        return client.request(
            method="POST",
            url=f"/bl/api/v2/execution/types/sync",
            params=params,
            parse_json=True,
            type_=CreateOrUpdateBusinessGraphResponse,
            **kwargs,
        )

    @staticmethod
    def get_api_v2_workspaces_workspace_id_environments(
        client: Client, workspace_id: str, **kwargs: Any
    ) -> List[Optional[Environment]]:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v2/workspaces/{workspace_id}/environments'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v2/workspaces/{workspace_id}/environments",
                "tracking_type": "API_REQUEST",
            },
        )

        return client.request(
            method="GET",
            url=f"/bl/api/v2/workspaces/{workspace_id}/environments",
            parse_json=True,
            type_=List[Optional[Environment]],
            **kwargs,
        )

    @staticmethod
    def post_api_v2_workspaces_workspace_id_environments(
        client: Client,
        workspace_id: str,
        request_body: EnvironmentRequestOptions,
        **kwargs: Any,
    ) -> Environment:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v2/workspaces/{workspace_id}/environments'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v2/workspaces/{workspace_id}/environments",
                "tracking_type": "API_REQUEST",
            },
        )

        return client.request(
            method="POST",
            url=f"/bl/api/v2/workspaces/{workspace_id}/environments",
            request_body=request_body,
            parse_json=True,
            type_=Environment,
            **kwargs,
        )

    @staticmethod
    def post_api_v2_workspaces_workspace_id_environments_init(
        client: Client, workspace_id: str, **kwargs: Any
    ) -> None:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v2/workspaces/{workspace_id}/environments/init'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v2/workspaces/{workspace_id}/environments/init",
                "tracking_type": "API_REQUEST",
            },
        )

        return client.request(
            method="POST",
            url=f"/bl/api/v2/workspaces/{workspace_id}/environments/init",
            **kwargs,
        )

    @staticmethod
    def post_api_v2_workspaces_workspace_id_environments_promote(
        client: Client,
        workspace_id: str,
        environment: Optional["str"] = None,
        target_environment: Optional["str"] = None,
        include_user_template_transformations: Optional["bool"] = None,
        use_v2_manifest: Optional["bool"] = None,
        **kwargs: Any,
    ) -> None:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v2/workspaces/{workspace_id}/environments/promote'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v2/workspaces/{workspace_id}/environments/promote",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        if target_environment is not None:
            if isinstance(target_environment, PyCelonisBaseModel):
                params.update(target_environment.json_dict(by_alias=True))
            elif isinstance(target_environment, dict):
                params.update(target_environment)
            else:
                params["targetEnvironment"] = target_environment
        if include_user_template_transformations is not None:
            if isinstance(include_user_template_transformations, PyCelonisBaseModel):
                params.update(
                    include_user_template_transformations.json_dict(by_alias=True)
                )
            elif isinstance(include_user_template_transformations, dict):
                params.update(include_user_template_transformations)
            else:
                params[
                    "includeUserTemplateTransformations"
                ] = include_user_template_transformations
        if use_v2_manifest is not None:
            if isinstance(use_v2_manifest, PyCelonisBaseModel):
                params.update(use_v2_manifest.json_dict(by_alias=True))
            elif isinstance(use_v2_manifest, dict):
                params.update(use_v2_manifest)
            else:
                params["useV2Manifest"] = use_v2_manifest
        return client.request(
            method="POST",
            url=f"/bl/api/v2/workspaces/{workspace_id}/environments/promote",
            params=params,
            **kwargs,
        )

    @staticmethod
    def get_api_v2_workspaces_workspace_id_environments_environment_id(
        client: Client, workspace_id: str, environment_id: str, **kwargs: Any
    ) -> Environment:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v2/workspaces/{workspace_id}/environments/{environment_id}'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v2/workspaces/{workspace_id}/environments/{environment_id}",
                "tracking_type": "API_REQUEST",
            },
        )

        return client.request(
            method="GET",
            url=f"/bl/api/v2/workspaces/{workspace_id}/environments/{environment_id}",
            parse_json=True,
            type_=Environment,
            **kwargs,
        )

    @staticmethod
    def put_api_v2_workspaces_workspace_id_environments_environment_id(
        client: Client,
        workspace_id: str,
        environment_id: str,
        request_body: EnvironmentRequestOptions,
        **kwargs: Any,
    ) -> Environment:
        logger.debug(
            f"Request: 'PUT' -> '/bl/api/v2/workspaces/{workspace_id}/environments/{environment_id}'",
            extra={
                "request_type": "PUT",
                "path": "/bl/api/v2/workspaces/{workspace_id}/environments/{environment_id}",
                "tracking_type": "API_REQUEST",
            },
        )

        return client.request(
            method="PUT",
            url=f"/bl/api/v2/workspaces/{workspace_id}/environments/{environment_id}",
            request_body=request_body,
            parse_json=True,
            type_=Environment,
            **kwargs,
        )

    @staticmethod
    def delete_api_v2_workspaces_workspace_id_environments_environment_id(
        client: Client, workspace_id: str, environment_id: str, **kwargs: Any
    ) -> None:
        logger.debug(
            f"Request: 'DELETE' -> '/bl/api/v2/workspaces/{workspace_id}/environments/{environment_id}'",
            extra={
                "request_type": "DELETE",
                "path": "/bl/api/v2/workspaces/{workspace_id}/environments/{environment_id}",
                "tracking_type": "API_REQUEST",
            },
        )

        return client.request(
            method="DELETE",
            url=f"/bl/api/v2/workspaces/{workspace_id}/environments/{environment_id}",
            **kwargs,
        )

    @staticmethod
    def get_api_v2_workspaces_workspace_id_execution_factories_data_source_tables(
        client: Client,
        workspace_id: str,
        data_source_id: Optional["str"] = None,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> List[Optional[TableDefinitionTransport]]:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v2/workspaces/{workspace_id}/execution/factories/data-source-tables'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v2/workspaces/{workspace_id}/execution/factories/data-source-tables",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if data_source_id is not None:
            if isinstance(data_source_id, PyCelonisBaseModel):
                params.update(data_source_id.json_dict(by_alias=True))
            elif isinstance(data_source_id, dict):
                params.update(data_source_id)
            else:
                params["dataSourceId"] = data_source_id
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v2/workspaces/{workspace_id}/execution/factories/data-source-tables",
            params=params,
            parse_json=True,
            type_=List[Optional[TableDefinitionTransport]],
            **kwargs,
        )

    @staticmethod
    def get_api_v2_workspaces_workspace_id_execution_factories_data_sources(
        client: Client,
        workspace_id: str,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> List[Optional[FactoryDataSourceTransport]]:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v2/workspaces/{workspace_id}/execution/factories/data-sources'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v2/workspaces/{workspace_id}/execution/factories/data-sources",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v2/workspaces/{workspace_id}/execution/factories/data-sources",
            params=params,
            parse_json=True,
            type_=List[Optional[FactoryDataSourceTransport]],
            **kwargs,
        )

    @staticmethod
    def post_api_v2_workspaces_workspace_id_execution_factories_entity_preview(
        client: Client,
        workspace_id: str,
        request_body: EntityPreviewRequest,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> EntityPreviewResponse:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v2/workspaces/{workspace_id}/execution/factories/entity/preview'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v2/workspaces/{workspace_id}/execution/factories/entity/preview",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="POST",
            url=f"/bl/api/v2/workspaces/{workspace_id}/execution/factories/entity/preview",
            params=params,
            request_body=request_body,
            parse_json=True,
            type_=EntityPreviewResponse,
            **kwargs,
        )

    @staticmethod
    def post_api_v2_workspaces_workspace_id_execution_factories_events_execute(
        client: Client,
        workspace_id: str,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> None:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v2/workspaces/{workspace_id}/execution/factories/events/execute'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v2/workspaces/{workspace_id}/execution/factories/events/execute",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="POST",
            url=f"/bl/api/v2/workspaces/{workspace_id}/execution/factories/events/execute",
            params=params,
            **kwargs,
        )

    @staticmethod
    def post_api_v2_workspaces_workspace_id_execution_factories_events_preview(
        client: Client,
        workspace_id: str,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> PreviewTransport:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v2/workspaces/{workspace_id}/execution/factories/events/preview'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v2/workspaces/{workspace_id}/execution/factories/events/preview",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="POST",
            url=f"/bl/api/v2/workspaces/{workspace_id}/execution/factories/events/preview",
            params=params,
            parse_json=True,
            type_=PreviewTransport,
            **kwargs,
        )

    @staticmethod
    def post_api_v2_workspaces_workspace_id_execution_factories_objects_execute(
        client: Client,
        workspace_id: str,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> None:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v2/workspaces/{workspace_id}/execution/factories/objects/execute'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v2/workspaces/{workspace_id}/execution/factories/objects/execute",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="POST",
            url=f"/bl/api/v2/workspaces/{workspace_id}/execution/factories/objects/execute",
            params=params,
            **kwargs,
        )

    @staticmethod
    def get_api_v2_workspaces_workspace_id_execution_factories_objects_source_preview(
        client: Client,
        workspace_id: str,
        schema_name: Optional["str"] = None,
        table_name: Optional["str"] = None,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> PreviewTransport:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v2/workspaces/{workspace_id}/execution/factories/objects/source-preview'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v2/workspaces/{workspace_id}/execution/factories/objects/source-preview",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if schema_name is not None:
            if isinstance(schema_name, PyCelonisBaseModel):
                params.update(schema_name.json_dict(by_alias=True))
            elif isinstance(schema_name, dict):
                params.update(schema_name)
            else:
                params["schemaName"] = schema_name
        if table_name is not None:
            if isinstance(table_name, PyCelonisBaseModel):
                params.update(table_name.json_dict(by_alias=True))
            elif isinstance(table_name, dict):
                params.update(table_name)
            else:
                params["tableName"] = table_name
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v2/workspaces/{workspace_id}/execution/factories/objects/source-preview",
            params=params,
            parse_json=True,
            type_=PreviewTransport,
            **kwargs,
        )

    @staticmethod
    def get_api_v2_workspaces_workspace_id_execution_factories_objects_source_tables(
        client: Client,
        workspace_id: str,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> ObjectFactorySourceTransport:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v2/workspaces/{workspace_id}/execution/factories/objects/source-tables'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v2/workspaces/{workspace_id}/execution/factories/objects/source-tables",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v2/workspaces/{workspace_id}/execution/factories/objects/source-tables",
            params=params,
            parse_json=True,
            type_=ObjectFactorySourceTransport,
            **kwargs,
        )

    @staticmethod
    def post_api_v2_workspaces_workspace_id_execution_factories_sql_dataset_preview(
        client: Client,
        workspace_id: str,
        request_body: SqlFactoryDataSetPreviewRequest,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> FactoryDataSetPreviewResponse:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v2/workspaces/{workspace_id}/execution/factories/sql/dataset-preview'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v2/workspaces/{workspace_id}/execution/factories/sql/dataset-preview",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="POST",
            url=f"/bl/api/v2/workspaces/{workspace_id}/execution/factories/sql/dataset-preview",
            params=params,
            request_body=request_body,
            parse_json=True,
            type_=FactoryDataSetPreviewResponse,
            **kwargs,
        )

    @staticmethod
    def post_api_v2_workspaces_workspace_id_execution_factories_sql_validate(
        client: Client,
        workspace_id: str,
        request_body: SqlFactoryDataSetPreviewRequest,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> FactoryDataSetValidationResponse:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v2/workspaces/{workspace_id}/execution/factories/sql/validate'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v2/workspaces/{workspace_id}/execution/factories/sql/validate",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="POST",
            url=f"/bl/api/v2/workspaces/{workspace_id}/execution/factories/sql/validate",
            params=params,
            request_body=request_body,
            parse_json=True,
            type_=FactoryDataSetValidationResponse,
            **kwargs,
        )

    @staticmethod
    def post_api_v2_workspaces_workspace_id_execution_publish(
        client: Client,
        workspace_id: str,
        environment: Optional["str"] = None,
        include_user_template_transformations: Optional["bool"] = None,
        use_v2_manifest: Optional["bool"] = None,
        **kwargs: Any,
    ) -> CreateOrUpdateBusinessGraphResponse:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v2/workspaces/{workspace_id}/execution/publish'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v2/workspaces/{workspace_id}/execution/publish",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        if include_user_template_transformations is not None:
            if isinstance(include_user_template_transformations, PyCelonisBaseModel):
                params.update(
                    include_user_template_transformations.json_dict(by_alias=True)
                )
            elif isinstance(include_user_template_transformations, dict):
                params.update(include_user_template_transformations)
            else:
                params[
                    "includeUserTemplateTransformations"
                ] = include_user_template_transformations
        if use_v2_manifest is not None:
            if isinstance(use_v2_manifest, PyCelonisBaseModel):
                params.update(use_v2_manifest.json_dict(by_alias=True))
            elif isinstance(use_v2_manifest, dict):
                params.update(use_v2_manifest)
            else:
                params["useV2Manifest"] = use_v2_manifest
        return client.request(
            method="POST",
            url=f"/bl/api/v2/workspaces/{workspace_id}/execution/publish",
            params=params,
            parse_json=True,
            type_=CreateOrUpdateBusinessGraphResponse,
            **kwargs,
        )

    @staticmethod
    def post_api_v2_workspaces_workspace_id_execution_tables_import(
        client: Client,
        workspace_id: str,
        request_body: List[Optional[TableImportRequestOptions]],
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> List[Optional[TableImportTransport]]:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v2/workspaces/{workspace_id}/execution/tables/import'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v2/workspaces/{workspace_id}/execution/tables/import",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="POST",
            url=f"/bl/api/v2/workspaces/{workspace_id}/execution/tables/import",
            params=params,
            request_body=request_body,
            parse_json=True,
            type_=List[Optional[TableImportTransport]],
            **kwargs,
        )

    @staticmethod
    def put_api_v2_workspaces_workspace_id_execution_tables_mappings(
        client: Client,
        workspace_id: str,
        request_body: List[Optional[TableMappingRequestOptions]],
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> List[Optional[TableImportTransport]]:
        logger.debug(
            f"Request: 'PUT' -> '/bl/api/v2/workspaces/{workspace_id}/execution/tables/mappings'",
            extra={
                "request_type": "PUT",
                "path": "/bl/api/v2/workspaces/{workspace_id}/execution/tables/mappings",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="PUT",
            url=f"/bl/api/v2/workspaces/{workspace_id}/execution/tables/mappings",
            params=params,
            request_body=request_body,
            parse_json=True,
            type_=List[Optional[TableImportTransport]],
            **kwargs,
        )

    @staticmethod
    def get_api_v2_workspaces_workspace_id_factories_event(
        client: Client,
        workspace_id: str,
        filter_options: Optional["EntityFilterOptions"] = None,
        pagination: Optional["Pagination"] = None,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> PageEventFactory:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v2/workspaces/{workspace_id}/factories/event'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v2/workspaces/{workspace_id}/factories/event",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if filter_options is not None:
            if isinstance(filter_options, PyCelonisBaseModel):
                params.update(filter_options.json_dict(by_alias=True))
            elif isinstance(filter_options, dict):
                params.update(filter_options)
            else:
                params["filterOptions"] = filter_options
        if pagination is not None:
            if isinstance(pagination, PyCelonisBaseModel):
                params.update(pagination.json_dict(by_alias=True))
            elif isinstance(pagination, dict):
                params.update(pagination)
            else:
                params["pagination"] = pagination
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v2/workspaces/{workspace_id}/factories/event",
            params=params,
            parse_json=True,
            type_=PageEventFactory,
            **kwargs,
        )

    @staticmethod
    def post_api_v2_workspaces_workspace_id_factories_event(
        client: Client,
        workspace_id: str,
        request_body: EventFactoryRequestOptions,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> EventFactory:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v2/workspaces/{workspace_id}/factories/event'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v2/workspaces/{workspace_id}/factories/event",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="POST",
            url=f"/bl/api/v2/workspaces/{workspace_id}/factories/event",
            params=params,
            request_body=request_body,
            parse_json=True,
            type_=EventFactory,
            **kwargs,
        )

    @staticmethod
    def get_api_v2_workspaces_workspace_id_factories_event_event_factory_id(
        client: Client,
        workspace_id: str,
        event_factory_id: str,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> EventFactory:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v2/workspaces/{workspace_id}/factories/event/{event_factory_id}'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v2/workspaces/{workspace_id}/factories/event/{event_factory_id}",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v2/workspaces/{workspace_id}/factories/event/{event_factory_id}",
            params=params,
            parse_json=True,
            type_=EventFactory,
            **kwargs,
        )

    @staticmethod
    def put_api_v2_workspaces_workspace_id_factories_event_event_factory_id(
        client: Client,
        workspace_id: str,
        event_factory_id: str,
        request_body: EventFactoryRequestOptions,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> EventFactory:
        logger.debug(
            f"Request: 'PUT' -> '/bl/api/v2/workspaces/{workspace_id}/factories/event/{event_factory_id}'",
            extra={
                "request_type": "PUT",
                "path": "/bl/api/v2/workspaces/{workspace_id}/factories/event/{event_factory_id}",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="PUT",
            url=f"/bl/api/v2/workspaces/{workspace_id}/factories/event/{event_factory_id}",
            params=params,
            request_body=request_body,
            parse_json=True,
            type_=EventFactory,
            **kwargs,
        )

    @staticmethod
    def delete_api_v2_workspaces_workspace_id_factories_event_event_factory_id(
        client: Client,
        workspace_id: str,
        event_factory_id: str,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> None:
        logger.debug(
            f"Request: 'DELETE' -> '/bl/api/v2/workspaces/{workspace_id}/factories/event/{event_factory_id}'",
            extra={
                "request_type": "DELETE",
                "path": "/bl/api/v2/workspaces/{workspace_id}/factories/event/{event_factory_id}",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="DELETE",
            url=f"/bl/api/v2/workspaces/{workspace_id}/factories/event/{event_factory_id}",
            params=params,
            **kwargs,
        )

    @staticmethod
    def get_api_v2_workspaces_workspace_id_factories_sql(
        client: Client,
        workspace_id: str,
        filter_options: Optional["SqlFactoryFilterOptions"] = None,
        pagination: Optional["Pagination"] = None,
        environment: Optional["str"] = None,
        include_user_template_transformations: Optional["bool"] = None,
        **kwargs: Any,
    ) -> PageFactoryListTransport:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v2/workspaces/{workspace_id}/factories/sql'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v2/workspaces/{workspace_id}/factories/sql",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if filter_options is not None:
            if isinstance(filter_options, PyCelonisBaseModel):
                params.update(filter_options.json_dict(by_alias=True))
            elif isinstance(filter_options, dict):
                params.update(filter_options)
            else:
                params["filterOptions"] = filter_options
        if pagination is not None:
            if isinstance(pagination, PyCelonisBaseModel):
                params.update(pagination.json_dict(by_alias=True))
            elif isinstance(pagination, dict):
                params.update(pagination)
            else:
                params["pagination"] = pagination
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        if include_user_template_transformations is not None:
            if isinstance(include_user_template_transformations, PyCelonisBaseModel):
                params.update(
                    include_user_template_transformations.json_dict(by_alias=True)
                )
            elif isinstance(include_user_template_transformations, dict):
                params.update(include_user_template_transformations)
            else:
                params[
                    "includeUserTemplateTransformations"
                ] = include_user_template_transformations
        return client.request(
            method="GET",
            url=f"/bl/api/v2/workspaces/{workspace_id}/factories/sql",
            params=params,
            parse_json=True,
            type_=PageFactoryListTransport,
            **kwargs,
        )

    @staticmethod
    def post_api_v2_workspaces_workspace_id_factories_sql(
        client: Client,
        workspace_id: str,
        request_body: SqlFactoryRequestOptions,
        environment: Optional["str"] = None,
        use_v2_manifest: Optional["bool"] = None,
        **kwargs: Any,
    ) -> SqlFactoryTransport:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v2/workspaces/{workspace_id}/factories/sql'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v2/workspaces/{workspace_id}/factories/sql",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        if use_v2_manifest is not None:
            if isinstance(use_v2_manifest, PyCelonisBaseModel):
                params.update(use_v2_manifest.json_dict(by_alias=True))
            elif isinstance(use_v2_manifest, dict):
                params.update(use_v2_manifest)
            else:
                params["useV2Manifest"] = use_v2_manifest
        return client.request(
            method="POST",
            url=f"/bl/api/v2/workspaces/{workspace_id}/factories/sql",
            params=params,
            request_body=request_body,
            parse_json=True,
            type_=SqlFactoryTransport,
            **kwargs,
        )

    @staticmethod
    def post_api_v2_workspaces_workspace_id_factories_sql_batch(
        client: Client,
        workspace_id: str,
        request_body: List[Optional[SqlFactoryRequestOptions]],
        environment: Optional["str"] = None,
        use_v2_manifest: Optional["bool"] = None,
        **kwargs: Any,
    ) -> List[Optional[SqlFactoryTransport]]:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v2/workspaces/{workspace_id}/factories/sql/batch'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v2/workspaces/{workspace_id}/factories/sql/batch",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        if use_v2_manifest is not None:
            if isinstance(use_v2_manifest, PyCelonisBaseModel):
                params.update(use_v2_manifest.json_dict(by_alias=True))
            elif isinstance(use_v2_manifest, dict):
                params.update(use_v2_manifest)
            else:
                params["useV2Manifest"] = use_v2_manifest
        return client.request(
            method="POST",
            url=f"/bl/api/v2/workspaces/{workspace_id}/factories/sql/batch",
            params=params,
            request_body=request_body,
            parse_json=True,
            type_=List[Optional[SqlFactoryTransport]],
            **kwargs,
        )

    @staticmethod
    def put_api_v2_workspaces_workspace_id_factories_sql_change_state(
        client: Client,
        workspace_id: str,
        request_body: SqlFactoryChangeStateManyRequest,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> List[Optional[FactoryListTransport]]:
        logger.debug(
            f"Request: 'PUT' -> '/bl/api/v2/workspaces/{workspace_id}/factories/sql/change-state'",
            extra={
                "request_type": "PUT",
                "path": "/bl/api/v2/workspaces/{workspace_id}/factories/sql/change-state",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="PUT",
            url=f"/bl/api/v2/workspaces/{workspace_id}/factories/sql/change-state",
            params=params,
            request_body=request_body,
            parse_json=True,
            type_=List[Optional[FactoryListTransport]],
            **kwargs,
        )

    @staticmethod
    def get_api_v2_workspaces_workspace_id_factories_sql_change_table_columns(
        client: Client,
        workspace_id: str,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> List[Optional[EntityField]]:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v2/workspaces/{workspace_id}/factories/sql/changeTableColumns'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v2/workspaces/{workspace_id}/factories/sql/changeTableColumns",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v2/workspaces/{workspace_id}/factories/sql/changeTableColumns",
            params=params,
            parse_json=True,
            type_=List[Optional[EntityField]],
            **kwargs,
        )

    @staticmethod
    def get_api_v2_workspaces_workspace_id_factories_sql_custom_factory_id(
        client: Client,
        workspace_id: str,
        factory_id: str,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> SqlFactoryTransport:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v2/workspaces/{workspace_id}/factories/sql/custom/{factory_id}'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v2/workspaces/{workspace_id}/factories/sql/custom/{factory_id}",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v2/workspaces/{workspace_id}/factories/sql/custom/{factory_id}",
            params=params,
            parse_json=True,
            type_=SqlFactoryTransport,
            **kwargs,
        )

    @staticmethod
    def get_api_v2_workspaces_workspace_id_factories_sql_templates(
        client: Client,
        workspace_id: str,
        pagination: Optional["Pagination"] = None,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> PageUserFactoryTemplateListTransport:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v2/workspaces/{workspace_id}/factories/sql/templates'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v2/workspaces/{workspace_id}/factories/sql/templates",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if pagination is not None:
            if isinstance(pagination, PyCelonisBaseModel):
                params.update(pagination.json_dict(by_alias=True))
            elif isinstance(pagination, dict):
                params.update(pagination)
            else:
                params["pagination"] = pagination
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v2/workspaces/{workspace_id}/factories/sql/templates",
            params=params,
            parse_json=True,
            type_=PageUserFactoryTemplateListTransport,
            **kwargs,
        )

    @staticmethod
    def post_api_v2_workspaces_workspace_id_factories_sql_templates(
        client: Client,
        workspace_id: str,
        request_body: UserFactoryTemplateRequestOptions,
        environment: Optional["str"] = None,
        use_v2_manifest: Optional["bool"] = None,
        **kwargs: Any,
    ) -> UserFactoryTemplateTransport:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v2/workspaces/{workspace_id}/factories/sql/templates'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v2/workspaces/{workspace_id}/factories/sql/templates",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        if use_v2_manifest is not None:
            if isinstance(use_v2_manifest, PyCelonisBaseModel):
                params.update(use_v2_manifest.json_dict(by_alias=True))
            elif isinstance(use_v2_manifest, dict):
                params.update(use_v2_manifest)
            else:
                params["useV2Manifest"] = use_v2_manifest
        return client.request(
            method="POST",
            url=f"/bl/api/v2/workspaces/{workspace_id}/factories/sql/templates",
            params=params,
            request_body=request_body,
            parse_json=True,
            type_=UserFactoryTemplateTransport,
            **kwargs,
        )

    @staticmethod
    def get_api_v2_workspaces_workspace_id_factories_sql_templates_template_id(
        client: Client,
        workspace_id: str,
        template_id: str,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> UserFactoryTemplateTransport:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v2/workspaces/{workspace_id}/factories/sql/templates/{template_id}'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v2/workspaces/{workspace_id}/factories/sql/templates/{template_id}",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v2/workspaces/{workspace_id}/factories/sql/templates/{template_id}",
            params=params,
            parse_json=True,
            type_=UserFactoryTemplateTransport,
            **kwargs,
        )

    @staticmethod
    def put_api_v2_workspaces_workspace_id_factories_sql_templates_template_id(
        client: Client,
        workspace_id: str,
        template_id: str,
        request_body: UserFactoryTemplateRequestOptions,
        environment: Optional["str"] = None,
        use_v2_manifest: Optional["bool"] = None,
        **kwargs: Any,
    ) -> UserFactoryTemplateTransport:
        logger.debug(
            f"Request: 'PUT' -> '/bl/api/v2/workspaces/{workspace_id}/factories/sql/templates/{template_id}'",
            extra={
                "request_type": "PUT",
                "path": "/bl/api/v2/workspaces/{workspace_id}/factories/sql/templates/{template_id}",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        if use_v2_manifest is not None:
            if isinstance(use_v2_manifest, PyCelonisBaseModel):
                params.update(use_v2_manifest.json_dict(by_alias=True))
            elif isinstance(use_v2_manifest, dict):
                params.update(use_v2_manifest)
            else:
                params["useV2Manifest"] = use_v2_manifest
        return client.request(
            method="PUT",
            url=f"/bl/api/v2/workspaces/{workspace_id}/factories/sql/templates/{template_id}",
            params=params,
            request_body=request_body,
            parse_json=True,
            type_=UserFactoryTemplateTransport,
            **kwargs,
        )

    @staticmethod
    def delete_api_v2_workspaces_workspace_id_factories_sql_templates_template_id(
        client: Client,
        workspace_id: str,
        template_id: str,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> None:
        logger.debug(
            f"Request: 'DELETE' -> '/bl/api/v2/workspaces/{workspace_id}/factories/sql/templates/{template_id}'",
            extra={
                "request_type": "DELETE",
                "path": "/bl/api/v2/workspaces/{workspace_id}/factories/sql/templates/{template_id}",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="DELETE",
            url=f"/bl/api/v2/workspaces/{workspace_id}/factories/sql/templates/{template_id}",
            params=params,
            **kwargs,
        )

    @staticmethod
    def get_api_v2_workspaces_workspace_id_factories_sql_templates_template_id_instances(
        client: Client,
        workspace_id: str,
        template_id: str,
        pagination: Optional["Pagination"] = None,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> PageFactoryListTransport:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v2/workspaces/{workspace_id}/factories/sql/templates/{template_id}/instances'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v2/workspaces/{workspace_id}/factories/sql/templates/{template_id}/instances",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if pagination is not None:
            if isinstance(pagination, PyCelonisBaseModel):
                params.update(pagination.json_dict(by_alias=True))
            elif isinstance(pagination, dict):
                params.update(pagination)
            else:
                params["pagination"] = pagination
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v2/workspaces/{workspace_id}/factories/sql/templates/{template_id}/instances",
            params=params,
            parse_json=True,
            type_=PageFactoryListTransport,
            **kwargs,
        )

    @staticmethod
    def get_api_v2_workspaces_workspace_id_factories_sql_factory_id(
        client: Client,
        workspace_id: str,
        factory_id: str,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> SqlFactoryTransport:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v2/workspaces/{workspace_id}/factories/sql/{factory_id}'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v2/workspaces/{workspace_id}/factories/sql/{factory_id}",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v2/workspaces/{workspace_id}/factories/sql/{factory_id}",
            params=params,
            parse_json=True,
            type_=SqlFactoryTransport,
            **kwargs,
        )

    @staticmethod
    def put_api_v2_workspaces_workspace_id_factories_sql_factory_id(
        client: Client,
        workspace_id: str,
        factory_id: str,
        request_body: SqlFactoryRequestOptions,
        environment: Optional["str"] = None,
        use_v2_manifest: Optional["bool"] = None,
        **kwargs: Any,
    ) -> SqlFactoryTransport:
        logger.debug(
            f"Request: 'PUT' -> '/bl/api/v2/workspaces/{workspace_id}/factories/sql/{factory_id}'",
            extra={
                "request_type": "PUT",
                "path": "/bl/api/v2/workspaces/{workspace_id}/factories/sql/{factory_id}",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        if use_v2_manifest is not None:
            if isinstance(use_v2_manifest, PyCelonisBaseModel):
                params.update(use_v2_manifest.json_dict(by_alias=True))
            elif isinstance(use_v2_manifest, dict):
                params.update(use_v2_manifest)
            else:
                params["useV2Manifest"] = use_v2_manifest
        return client.request(
            method="PUT",
            url=f"/bl/api/v2/workspaces/{workspace_id}/factories/sql/{factory_id}",
            params=params,
            request_body=request_body,
            parse_json=True,
            type_=SqlFactoryTransport,
            **kwargs,
        )

    @staticmethod
    def delete_api_v2_workspaces_workspace_id_factories_sql_factory_id(
        client: Client,
        workspace_id: str,
        factory_id: str,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> None:
        logger.debug(
            f"Request: 'DELETE' -> '/bl/api/v2/workspaces/{workspace_id}/factories/sql/{factory_id}'",
            extra={
                "request_type": "DELETE",
                "path": "/bl/api/v2/workspaces/{workspace_id}/factories/sql/{factory_id}",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="DELETE",
            url=f"/bl/api/v2/workspaces/{workspace_id}/factories/sql/{factory_id}",
            params=params,
            **kwargs,
        )

    @staticmethod
    def post_api_v2_workspaces_workspace_id_factories_sql_factory_id_convert_to_template(
        client: Client,
        workspace_id: str,
        factory_id: str,
        request_body: ConvertSqlFactoryToTemplateRequestOptions,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> SqlFactoryTransport:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v2/workspaces/{workspace_id}/factories/sql/{factory_id}/convert-to-template'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v2/workspaces/{workspace_id}/factories/sql/{factory_id}/convert-to-template",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="POST",
            url=f"/bl/api/v2/workspaces/{workspace_id}/factories/sql/{factory_id}/convert-to-template",
            params=params,
            request_body=request_body,
            parse_json=True,
            type_=SqlFactoryTransport,
            **kwargs,
        )

    @staticmethod
    def post_api_v2_workspaces_workspace_id_factories_sql_factory_id_detach(
        client: Client,
        workspace_id: str,
        factory_id: str,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> SqlFactoryTransport:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v2/workspaces/{workspace_id}/factories/sql/{factory_id}/detach'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v2/workspaces/{workspace_id}/factories/sql/{factory_id}/detach",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="POST",
            url=f"/bl/api/v2/workspaces/{workspace_id}/factories/sql/{factory_id}/detach",
            params=params,
            parse_json=True,
            type_=SqlFactoryTransport,
            **kwargs,
        )

    @staticmethod
    def post_api_v2_workspaces_workspace_id_factories_sql_factory_id_duplicate(
        client: Client,
        workspace_id: str,
        factory_id: str,
        request_body: DuplicateSqlFactoryOptions,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> SqlFactoryTransport:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v2/workspaces/{workspace_id}/factories/sql/{factory_id}/duplicate'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v2/workspaces/{workspace_id}/factories/sql/{factory_id}/duplicate",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="POST",
            url=f"/bl/api/v2/workspaces/{workspace_id}/factories/sql/{factory_id}/duplicate",
            params=params,
            request_body=request_body,
            parse_json=True,
            type_=SqlFactoryTransport,
            **kwargs,
        )

    @staticmethod
    def post_api_v2_workspaces_workspace_id_factories_sql_factory_id_update_metadata(
        client: Client,
        workspace_id: str,
        factory_id: str,
        request_body: SqlFactoryUpdateMetadataRequestOptions,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> SqlFactoryTransport:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v2/workspaces/{workspace_id}/factories/sql/{factory_id}/update-metadata'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v2/workspaces/{workspace_id}/factories/sql/{factory_id}/update-metadata",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="POST",
            url=f"/bl/api/v2/workspaces/{workspace_id}/factories/sql/{factory_id}/update-metadata",
            params=params,
            request_body=request_body,
            parse_json=True,
            type_=SqlFactoryTransport,
            **kwargs,
        )

    @staticmethod
    def get_api_v2_workspaces_workspace_id_landscape_layout(
        client: Client,
        workspace_id: str,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> BusinessLandscapeLayout:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v2/workspaces/{workspace_id}/landscape/layout'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v2/workspaces/{workspace_id}/landscape/layout",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v2/workspaces/{workspace_id}/landscape/layout",
            params=params,
            parse_json=True,
            type_=BusinessLandscapeLayout,
            **kwargs,
        )

    @staticmethod
    def put_api_v2_workspaces_workspace_id_landscape_layout(
        client: Client,
        workspace_id: str,
        request_body: BusinessLandscapeLayoutOptions,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> BusinessLandscapeLayout:
        logger.debug(
            f"Request: 'PUT' -> '/bl/api/v2/workspaces/{workspace_id}/landscape/layout'",
            extra={
                "request_type": "PUT",
                "path": "/bl/api/v2/workspaces/{workspace_id}/landscape/layout",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="PUT",
            url=f"/bl/api/v2/workspaces/{workspace_id}/landscape/layout",
            params=params,
            request_body=request_body,
            parse_json=True,
            type_=BusinessLandscapeLayout,
            **kwargs,
        )

    @staticmethod
    def post_api_v2_workspaces_workspace_id_landscape_layout(
        client: Client,
        workspace_id: str,
        request_body: BusinessLandscapeLayoutOptions,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> BusinessLandscapeLayout:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v2/workspaces/{workspace_id}/landscape/layout'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v2/workspaces/{workspace_id}/landscape/layout",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="POST",
            url=f"/bl/api/v2/workspaces/{workspace_id}/landscape/layout",
            params=params,
            request_body=request_body,
            parse_json=True,
            type_=BusinessLandscapeLayout,
            **kwargs,
        )

    @staticmethod
    def get_api_v2_workspaces_workspace_id_perspectives(
        client: Client,
        workspace_id: str,
        filter_options: Optional["PerspectiveFilterOptions"] = None,
        pagination: Optional["Pagination"] = None,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> PagePerspective:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v2/workspaces/{workspace_id}/perspectives'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v2/workspaces/{workspace_id}/perspectives",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if filter_options is not None:
            if isinstance(filter_options, PyCelonisBaseModel):
                params.update(filter_options.json_dict(by_alias=True))
            elif isinstance(filter_options, dict):
                params.update(filter_options)
            else:
                params["filterOptions"] = filter_options
        if pagination is not None:
            if isinstance(pagination, PyCelonisBaseModel):
                params.update(pagination.json_dict(by_alias=True))
            elif isinstance(pagination, dict):
                params.update(pagination)
            else:
                params["pagination"] = pagination
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v2/workspaces/{workspace_id}/perspectives",
            params=params,
            parse_json=True,
            type_=PagePerspective,
            **kwargs,
        )

    @staticmethod
    def post_api_v2_workspaces_workspace_id_perspectives(
        client: Client,
        workspace_id: str,
        request_body: PerspectiveRequestOptions,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> Perspective:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v2/workspaces/{workspace_id}/perspectives'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v2/workspaces/{workspace_id}/perspectives",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="POST",
            url=f"/bl/api/v2/workspaces/{workspace_id}/perspectives",
            params=params,
            request_body=request_body,
            parse_json=True,
            type_=Perspective,
            **kwargs,
        )

    @staticmethod
    def get_api_v2_workspaces_workspace_id_perspectives_perspective_id(
        client: Client,
        workspace_id: str,
        perspective_id: str,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> Perspective:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v2/workspaces/{workspace_id}/perspectives/{perspective_id}'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v2/workspaces/{workspace_id}/perspectives/{perspective_id}",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v2/workspaces/{workspace_id}/perspectives/{perspective_id}",
            params=params,
            parse_json=True,
            type_=Perspective,
            **kwargs,
        )

    @staticmethod
    def put_api_v2_workspaces_workspace_id_perspectives_perspective_id(
        client: Client,
        workspace_id: str,
        perspective_id: str,
        request_body: PerspectiveRequestOptions,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> Perspective:
        logger.debug(
            f"Request: 'PUT' -> '/bl/api/v2/workspaces/{workspace_id}/perspectives/{perspective_id}'",
            extra={
                "request_type": "PUT",
                "path": "/bl/api/v2/workspaces/{workspace_id}/perspectives/{perspective_id}",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="PUT",
            url=f"/bl/api/v2/workspaces/{workspace_id}/perspectives/{perspective_id}",
            params=params,
            request_body=request_body,
            parse_json=True,
            type_=Perspective,
            **kwargs,
        )

    @staticmethod
    def delete_api_v2_workspaces_workspace_id_perspectives_perspective_id(
        client: Client,
        workspace_id: str,
        perspective_id: str,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> None:
        logger.debug(
            f"Request: 'DELETE' -> '/bl/api/v2/workspaces/{workspace_id}/perspectives/{perspective_id}'",
            extra={
                "request_type": "DELETE",
                "path": "/bl/api/v2/workspaces/{workspace_id}/perspectives/{perspective_id}",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="DELETE",
            url=f"/bl/api/v2/workspaces/{workspace_id}/perspectives/{perspective_id}",
            params=params,
            **kwargs,
        )

    @staticmethod
    def get_api_v2_workspaces_workspace_id_processes(
        client: Client,
        workspace_id: str,
        pagination: Optional["Pagination"] = None,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> PageProcess:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v2/workspaces/{workspace_id}/processes'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v2/workspaces/{workspace_id}/processes",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if pagination is not None:
            if isinstance(pagination, PyCelonisBaseModel):
                params.update(pagination.json_dict(by_alias=True))
            elif isinstance(pagination, dict):
                params.update(pagination)
            else:
                params["pagination"] = pagination
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v2/workspaces/{workspace_id}/processes",
            params=params,
            parse_json=True,
            type_=PageProcess,
            **kwargs,
        )

    @staticmethod
    def post_api_v2_workspaces_workspace_id_processes(
        client: Client,
        workspace_id: str,
        request_body: ProcessCreateOptions,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> Process:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v2/workspaces/{workspace_id}/processes'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v2/workspaces/{workspace_id}/processes",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="POST",
            url=f"/bl/api/v2/workspaces/{workspace_id}/processes",
            params=params,
            request_body=request_body,
            parse_json=True,
            type_=Process,
            **kwargs,
        )

    @staticmethod
    def get_api_v2_workspaces_workspace_id_processes_transformation_types(
        client: Client,
        workspace_id: str,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> List[Optional[DataSourceTransformationType]]:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v2/workspaces/{workspace_id}/processes/transformation-types'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v2/workspaces/{workspace_id}/processes/transformation-types",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v2/workspaces/{workspace_id}/processes/transformation-types",
            params=params,
            parse_json=True,
            type_=List[Optional[DataSourceTransformationType]],
            **kwargs,
        )

    @staticmethod
    def get_api_v2_workspaces_workspace_id_processes_process_name(
        client: Client,
        workspace_id: str,
        process_name: str,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> Process:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v2/workspaces/{workspace_id}/processes/{process_name}'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v2/workspaces/{workspace_id}/processes/{process_name}",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v2/workspaces/{workspace_id}/processes/{process_name}",
            params=params,
            parse_json=True,
            type_=Process,
            **kwargs,
        )

    @staticmethod
    def put_api_v2_workspaces_workspace_id_processes_process_name(
        client: Client,
        workspace_id: str,
        process_name: str,
        request_body: ProcessUpdateOptions,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> Process:
        logger.debug(
            f"Request: 'PUT' -> '/bl/api/v2/workspaces/{workspace_id}/processes/{process_name}'",
            extra={
                "request_type": "PUT",
                "path": "/bl/api/v2/workspaces/{workspace_id}/processes/{process_name}",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="PUT",
            url=f"/bl/api/v2/workspaces/{workspace_id}/processes/{process_name}",
            params=params,
            request_body=request_body,
            parse_json=True,
            type_=Process,
            **kwargs,
        )

    @staticmethod
    def delete_api_v2_workspaces_workspace_id_processes_process_name(
        client: Client,
        workspace_id: str,
        process_name: str,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> None:
        logger.debug(
            f"Request: 'DELETE' -> '/bl/api/v2/workspaces/{workspace_id}/processes/{process_name}'",
            extra={
                "request_type": "DELETE",
                "path": "/bl/api/v2/workspaces/{workspace_id}/processes/{process_name}",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="DELETE",
            url=f"/bl/api/v2/workspaces/{workspace_id}/processes/{process_name}",
            params=params,
            **kwargs,
        )

    @staticmethod
    def post_api_v2_workspaces_workspace_id_processes_process_name_disable(
        client: Client,
        workspace_id: str,
        process_name: str,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> Process:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v2/workspaces/{workspace_id}/processes/{process_name}/disable'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v2/workspaces/{workspace_id}/processes/{process_name}/disable",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="POST",
            url=f"/bl/api/v2/workspaces/{workspace_id}/processes/{process_name}/disable",
            params=params,
            parse_json=True,
            type_=Process,
            **kwargs,
        )

    @staticmethod
    def post_api_v2_workspaces_workspace_id_processes_process_name_enable(
        client: Client,
        workspace_id: str,
        process_name: str,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> Process:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v2/workspaces/{workspace_id}/processes/{process_name}/enable'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v2/workspaces/{workspace_id}/processes/{process_name}/enable",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="POST",
            url=f"/bl/api/v2/workspaces/{workspace_id}/processes/{process_name}/enable",
            params=params,
            parse_json=True,
            type_=Process,
            **kwargs,
        )

    @staticmethod
    def get_api_v2_workspaces_workspace_id_tags(
        client: Client,
        workspace_id: str,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> List[Optional[str]]:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v2/workspaces/{workspace_id}/tags'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v2/workspaces/{workspace_id}/tags",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v2/workspaces/{workspace_id}/tags",
            params=params,
            parse_json=True,
            type_=List[Optional[str]],
            **kwargs,
        )

    @staticmethod
    def get_api_v2_workspaces_workspace_id_types_events(
        client: Client,
        workspace_id: str,
        filter_options: Optional["EntityFilterOptions"] = None,
        pagination: Optional["Pagination"] = None,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> PageEventEntity:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v2/workspaces/{workspace_id}/types/events'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v2/workspaces/{workspace_id}/types/events",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if filter_options is not None:
            if isinstance(filter_options, PyCelonisBaseModel):
                params.update(filter_options.json_dict(by_alias=True))
            elif isinstance(filter_options, dict):
                params.update(filter_options)
            else:
                params["filterOptions"] = filter_options
        if pagination is not None:
            if isinstance(pagination, PyCelonisBaseModel):
                params.update(pagination.json_dict(by_alias=True))
            elif isinstance(pagination, dict):
                params.update(pagination)
            else:
                params["pagination"] = pagination
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v2/workspaces/{workspace_id}/types/events",
            params=params,
            parse_json=True,
            type_=PageEventEntity,
            **kwargs,
        )

    @staticmethod
    def post_api_v2_workspaces_workspace_id_types_events(
        client: Client,
        workspace_id: str,
        request_body: EventEntityRequestOptions,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> EventEntity:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v2/workspaces/{workspace_id}/types/events'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v2/workspaces/{workspace_id}/types/events",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="POST",
            url=f"/bl/api/v2/workspaces/{workspace_id}/types/events",
            params=params,
            request_body=request_body,
            parse_json=True,
            type_=EventEntity,
            **kwargs,
        )

    @staticmethod
    def get_api_v2_workspaces_workspace_id_types_events_event_type_id(
        client: Client,
        workspace_id: str,
        event_type_id: str,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> EventEntity:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v2/workspaces/{workspace_id}/types/events/{event_type_id}'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v2/workspaces/{workspace_id}/types/events/{event_type_id}",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v2/workspaces/{workspace_id}/types/events/{event_type_id}",
            params=params,
            parse_json=True,
            type_=EventEntity,
            **kwargs,
        )

    @staticmethod
    def put_api_v2_workspaces_workspace_id_types_events_event_type_id(
        client: Client,
        workspace_id: str,
        event_type_id: str,
        request_body: EventEntityRequestOptions,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> EventEntity:
        logger.debug(
            f"Request: 'PUT' -> '/bl/api/v2/workspaces/{workspace_id}/types/events/{event_type_id}'",
            extra={
                "request_type": "PUT",
                "path": "/bl/api/v2/workspaces/{workspace_id}/types/events/{event_type_id}",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="PUT",
            url=f"/bl/api/v2/workspaces/{workspace_id}/types/events/{event_type_id}",
            params=params,
            request_body=request_body,
            parse_json=True,
            type_=EventEntity,
            **kwargs,
        )

    @staticmethod
    def delete_api_v2_workspaces_workspace_id_types_events_event_type_id(
        client: Client,
        workspace_id: str,
        event_type_id: str,
        force: Optional["bool"] = None,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> None:
        logger.debug(
            f"Request: 'DELETE' -> '/bl/api/v2/workspaces/{workspace_id}/types/events/{event_type_id}'",
            extra={
                "request_type": "DELETE",
                "path": "/bl/api/v2/workspaces/{workspace_id}/types/events/{event_type_id}",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if force is not None:
            if isinstance(force, PyCelonisBaseModel):
                params.update(force.json_dict(by_alias=True))
            elif isinstance(force, dict):
                params.update(force)
            else:
                params["force"] = force
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="DELETE",
            url=f"/bl/api/v2/workspaces/{workspace_id}/types/events/{event_type_id}",
            params=params,
            **kwargs,
        )

    @staticmethod
    def put_api_v2_workspaces_workspace_id_types_events_event_type_id_rename(
        client: Client,
        workspace_id: str,
        event_type_id: str,
        request_body: EntityRenameRequestOptions,
        force: Optional["bool"] = None,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> EventEntity:
        logger.debug(
            f"Request: 'PUT' -> '/bl/api/v2/workspaces/{workspace_id}/types/events/{event_type_id}/rename'",
            extra={
                "request_type": "PUT",
                "path": "/bl/api/v2/workspaces/{workspace_id}/types/events/{event_type_id}/rename",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if force is not None:
            if isinstance(force, PyCelonisBaseModel):
                params.update(force.json_dict(by_alias=True))
            elif isinstance(force, dict):
                params.update(force)
            else:
                params["force"] = force
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="PUT",
            url=f"/bl/api/v2/workspaces/{workspace_id}/types/events/{event_type_id}/rename",
            params=params,
            request_body=request_body,
            parse_json=True,
            type_=EventEntity,
            **kwargs,
        )

    @staticmethod
    def get_api_v2_workspaces_workspace_id_types_events_event_type_id_rename_dependencies(
        client: Client,
        workspace_id: str,
        event_type_id: str,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> None:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v2/workspaces/{workspace_id}/types/events/{event_type_id}/rename/dependencies'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v2/workspaces/{workspace_id}/types/events/{event_type_id}/rename/dependencies",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v2/workspaces/{workspace_id}/types/events/{event_type_id}/rename/dependencies",
            params=params,
            **kwargs,
        )

    @staticmethod
    def get_api_v2_workspaces_workspace_id_types_objects(
        client: Client,
        workspace_id: str,
        filter_options: Optional["EntityFilterOptions"] = None,
        pagination: Optional["Pagination"] = None,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> PageObjectEntity:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v2/workspaces/{workspace_id}/types/objects'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v2/workspaces/{workspace_id}/types/objects",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if filter_options is not None:
            if isinstance(filter_options, PyCelonisBaseModel):
                params.update(filter_options.json_dict(by_alias=True))
            elif isinstance(filter_options, dict):
                params.update(filter_options)
            else:
                params["filterOptions"] = filter_options
        if pagination is not None:
            if isinstance(pagination, PyCelonisBaseModel):
                params.update(pagination.json_dict(by_alias=True))
            elif isinstance(pagination, dict):
                params.update(pagination)
            else:
                params["pagination"] = pagination
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v2/workspaces/{workspace_id}/types/objects",
            params=params,
            parse_json=True,
            type_=PageObjectEntity,
            **kwargs,
        )

    @staticmethod
    def post_api_v2_workspaces_workspace_id_types_objects(
        client: Client,
        workspace_id: str,
        request_body: ObjectEntityRequestOptions,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> ObjectEntity:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v2/workspaces/{workspace_id}/types/objects'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v2/workspaces/{workspace_id}/types/objects",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="POST",
            url=f"/bl/api/v2/workspaces/{workspace_id}/types/objects",
            params=params,
            request_body=request_body,
            parse_json=True,
            type_=ObjectEntity,
            **kwargs,
        )

    @staticmethod
    def post_api_v2_workspaces_workspace_id_types_objects_batch(
        client: Client,
        workspace_id: str,
        request_body: List[Optional[ObjectEntityRequestOptions]],
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> List[Optional[ObjectEntity]]:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v2/workspaces/{workspace_id}/types/objects/batch'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v2/workspaces/{workspace_id}/types/objects/batch",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="POST",
            url=f"/bl/api/v2/workspaces/{workspace_id}/types/objects/batch",
            params=params,
            request_body=request_body,
            parse_json=True,
            type_=List[Optional[ObjectEntity]],
            **kwargs,
        )

    @staticmethod
    def post_api_v2_workspaces_workspace_id_types_objects_relationships(
        client: Client,
        workspace_id: str,
        request_body: ObjectRelationshipRequestOptions,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> ObjectRelationship:
        logger.debug(
            f"Request: 'POST' -> '/bl/api/v2/workspaces/{workspace_id}/types/objects/relationships'",
            extra={
                "request_type": "POST",
                "path": "/bl/api/v2/workspaces/{workspace_id}/types/objects/relationships",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="POST",
            url=f"/bl/api/v2/workspaces/{workspace_id}/types/objects/relationships",
            params=params,
            request_body=request_body,
            parse_json=True,
            type_=ObjectRelationship,
            **kwargs,
        )

    @staticmethod
    def get_api_v2_workspaces_workspace_id_types_objects_object_type_id(
        client: Client,
        workspace_id: str,
        object_type_id: str,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> ObjectEntity:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v2/workspaces/{workspace_id}/types/objects/{object_type_id}'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v2/workspaces/{workspace_id}/types/objects/{object_type_id}",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v2/workspaces/{workspace_id}/types/objects/{object_type_id}",
            params=params,
            parse_json=True,
            type_=ObjectEntity,
            **kwargs,
        )

    @staticmethod
    def put_api_v2_workspaces_workspace_id_types_objects_object_type_id(
        client: Client,
        workspace_id: str,
        object_type_id: str,
        request_body: ObjectEntityRequestOptions,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> ObjectEntity:
        logger.debug(
            f"Request: 'PUT' -> '/bl/api/v2/workspaces/{workspace_id}/types/objects/{object_type_id}'",
            extra={
                "request_type": "PUT",
                "path": "/bl/api/v2/workspaces/{workspace_id}/types/objects/{object_type_id}",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="PUT",
            url=f"/bl/api/v2/workspaces/{workspace_id}/types/objects/{object_type_id}",
            params=params,
            request_body=request_body,
            parse_json=True,
            type_=ObjectEntity,
            **kwargs,
        )

    @staticmethod
    def delete_api_v2_workspaces_workspace_id_types_objects_object_type_id(
        client: Client,
        workspace_id: str,
        object_type_id: str,
        force: Optional["bool"] = None,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> None:
        logger.debug(
            f"Request: 'DELETE' -> '/bl/api/v2/workspaces/{workspace_id}/types/objects/{object_type_id}'",
            extra={
                "request_type": "DELETE",
                "path": "/bl/api/v2/workspaces/{workspace_id}/types/objects/{object_type_id}",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if force is not None:
            if isinstance(force, PyCelonisBaseModel):
                params.update(force.json_dict(by_alias=True))
            elif isinstance(force, dict):
                params.update(force)
            else:
                params["force"] = force
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="DELETE",
            url=f"/bl/api/v2/workspaces/{workspace_id}/types/objects/{object_type_id}",
            params=params,
            **kwargs,
        )

    @staticmethod
    def get_api_v2_workspaces_workspace_id_types_objects_object_type_id_relationships(
        client: Client,
        workspace_id: str,
        object_type_id: str,
        pagination: Optional["Pagination"] = None,
        filter_bidirectional: Optional["bool"] = None,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> PageObjectRelationship:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v2/workspaces/{workspace_id}/types/objects/{object_type_id}/relationships'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v2/workspaces/{workspace_id}/types/objects/{object_type_id}/relationships",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if pagination is not None:
            if isinstance(pagination, PyCelonisBaseModel):
                params.update(pagination.json_dict(by_alias=True))
            elif isinstance(pagination, dict):
                params.update(pagination)
            else:
                params["pagination"] = pagination
        if filter_bidirectional is not None:
            if isinstance(filter_bidirectional, PyCelonisBaseModel):
                params.update(filter_bidirectional.json_dict(by_alias=True))
            elif isinstance(filter_bidirectional, dict):
                params.update(filter_bidirectional)
            else:
                params["filterBidirectional"] = filter_bidirectional
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v2/workspaces/{workspace_id}/types/objects/{object_type_id}/relationships",
            params=params,
            parse_json=True,
            type_=PageObjectRelationship,
            **kwargs,
        )

    @staticmethod
    def get_api_v2_workspaces_workspace_id_types_objects_object_type_id_relationships_incoming(
        client: Client,
        workspace_id: str,
        object_type_id: str,
        pagination: Optional["Pagination"] = None,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> PageObjectRelationship:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v2/workspaces/{workspace_id}/types/objects/{object_type_id}/relationships/incoming'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v2/workspaces/{workspace_id}/types/objects/{object_type_id}/relationships/incoming",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if pagination is not None:
            if isinstance(pagination, PyCelonisBaseModel):
                params.update(pagination.json_dict(by_alias=True))
            elif isinstance(pagination, dict):
                params.update(pagination)
            else:
                params["pagination"] = pagination
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v2/workspaces/{workspace_id}/types/objects/{object_type_id}/relationships/incoming",
            params=params,
            parse_json=True,
            type_=PageObjectRelationship,
            **kwargs,
        )

    @staticmethod
    def get_api_v2_workspaces_workspace_id_types_objects_object_type_id_relationships_outgoing(
        client: Client,
        workspace_id: str,
        object_type_id: str,
        pagination: Optional["Pagination"] = None,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> PageObjectRelationship:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v2/workspaces/{workspace_id}/types/objects/{object_type_id}/relationships/outgoing'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v2/workspaces/{workspace_id}/types/objects/{object_type_id}/relationships/outgoing",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if pagination is not None:
            if isinstance(pagination, PyCelonisBaseModel):
                params.update(pagination.json_dict(by_alias=True))
            elif isinstance(pagination, dict):
                params.update(pagination)
            else:
                params["pagination"] = pagination
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v2/workspaces/{workspace_id}/types/objects/{object_type_id}/relationships/outgoing",
            params=params,
            parse_json=True,
            type_=PageObjectRelationship,
            **kwargs,
        )

    @staticmethod
    def delete_api_v2_workspaces_workspace_id_types_objects_object_type_id_relationships_target_type_id(
        client: Client,
        workspace_id: str,
        object_type_id: str,
        target_type_id: str,
        relationship: Optional["str"] = None,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> None:
        logger.debug(
            f"Request: 'DELETE' -> '/bl/api/v2/workspaces/{workspace_id}/types/objects/{object_type_id}/relationships/{target_type_id}'",
            extra={
                "request_type": "DELETE",
                "path": "/bl/api/v2/workspaces/{workspace_id}/types/objects/{object_type_id}/relationships/{target_type_id}",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if relationship is not None:
            if isinstance(relationship, PyCelonisBaseModel):
                params.update(relationship.json_dict(by_alias=True))
            elif isinstance(relationship, dict):
                params.update(relationship)
            else:
                params["relationship"] = relationship
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="DELETE",
            url=f"/bl/api/v2/workspaces/{workspace_id}/types/objects/{object_type_id}/relationships/{target_type_id}",
            params=params,
            **kwargs,
        )

    @staticmethod
    def put_api_v2_workspaces_workspace_id_types_objects_object_type_id_rename(
        client: Client,
        workspace_id: str,
        object_type_id: str,
        request_body: EntityRenameRequestOptions,
        force: Optional["bool"] = None,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> ObjectEntity:
        logger.debug(
            f"Request: 'PUT' -> '/bl/api/v2/workspaces/{workspace_id}/types/objects/{object_type_id}/rename'",
            extra={
                "request_type": "PUT",
                "path": "/bl/api/v2/workspaces/{workspace_id}/types/objects/{object_type_id}/rename",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if force is not None:
            if isinstance(force, PyCelonisBaseModel):
                params.update(force.json_dict(by_alias=True))
            elif isinstance(force, dict):
                params.update(force)
            else:
                params["force"] = force
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="PUT",
            url=f"/bl/api/v2/workspaces/{workspace_id}/types/objects/{object_type_id}/rename",
            params=params,
            request_body=request_body,
            parse_json=True,
            type_=ObjectEntity,
            **kwargs,
        )

    @staticmethod
    def get_api_v2_workspaces_workspace_id_types_objects_object_type_id_rename_dependencies(
        client: Client,
        workspace_id: str,
        object_type_id: str,
        environment: Optional["str"] = None,
        **kwargs: Any,
    ) -> None:
        logger.debug(
            f"Request: 'GET' -> '/bl/api/v2/workspaces/{workspace_id}/types/objects/{object_type_id}/rename/dependencies'",
            extra={
                "request_type": "GET",
                "path": "/bl/api/v2/workspaces/{workspace_id}/types/objects/{object_type_id}/rename/dependencies",
                "tracking_type": "API_REQUEST",
            },
        )

        params: Dict[str, Any] = {}
        if environment is not None:
            if isinstance(environment, PyCelonisBaseModel):
                params.update(environment.json_dict(by_alias=True))
            elif isinstance(environment, dict):
                params.update(environment)
            else:
                params["environment"] = environment
        return client.request(
            method="GET",
            url=f"/bl/api/v2/workspaces/{workspace_id}/types/objects/{object_type_id}/rename/dependencies",
            params=params,
            **kwargs,
        )
