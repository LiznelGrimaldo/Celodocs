from dataclasses import dataclass, field
from typing import List, Dict
import json


@dataclass
class Factory:
    factory_id: str
    data_connection_id: str

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


@dataclass
class Table:
    name: str
    columns: List[str] = field(default_factory=list)

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


@dataclass
class Event:
    name: str
    relationship_with_object: str

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


@dataclass
class Object:
    name: str
    factory: Factory
    sql_statements: List[str] = field(default_factory=list)
    tables: List[Table] = field(default_factory=list)
    events: List[Event] = field(default_factory=list)
    columns_aliases: Dict[str, List] = field(default_factory=dict)
    columns_aliases_by_script: [List] = field(default_factory=list)

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


@dataclass
class Process:
    name: str
    objects: List[Object]
    events: List[Event]
    columns: List[str] = field(default_factory=list)

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


@dataclass
class App:
    name: str
    objects: List[Object]

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
