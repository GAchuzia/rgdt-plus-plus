from __future__ import annotations
from dataclasses import dataclass, field
from typing import Self, TypeAlias, Any, Optional
from xml.etree.ElementTree import Element
import xml.etree.ElementTree as ET
import math
import json
import heapq
from enum import Enum, auto

JSON: TypeAlias = dict[str, Any]
NodeID: TypeAlias = int
NodeDistances: TypeAlias = dict[NodeID, float]

EARTH_RADIUS: float = 6371  # In km
BOT_SPEED: float = 40  # kmph
DELIVERY_TIME: float = 2 / 60  # hours


class PackageState(Enum):
    PICKED_UP = auto()
    DELIVERED = auto()
    UNMOVED = auto()
    CLAIMED = auto()


@dataclass
class Way:
    id: int
    nodes: tuple[int, int]
    cost: float

    @classmethod
    def from_xml(cls, data: Element) -> Self:
        nodes = [int(node.text) for node in data.findall("node")]  # type: ignore
        return cls(id=int(data.get("id")), nodes=tuple(nodes), cost=0)  # type: ignore


@dataclass
class Package:
    """Represents a package to be delivered."""

    source: int
    destination: int
    state: PackageState
    claimed: Optional[int] = None  # ID of robot who has claimed this package

    @classmethod
    def from_json(cls, data: JSON) -> Self:
        return cls(source=data["source"], destination=data["destination"], state=PackageState.UNMOVED)

    def claim(self, robot_id: int) -> None:
        """Mark the package as claimed."""
        self.state = PackageState.CLAIMED
        self.claimed = robot_id

    def delivered(self) -> None:
        """Mark the package as delivered."""
        self.state = PackageState.DELIVERED

    def __str__(self) -> str:
        return f"Pkg({self.state}, {self.destination})"

    __repr__ = __str__


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
            id=int(data.get("id")),  # type:ignore
            lat=float(lat.text),  # type:ignore
            long=float(long.text),  # type:ignore
            ways=[],
        )

    def add_way(self, way: Way) -> None:
        """Adds a way between nodes."""
        self.ways.append(way)

    def __str__(self) -> str:
        return f"Node(id={self.id})"

    __repr__ = __str__


@dataclass
class DijkstraNode:
    ref: Node
    distance: float = float("inf")
    finished: bool = False
    parent: Optional[Self] = None

    def __str__(self) -> str:
        return f"DNode(time={self.distance:.2f})"

    __repr__ = __str__


def dijkstra(graph: dict[NodeID, Node], source: Node) -> NodeDistances:
    """
    Djikstra's algorithm.
    https://builtin.com/software-engineering-perspectives/dijkstras-algorithm
    """
    nodes: dict[int, DijkstraNode] = {}
    for node in graph.values():
        nodes[node.id] = DijkstraNode(ref=node)

    nodes[source.id].distance = 0
    queue: list[tuple[float, DijkstraNode]] = [(0, DijkstraNode(ref=source))]  # priority queue

    while queue:
        d, node = heapq.heappop(queue)
        if nodes[node.ref.id].finished:
            continue
        nodes[node.ref.id].finished = True

        for way in graph[node.ref.id].ways:
            if way.nodes[0] == node.ref.id:
                neighbor = way.nodes[1]
            else:
                neighbor = way.nodes[0]

            if nodes[neighbor].finished:
                continue

            new_d = d + haversine_dist(node.ref, graph[neighbor]) * (1 / BOT_SPEED)

            if new_d < nodes[neighbor].distance:
                nodes[neighbor].distance = new_d
                nodes[neighbor].parent = node
                heapq.heappush(queue, (new_d, nodes[neighbor]))

    # Only return distances
    return {k: v.distance for k, v in nodes.items()}


