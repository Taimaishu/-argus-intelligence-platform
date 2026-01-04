"""Canvas generation service for converting knowledge graphs to canvas format."""

from typing import List, Dict, Any, Optional, Tuple
import random
import math
import networkx as nx
from dataclasses import dataclass

from app.core.knowledge_graph_service import KnowledgeGraph, KnowledgeGraphService
from app.utils.logger import logger


@dataclass
class NodePosition:
    """Position of a node on the canvas."""
    node_id: str
    x: float
    y: float


class CanvasGenerationService:
    """Service for generating canvas layouts from knowledge graphs."""

    def __init__(self, kg_service: KnowledgeGraphService):
        """Initialize canvas generation service."""
        self.kg_service = kg_service
        self.canvas_width = 1920
        self.canvas_height = 1080
        self.default_node_spacing = 200

    def generate_canvas_from_graph(
        self,
        graph: KnowledgeGraph,
        layout_type: str = "force_directed"
    ) -> Dict[str, Any]:
        """
        Generate canvas data from knowledge graph.

        Args:
            graph: Knowledge graph to convert
            layout_type: Type of layout algorithm to use

        Returns:
            Canvas data with positioned nodes and edges
        """
        try:
            # Get base canvas data (nodes and edges)
            canvas_data = self.kg_service.get_graph_data(graph)

            # Apply layout algorithm
            if layout_type == "force_directed":
                positions = self.apply_force_directed_layout(
                    canvas_data["nodes"],
                    canvas_data["edges"]
                )
            elif layout_type == "hierarchical":
                positions = self.apply_hierarchical_layout(
                    canvas_data["nodes"],
                    canvas_data["edges"]
                )
            elif layout_type == "circular":
                positions = self.apply_circular_layout(canvas_data["nodes"])
            else:
                positions = self.apply_random_layout(canvas_data["nodes"])

            # Update node positions
            position_map = {pos.node_id: (pos.x, pos.y) for pos in positions}
            for node in canvas_data["nodes"]:
                if node["id"] in position_map:
                    x, y = position_map[node["id"]]
                    node["position"] = {"x": x, "y": y}

            logger.info(f"Generated canvas with {len(canvas_data['nodes'])} nodes, {len(canvas_data['edges'])} edges")
            return canvas_data

        except Exception as e:
            logger.error(f"Canvas generation failed: {e}")
            raise

    def apply_force_directed_layout(
        self,
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]],
        iterations: int = 50
    ) -> List[NodePosition]:
        """
        Apply force-directed layout algorithm.

        Args:
            nodes: List of nodes
            edges: List of edges
            iterations: Number of iterations for the algorithm

        Returns:
            List of node positions
        """
        try:
            # Create NetworkX graph
            G = nx.Graph()

            # Add nodes
            for node in nodes:
                G.add_node(node["id"])

            # Add edges with weights
            for edge in edges:
                weight = edge.get("data", {}).get("strength", 0.5)
                G.add_edge(edge["source"], edge["target"], weight=weight)

            # Use NetworkX spring layout (force-directed)
            # k controls the ideal distance between nodes
            k = self.default_node_spacing / math.sqrt(len(nodes)) if nodes else 1
            pos = nx.spring_layout(
                G,
                k=k,
                iterations=iterations,
                scale=min(self.canvas_width, self.canvas_height) / 2,
                center=(self.canvas_width / 2, self.canvas_height / 2)
            )

            # Convert to NodePosition objects
            positions = []
            for node_id, (x, y) in pos.items():
                positions.append(NodePosition(
                    node_id=node_id,
                    x=float(x),
                    y=float(y)
                ))

            logger.info(f"Applied force-directed layout to {len(positions)} nodes")
            return positions

        except Exception as e:
            logger.error(f"Force-directed layout failed: {e}")
            # Fallback to random layout
            return self.apply_random_layout(nodes)

    def apply_hierarchical_layout(
        self,
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]]
    ) -> List[NodePosition]:
        """
        Apply hierarchical (tree-like) layout.

        Args:
            nodes: List of nodes
            edges: List of edges

        Returns:
            List of node positions
        """
        try:
            # Create directed graph
            G = nx.DiGraph()

            for node in nodes:
                G.add_node(node["id"])

            for edge in edges:
                G.add_edge(edge["source"], edge["target"])

            # Use multipartite layout if graph is DAG
            if nx.is_directed_acyclic_graph(G):
                # Assign layers based on longest path from roots
                layers = {}
                roots = [n for n in G.nodes() if G.in_degree(n) == 0]

                if not roots:
                    # No clear hierarchy, use spring layout
                    return self.apply_force_directed_layout(nodes, edges)

                for root in roots:
                    layers[root] = 0

                # BFS to assign layers
                visited = set(roots)
                queue = roots.copy()

                while queue:
                    current = queue.pop(0)
                    current_layer = layers[current]

                    for neighbor in G.successors(current):
                        if neighbor not in visited:
                            visited.add(neighbor)
                            layers[neighbor] = current_layer + 1
                            queue.append(neighbor)

                # Set subset attribute for multipartite layout
                for node, layer in layers.items():
                    G.nodes[node]["subset"] = layer

                pos = nx.multipartite_layout(G, subset_key="subset")

                # Scale positions - make it wide and spread out horizontally
                positions = []
                for node_id, (x, y) in pos.items():
                    # Swap x and y for horizontal flow (left-to-right)
                    # Scale x much wider for spreading out
                    positions.append(NodePosition(
                        node_id=node_id,
                        x=y * self.canvas_width * 2.5,  # Horizontal spread (was vertical)
                        y=x * self.canvas_height * 0.8  # Vertical positioning (was horizontal)
                    ))

                logger.info(f"Applied hierarchical layout (horizontal flow) to {len(positions)} nodes")
                return positions
            else:
                # Not a DAG, use spring layout
                return self.apply_force_directed_layout(nodes, edges)

        except Exception as e:
            logger.error(f"Hierarchical layout failed: {e}")
            return self.apply_force_directed_layout(nodes, edges)

    def apply_circular_layout(self, nodes: List[Dict[str, Any]]) -> List[NodePosition]:
        """
        Apply circular layout.

        Args:
            nodes: List of nodes

        Returns:
            List of node positions
        """
        positions = []
        n = len(nodes)

        if n == 0:
            return positions

        # Calculate radius
        radius = min(self.canvas_width, self.canvas_height) * 0.4
        center_x = self.canvas_width / 2
        center_y = self.canvas_height / 2

        # Place nodes in a circle
        for i, node in enumerate(nodes):
            angle = (2 * math.pi * i) / n
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)

            positions.append(NodePosition(
                node_id=node["id"],
                x=x,
                y=y
            ))

        logger.info(f"Applied circular layout to {len(positions)} nodes")
        return positions

    def apply_random_layout(self, nodes: List[Dict[str, Any]]) -> List[NodePosition]:
        """
        Apply random layout (fallback).

        Args:
            nodes: List of nodes

        Returns:
            List of node positions
        """
        positions = []

        for node in nodes:
            x = random.uniform(100, self.canvas_width - 100)
            y = random.uniform(100, self.canvas_height - 100)

            positions.append(NodePosition(
                node_id=node["id"],
                x=x,
                y=y
            ))

        logger.info(f"Applied random layout to {len(positions)} nodes")
        return positions

    def optimize_layout(
        self,
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]],
        iterations: int = 100
    ) -> List[NodePosition]:
        """
        Optimize layout to minimize edge crossings and improve readability.

        Args:
            nodes: List of nodes with current positions
            edges: List of edges
            iterations: Number of optimization iterations

        Returns:
            Optimized node positions
        """
        # Get current positions
        positions = {
            node["id"]: (node["position"]["x"], node["position"]["y"])
            for node in nodes
        }

        # Build adjacency list
        adjacency = {node["id"]: [] for node in nodes}
        for edge in edges:
            adjacency[edge["source"]].append(edge["target"])
            adjacency[edge["target"]].append(edge["source"])

        # Simulated annealing for optimization
        temperature = 100.0
        cooling_rate = 0.95

        for iteration in range(iterations):
            # Pick random node
            node_id = random.choice([n["id"] for n in nodes])

            # Calculate current energy (edge length + crossings)
            old_energy = self._calculate_energy(node_id, positions, adjacency)

            # Perturb position
            old_pos = positions[node_id]
            new_x = old_pos[0] + random.gauss(0, temperature)
            new_y = old_pos[1] + random.gauss(0, temperature)

            # Clamp to canvas bounds
            new_x = max(100, min(self.canvas_width - 100, new_x))
            new_y = max(100, min(self.canvas_height - 100, new_y))

            positions[node_id] = (new_x, new_y)

            # Calculate new energy
            new_energy = self._calculate_energy(node_id, positions, adjacency)

            # Accept or reject
            energy_diff = new_energy - old_energy
            if energy_diff > 0 and random.random() > math.exp(-energy_diff / temperature):
                # Reject: revert position
                positions[node_id] = old_pos

            # Cool down
            temperature *= cooling_rate

        # Convert to NodePosition objects
        return [
            NodePosition(node_id=node_id, x=x, y=y)
            for node_id, (x, y) in positions.items()
        ]

    def _calculate_energy(
        self,
        node_id: str,
        positions: Dict[str, Tuple[float, float]],
        adjacency: Dict[str, List[str]]
    ) -> float:
        """Calculate energy for a node (lower is better)."""
        energy = 0.0
        x, y = positions[node_id]

        # Edge length energy (prefer shorter edges)
        for neighbor_id in adjacency.get(node_id, []):
            if neighbor_id in positions:
                nx, ny = positions[neighbor_id]
                distance = math.sqrt((x - nx)**2 + (y - ny)**2)
                energy += distance

        # Node repulsion (prefer spacing)
        for other_id, (ox, oy) in positions.items():
            if other_id != node_id:
                distance = math.sqrt((x - ox)**2 + (y - oy)**2)
                if distance < self.default_node_spacing:
                    energy += (self.default_node_spacing - distance)

        return energy

    def cluster_by_entity_type(
        self,
        graph: KnowledgeGraph
    ) -> Dict[str, List[NodePosition]]:
        """
        Cluster nodes by entity type with separate layouts per cluster.

        Args:
            graph: Knowledge graph

        Returns:
            Dictionary mapping entity types to node positions
        """
        # Group entities by type
        entities_by_type = {}
        for entity in graph.entities:
            entity_type = entity.type.value
            if entity_type not in entities_by_type:
                entities_by_type[entity_type] = []
            entities_by_type[entity_type].append(entity)

        # Calculate cluster centers
        n_clusters = len(entities_by_type)
        cluster_positions = {}

        for i, (entity_type, entities) in enumerate(entities_by_type.items()):
            # Position clusters in a circle
            angle = (2 * math.pi * i) / n_clusters
            cluster_radius = min(self.canvas_width, self.canvas_height) * 0.3
            cluster_center_x = self.canvas_width / 2 + cluster_radius * math.cos(angle)
            cluster_center_y = self.canvas_height / 2 + cluster_radius * math.sin(angle)

            # Layout entities within cluster
            cluster_size = len(entities)
            entity_positions = []

            for j, entity in enumerate(entities):
                # Circular layout within cluster
                entity_angle = (2 * math.pi * j) / cluster_size
                entity_radius = 50 + cluster_size * 5  # Adjust based on cluster size
                x = cluster_center_x + entity_radius * math.cos(entity_angle)
                y = cluster_center_y + entity_radius * math.sin(entity_angle)

                entity_positions.append(NodePosition(
                    node_id=f"{entity_type}-{j}",
                    x=x,
                    y=y
                ))

            cluster_positions[entity_type] = entity_positions

        return cluster_positions
