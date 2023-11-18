from dataclasses import dataclass
from typing import Self, TypeAlias, Any
from xml.etree.ElementTree import Element
import xml.etree.ElementTree as ET

JSON: TypeAlias = dict[str, Any]


@dataclass
class Scenario:
    """Represents a delivery scenario."""

    name: str

    @classmethod
    def from_name(cls, name: str) -> Self:
        # Parse XML graph first
        tree = ET.parse(f"{name}.xml")
        root = tree.getroot()
        nodes: list[Nodes] = [Node.from_xml(n) for n in root.findall("node")]
        print(nodes)

        return cls(
            name=name,
        )


@dataclass
class Package:
    """Represents a package to be delivered."""

    source: int
    destination: int

    @classmethod
    def from_json(cls, data: JSON) -> Self:
        return cls(source=data["source"], destination=data["destination"])


@dataclass
class Bot:
    """Represents a delivery robot who can carry packages."""

    location: int
    capacity: int
    carrying: list[Package]

    @classmethod
    def from_json(cls, data: JSON) -> Self:
        return cls(location=data["location"], capacity=data["capacity"], carrying=[])


@dataclass
class Node:
    """Represents a node in the simulation."""

    id: int
    lat: float
    long: float

    @classmethod
    def from_xml(cls, node: Element) -> Self:
        lat = node.find("lat")
        long = node.find("lon")

        if lat is None:
            raise ValueError("No latitude node found.")

        if long is None:
            raise ValueError("No longitude node found.")

        return cls(
            id=node.get("id"),
            lat=float(lat.text),  # type:ignore
            long=float(long.text),  # type:ignore
        )
