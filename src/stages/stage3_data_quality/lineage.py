"""Data lineage tracking for data quality monitoring."""

from typing import Dict, List, Optional, Set, Union
import json
from datetime import datetime
import networkx as nx
from pyspark.sql import DataFrame
from pyspark.sql.functions import col, expr

class DataLineageTracker:
    """Track data lineage through the pipeline."""
    
    def __init__(self, lineage_path: str = "/tmp/data_lineage"):
        """Initialize the lineage tracker.
        
        Args:
            lineage_path: Path to store lineage information
        """
        self.lineage_path = lineage_path
        self.graph = nx.DiGraph()
        
    def add_source(
        self,
        source_id: str,
        source_type: str,
        location: str,
        schema: Optional[Dict] = None
    ) -> None:
        """Add a data source to the lineage graph.
        
        Args:
            source_id: Unique identifier for the source
            source_type: Type of data source
            location: Location/path of the source
            schema: Optional schema information
        """
        self.graph.add_node(
            source_id,
            node_type="source",
            source_type=source_type,
            location=location,
            schema=schema,
            created_at=datetime.now().isoformat()
        )
        
    def add_transformation(
        self,
        transformation_id: str,
        transformation_type: str,
        inputs: List[str],
        outputs: List[str],
        parameters: Optional[Dict] = None
    ) -> None:
        """Add a transformation to the lineage graph.
        
        Args:
            transformation_id: Unique identifier for the transformation
            transformation_type: Type of transformation
            inputs: List of input node IDs
            outputs: List of output node IDs
            parameters: Optional transformation parameters
        """
        # Add transformation node
        self.graph.add_node(
            transformation_id,
            node_type="transformation",
            transformation_type=transformation_type,
            parameters=parameters,
            created_at=datetime.now().isoformat()
        )
        
        # Add edges from inputs to transformation
        for input_id in inputs:
            self.graph.add_edge(
                input_id,
                transformation_id,
                edge_type="input",
                created_at=datetime.now().isoformat()
            )
        
        # Add edges from transformation to outputs
        for output_id in outputs:
            self.graph.add_edge(
                transformation_id,
                output_id,
                edge_type="output",
                created_at=datetime.now().isoformat()
            )
            
    def add_quality_check(
        self,
        check_id: str,
        check_type: str,
        target_id: str,
        results: Dict[str, Union[float, str]],
        parameters: Optional[Dict] = None
    ) -> None:
        """Add a quality check to the lineage graph.
        
        Args:
            check_id: Unique identifier for the check
            check_type: Type of quality check
            target_id: ID of the node being checked
            results: Results of the quality check
            parameters: Optional check parameters
        """
        # Add quality check node
        self.graph.add_node(
            check_id,
            node_type="quality_check",
            check_type=check_type,
            results=results,
            parameters=parameters,
            created_at=datetime.now().isoformat()
        )
        
        # Add edge from target to quality check
        self.graph.add_edge(
            target_id,
            check_id,
            edge_type="quality_check",
            created_at=datetime.now().isoformat()
        )
        
    def get_upstream_nodes(self, node_id: str) -> Set[str]:
        """Get all upstream nodes for a given node.
        
        Args:
            node_id: ID of the node
            
        Returns:
            Set of upstream node IDs
        """
        return set(nx.ancestors(self.graph, node_id))
    
    def get_downstream_nodes(self, node_id: str) -> Set[str]:
        """Get all downstream nodes for a given node.
        
        Args:
            node_id: ID of the node
            
        Returns:
            Set of downstream node IDs
        """
        return set(nx.descendants(self.graph, node_id))
    
    def get_node_history(self, node_id: str) -> List[Dict]:
        """Get the complete history of a node.
        
        Args:
            node_id: ID of the node
            
        Returns:
            List of historical events
        """
        history = []
        
        # Get node attributes
        node_attrs = self.graph.nodes[node_id]
        history.append({
            "event_type": "creation",
            "timestamp": node_attrs["created_at"],
            "details": node_attrs
        })
        
        # Get incoming edges (transformations)
        for pred in self.graph.predecessors(node_id):
            edge_attrs = self.graph.edges[(pred, node_id)]
            pred_attrs = self.graph.nodes[pred]
            history.append({
                "event_type": "input_from",
                "timestamp": edge_attrs["created_at"],
                "source": pred,
                "details": pred_attrs
            })
        
        # Get outgoing edges (downstream usage)
        for succ in self.graph.successors(node_id):
            edge_attrs = self.graph.edges[(node_id, succ)]
            succ_attrs = self.graph.nodes[succ]
            history.append({
                "event_type": "output_to",
                "timestamp": edge_attrs["created_at"],
                "target": succ,
                "details": succ_attrs
            })
            
        return sorted(history, key=lambda x: x["timestamp"])
    
    def save_lineage(self) -> None:
        """Save the lineage graph to storage."""
        timestamp = datetime.now().isoformat()
        
        # Convert graph to dictionary
        graph_dict = {
            "nodes": dict(self.graph.nodes(data=True)),
            "edges": [
                {
                    "source": u,
                    "target": v,
                    **d
                }
                for u, v, d in self.graph.edges(data=True)
            ]
        }
        
        # Save to file
        with open(f"{self.lineage_path}/lineage_{timestamp}.json", "w") as f:
            json.dump(graph_dict, f, indent=2)
            
    def load_lineage(self, file_path: str) -> None:
        """Load a lineage graph from storage.
        
        Args:
            file_path: Path to the lineage file
        """
        with open(file_path, "r") as f:
            graph_dict = json.load(f)
            
        # Create new graph
        self.graph = nx.DiGraph()
        
        # Add nodes
        for node_id, attrs in graph_dict["nodes"].items():
            self.graph.add_node(node_id, **attrs)
            
        # Add edges
        for edge in graph_dict["edges"]:
            self.graph.add_edge(
                edge["source"],
                edge["target"],
                **{k: v for k, v in edge.items() if k not in ["source", "target"]}
            )
            
    def visualize_lineage(self, output_path: str) -> None:
        """Generate a visualization of the lineage graph.
        
        Args:
            output_path: Path to save the visualization
        """
        import matplotlib.pyplot as plt
        
        # Create layout
        pos = nx.spring_layout(self.graph)
        
        # Draw nodes
        nx.draw_networkx_nodes(
            self.graph, pos,
            node_color="lightblue",
            node_size=1000
        )
        
        # Draw edges
        nx.draw_networkx_edges(
            self.graph, pos,
            edge_color="gray",
            arrows=True
        )
        
        # Add labels
        nx.draw_networkx_labels(self.graph, pos)
        
        # Save plot
        plt.savefig(output_path)
        plt.close() 