@dataclass
class Bot:
    """Represents a delivery robot who can carry packages."""

    id: int
    location: int
    capacity: int
    accumulated_cost: float
    num_deliveries: int
    carrying: list[Package] = field(default_factory=list)

    @classmethod
    def from_json(cls, id: int, data: JSON) -> Self:
        return cls(
            id=id,
            location=data["location"],
            capacity=data["capacity"],
            accumulated_cost=0,
            num_deliveries=0,
        )

    def has_room(self) -> bool:
        """Returns true if the robot has room to carry another package."""
        return len(self.carrying) < self.capacity

    def calculate_destination(self, scenario: Scenario) -> int:
        """
        Returns the ideal node to travel to for collecting or delivering a package.
        Simultaneously delivers any packages required at this node and picks up packages if it has capacity.
        """

        # Drop off any packages at the current node
        for pkg in self.carrying:
            if pkg.destination == self.location:
                pkg.delivered()
                self.carrying.remove(pkg)
                self.num_deliveries += 1
                self.accumulated_cost += DELIVERY_TIME

        # Pick up any packages at the current node
        for pkg in scenario.packages:
            unmoved = pkg.state == PackageState.UNMOVED and pkg.source == self.location
            self_claimed = pkg.state == PackageState.CLAIMED and pkg.claimed == self.id and pkg.source == self.location
            if (unmoved or self_claimed) and self.has_room():
                pkg.state = PackageState.PICKED_UP
                self.carrying.append(pkg)

        # Picking a package closest to the bot
        dists = scenario.computed_dists.get(self.location)
        if dists is None:  # Only compute if not computed before
            dists = dijkstra(scenario.nodes, scenario.nodes[self.location])
            scenario.computed_dists[self.location] = dists

        candidate: tuple[float, int, Package] = (float("inf"), scenario.packages[0].source, scenario.packages[0])
        for pkg in scenario.packages:
            # If we have room to take a package or we've claimed it, head to pick up the closest one
            self_claimed = pkg.state == PackageState.CLAIMED and pkg.claimed == self.id
            unmoved = pkg.state == PackageState.UNMOVED
            if (unmoved or self_claimed) and self.has_room():
                if dists[pkg.source] < candidate[0]:
                    candidate = (dists[pkg.source], pkg.source, pkg)

            # If we're carrying packages, go to the carried package destination that's closest
            if pkg in self.carrying:
                if dists[pkg.destination] < candidate[0]:
                    candidate = (dists[pkg.destination], pkg.destination, pkg)

        # Package has been picked
        if candidate[2].state == PackageState.UNMOVED:
            candidate[2].claim(self.id)
        return candidate[1]

    def step_towards(self, target_id: int, scenario: Scenario) -> None:
        """Take a step to the next node in the path to the node which is associated with the ID provided."""

        # Distances from target to all nodes
        distances = scenario.computed_dists.get(target_id)
        if distances is None:
            distances = dijkstra(scenario.nodes, scenario.nodes[target_id])
            scenario.computed_dists[target_id] = distances

        current_node = scenario.nodes[self.location]
        candidate: tuple[float, int, Way] = (float("inf"), self.location, scenario.nodes[self.location].ways[0])

        # Find the minimum distance to our next step to the target node
        for way in current_node.ways:
            if way.nodes[0] == self.location:
                adjacent = way.nodes[1]
            else:
                adjacent = way.nodes[0]

            if distances[adjacent] < candidate[0]:
                candidate = (distances[adjacent], adjacent, way)

        # Found ideal step
        self.accumulated_cost += candidate[2].cost
        self.location = candidate[1]


@dataclass
class Scenario:
    """Represents a delivery scenario."""

    name: str
    nodes: dict[NodeID, Node] = field(default_factory=dict)
    bots: list[Bot] = field(default_factory=list)
    packages: list[Package] = field(default_factory=list)
    computed_dists: dict[NodeID, NodeDistances] = field(default_factory=dict)

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
            way.cost = haversine_dist(node1, node2) * (1 / BOT_SPEED)
            node1.add_way(way)
            node2.add_way(way)

        # Parse JSON
        bots: list[Bot] = []
        packages: list[Package] = []
        with open(f"{name}.json", "r") as file:
            data = json.load(file)

            for bot, _id in enumerate(data["bots"]):
                bots.append(Bot.from_json(bot, _id))

            for pkg in data["packages"]:
                packages.append(Package.from_json(pkg))

        return cls(
            name=name,
            nodes=nodes,
            bots=bots,
            packages=packages,
        )

    def complete(self) -> bool:
        """Returns true when all packages are delivered."""
        delivered_status = [pkg.state == PackageState.DELIVERED for pkg in self.packages]
        print(f"Packages remaining {len(self.packages) - sum(delivered_status)}")
        return all(delivered_status)


def haversine_dist(n1: Node, n2: Node) -> float:
    """Calculates the distance between two nodes using the haversine formula. Distance is returned in km."""
    firsts2 = math.sin((math.radians(n2.lat) - math.radians(n1.lat)) / 2) ** 2
    seconds2 = math.sin((math.radians(n2.long) - math.radians(n1.long)) / 2) ** 2
    cosproduct = math.cos(math.radians(n1.lat)) * math.cos(math.radians(n2.lat))
    return 2 * EARTH_RADIUS * math.asin(math.sqrt(firsts2 + cosproduct * seconds2))
