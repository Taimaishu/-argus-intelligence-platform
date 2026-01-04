/**
 * Force-directed layout hook using D3.js
 * Integrates D3 force simulation with React Flow
 */

import { useCallback, useRef } from 'react';
import * as d3 from 'd3';
import type { Node, Edge } from 'reactflow';

interface ForceLayoutOptions {
  strength?: number;
  distance?: number;
  iterations?: number;
  centerStrength?: number;
  collisionRadius?: number;
}

interface SimulationNode extends d3.SimulationNodeDatum {
  id: string;
  x: number;
  y: number;
}

export const useForceDirectedLayout = () => {
  const simulationRef = useRef<d3.Simulation<SimulationNode, undefined> | null>(null);

  /**
   * Apply force-directed layout to nodes based on edges
   */
  const applyLayout = useCallback(
    (
      nodes: Node[],
      edges: Edge[],
      options: ForceLayoutOptions = {}
    ): Promise<Node[]> => {
      return new Promise((resolve) => {
        // Default options
        const {
          strength = -300,
          distance = 150,
          iterations = 300,
          centerStrength = 0.1,
          collisionRadius = 80,
        } = options;

        // Stop any existing simulation
        if (simulationRef.current) {
          simulationRef.current.stop();
        }

        // Convert nodes to D3 format
        const simulationNodes: SimulationNode[] = nodes.map((node) => ({
          id: node.id,
          x: node.position.x,
          y: node.position.y,
        }));

        // Convert edges to D3 links format
        const links = edges.map((edge) => ({
          source: edge.source,
          target: edge.target,
          strength: (edge.data?.strength as number) || 0.5,
        }));

        // Create force simulation
        const simulation = d3
          .forceSimulation<SimulationNode>(simulationNodes)
          .force(
            'link',
            d3
              .forceLink(links)
              .id((d: any) => d.id)
              .distance(distance)
              .strength((d: any) => d.strength)
          )
          .force('charge', d3.forceManyBody().strength(strength))
          .force('center', d3.forceCenter(500, 400).strength(centerStrength))
          .force('collision', d3.forceCollide().radius(collisionRadius))
          .force('x', d3.forceX(500).strength(0.05))
          .force('y', d3.forceY(400).strength(0.05))
          .alphaDecay(0.02)
          .velocityDecay(0.3);

        simulationRef.current = simulation;

        // Run simulation for specified iterations
        simulation.tick(iterations);

        // Update node positions
        const updatedNodes = nodes.map((node) => {
          const simNode = simulationNodes.find((n) => n.id === node.id);
          if (simNode) {
            return {
              ...node,
              position: {
                x: simNode.x || node.position.x,
                y: simNode.y || node.position.y,
              },
            };
          }
          return node;
        });

        simulation.stop();
        resolve(updatedNodes);
      });
    },
    []
  );

  /**
   * Apply hierarchical layout for directed acyclic graphs
   */
  const applyHierarchicalLayout = useCallback(
    (nodes: Node[], edges: Edge[]): Node[] => {
      // Group nodes by their depth in the hierarchy
      const nodeDepths = new Map<string, number>();
      const visited = new Set<string>();

      // Find root nodes (nodes with no incoming edges)
      const incomingEdges = new Map<string, number>();
      nodes.forEach((node) => incomingEdges.set(node.id, 0));
      edges.forEach((edge) => {
        incomingEdges.set(edge.target, (incomingEdges.get(edge.target) || 0) + 1);
      });

      const rootNodes = nodes.filter((node) => incomingEdges.get(node.id) === 0);

      // BFS to assign depths
      const queue = rootNodes.map((node) => ({ id: node.id, depth: 0 }));

      while (queue.length > 0) {
        const { id, depth } = queue.shift()!;

        if (visited.has(id)) continue;
        visited.add(id);
        nodeDepths.set(id, depth);

        // Add children to queue
        const children = edges
          .filter((edge) => edge.source === id)
          .map((edge) => ({ id: edge.target, depth: depth + 1 }));

        queue.push(...children);
      }

      // Assign unvisited nodes to depth 0
      nodes.forEach((node) => {
        if (!nodeDepths.has(node.id)) {
          nodeDepths.set(node.id, 0);
        }
      });

      // Group nodes by depth
      const depthGroups = new Map<number, string[]>();
      nodeDepths.forEach((depth, nodeId) => {
        if (!depthGroups.has(depth)) {
          depthGroups.set(depth, []);
        }
        depthGroups.get(depth)!.push(nodeId);
      });

      // Position nodes
      const verticalSpacing = 200;
      const horizontalSpacing = 250;
      const startX = 100;
      const startY = 100;

      const updatedNodes = nodes.map((node) => {
        const depth = nodeDepths.get(node.id) || 0;
        const nodesAtDepth = depthGroups.get(depth) || [];
        const indexInDepth = nodesAtDepth.indexOf(node.id);

        return {
          ...node,
          position: {
            x: startX + depth * horizontalSpacing,
            y: startY + indexInDepth * verticalSpacing,
          },
        };
      });

      return updatedNodes;
    },
    []
  );

  /**
   * Apply circular layout
   */
  const applyCircularLayout = useCallback((nodes: Node[]): Node[] => {
    const radius = Math.max(300, nodes.length * 30);
    const centerX = 500;
    const centerY = 400;
    const angleStep = (2 * Math.PI) / nodes.length;

    return nodes.map((node, index) => ({
      ...node,
      position: {
        x: centerX + radius * Math.cos(index * angleStep),
        y: centerY + radius * Math.sin(index * angleStep),
      },
    }));
  }, []);

  /**
   * Apply grid layout
   */
  const applyGridLayout = useCallback((nodes: Node[]): Node[] => {
    const columns = Math.ceil(Math.sqrt(nodes.length));
    const horizontalSpacing = 250;
    const verticalSpacing = 200;
    const startX = 100;
    const startY = 100;

    return nodes.map((node, index) => ({
      ...node,
      position: {
        x: startX + (index % columns) * horizontalSpacing,
        y: startY + Math.floor(index / columns) * verticalSpacing,
      },
    }));
  }, []);

  /**
   * Stop any running simulation
   */
  const stopSimulation = useCallback(() => {
    if (simulationRef.current) {
      simulationRef.current.stop();
      simulationRef.current = null;
    }
  }, []);

  return {
    applyLayout,
    applyHierarchicalLayout,
    applyCircularLayout,
    applyGridLayout,
    stopSimulation,
  };
};
