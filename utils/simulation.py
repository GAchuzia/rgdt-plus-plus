from dataclasses import dataclass, field
from typing import Self, TypeAlias, Any
from xml.etree.ElementTree import Element
import xml.etree.ElementTree as ET
import math
import json
from enum import Enum, auto

JSON: TypeAlias = dict[str, Any]
EARTH_RADIUS: float = 6371  # In km
BOT_SPEED: float = 40  # kmph


class PackageState(Enum):
    PICKED_UP = auto()
    DELIVERED = auto()
    UNMOVED = auto()


@dataclass
class Way:
    id: int
    nodes: tuple[int, int]
    cost: float

    @classmethod
    def from_xml(cls, data: Element) -> Self:
        nodes = [int(node.text) for node in data.findall("node")]  # type: ignore
        return cls(id=data.get("id"), nodes=tuple(nodes), cost=0)  # type: ignore


@dataclass
class Package:
    """Represents a package to be delivered."""

    source: int
    destination: int
    state: PackageState

    @classmethod
    def from_json(cls, data: JSON) -> Self:
        return cls(source=data["source"], destination=data["destination"], state=PackageState.UNMOVED)


@dataclass
class Bot:
    """Represents a delivery robot who can carry packages."""

    location: int
    capacity: int
    carrying: list[Package]
    accumulated_cost: float

    @classmethod
    def from_json(cls, data: JSON) -> Self:
        return cls(location=data["location"], capacity=data["capacity"], carrying=[], accumulated_cost=0)


@dataclass
class Node:
    """Represents a node in the simulation."""

    id: int
    lat: float
    long: float
    ways: list[Way]

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

    def add_way(self, way: Way) -> None:
        """Adds a way between nodes."""
        self.ways.append(way)


@dataclass
class Scenario:
    """Represents a delivery scenario."""

    name: str
    nodes: dict[int, Node] = field(default_factory=dict)
    bots: list[Bot] = field(default_factory=list)
    packages: list[Package] = field(default_factory=list)

    @classmethod
    def from_name(cls, name: str) -> Self:
        # Parse XML graph first
        tree = ET.parse(f"{name}.xml")
        root = tree.getroot()

        # Create nodes
        nodes: dict[int, Node] = {}
        for n in root.findall("node"):
            node = Node.from_xml(n)
            nodes[node.id] = node

        # Add ways
        for w in root.findall("way"):
            way = Way.from_xml(w)
            n1, n2 = way.nodes
            node1, node2 = nodes[n1], nodes[n2]
            way.cost = haversine_dist(node1, node2)
            node1.add_way(way)
            node2.add_way(way)

        # Parse JSON
        bots: list[Bot] = []
        packages: list[Package] = []
        with open(f"{name}.json", "r") as file:
            data = json.loads(file)  # type: ignore

            for bot in data["bots"]:
                bots.append(Bot.from_json(bot))

            for pkg in data["packages"]:
                packages.append(Package.from_json(pkg))

        return cls(
            name=name,
            nodes=nodes,
            bots=bots,
            packages=packages,
        )


def haversine_dist(n1: Node, n2: Node) -> float:
    """Calculates the distance between two nodes using the haversine formula. Distance is returned in km."""
    firsts2 = math.sin((math.radians(n2.lat) - math.radians(n1.lat)) / 2) ** 2
    seconds2 = math.sin((math.radians(n2.long) - math.radians(n1.long)) / 2) ** 2
    cosproduct = math.cos(math.radians(n1.lat)) * math.cos(math.radians(n2.lat))
    return 2 * EARTH_RADIUS * math.asin(math.sqrt(firsts2 + cosproduct * seconds2))
