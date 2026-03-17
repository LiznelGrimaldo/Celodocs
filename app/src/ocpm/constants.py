"""String classes for OCPM related content"""


class Namespace:
    CUSTOM = ["custom"]
    CELONIS = ["celonis", "DuplicateInvoiceChecker"]


class NamespaceType:
    CUSTOM = "custom"
    CELONIS = "celonis"
    DUPLICATE_CHECKER = "DuplicateInvoiceChecker"


class Method:
    MERGE_OVERWRITE = "merge_overwrite"
    OVERWRITE = "overwrite"
    DEFAULT = "no_overwrite"


class EnvironmentName:
    PRODUCTION = "production"
    DEVELOPMENT = "develop"
