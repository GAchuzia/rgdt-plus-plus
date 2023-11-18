from dataclasses import dataclass
from typing import Self, TypeAlias, Any
from xml.etree.ElementTree import Element
import xml.etree.ElementTree as ET
import math

JSON: TypeAlias = dict[str, Any]
EARTH_RADIUS: float = 6371  # In km


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
class Ways:
    id: int
    nodes: tuple[int, int]
    cost: float

    @classmethod
    def from_xml(cls, data: Element) -> Self:
        nodes = [int(node.text) for node in data.findall("node")]  # type: ignore

        return cls(id=data.get("id"), nodes=tuple(nodes), cost=0)


@dataclass
class Node:
    """Represents a node in the simulation."""

    id: int
    lat: float
    long: float
    ways: list[Ways]

    @classmethod
    def from_xml(cls, data: Element) -> Self:
        lat = data.find("lat")
        long = data.find("lon")

        if lat is None:
            raise ValueError("No latitude node found.")

        if long is None:
            raise ValueError("No longitude node found.")

        return cls(
            id=data.get("id"),
            lat=float(lat.text),  # type:ignore
            long=float(long.text),  # type:ignore
            ways=[],
        )


def haversine_dist(n1: Node, n2: Node) -> float:
    """Calculates the distance between two nodes."""
    firsts2 = math.sin((math.radians(n2.lat) - math.radians(n1.lat)) / 2) ** 2
    seconds2 = math.sin((math.radians(n2.long) - math.radians(n1.long)) / 2) ** 2
    cosproduct = math.cos(math.radians(n1.lat)) * math.cos(math.radians(n2.lat))
    return 2 * EARTH_RADIUS * math.asin(math.sqrt(firsts2 + cosproduct * seconds2))
