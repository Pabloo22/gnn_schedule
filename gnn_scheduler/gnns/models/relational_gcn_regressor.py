from typing import Optional

import torch
from torch import nn

from gnn_scheduler.gnns.models import (
    GraphAggregationLayer,
    MultiGraphConvolutionLayers,
)


class RelationalGCNRegressor(nn.Module):
    """
    A regression model that processes graphs with two types of edges using a
    relational graph convolutional network (GCN).

    Attributes:
        graph_conv (MultiGraphConvolutionLayers): The graph convolution layers.
        aggregation_layer (GraphAggregationLayer): The layer that aggregates node embeddings.
    """

    def __init__(
        self,
        in_features: int,
        conv_units: list[int],
        aggregation_units: int,
        dropout_rate: float = 0.0,
        leaky_relu_slope: float = 0.1,
        with_features: bool = False,
        feature_dim_size: int = 0,
    ):
        """Initializes the RelationalGCNRegressor model.

        Args:
            in_features (int): The number of features in each input node
                embedding.
            conv_units ([int]): List of units in each graph convolution layer.
            aggregation_units (int): The number of units in the graph
                aggregation layer before regression.
            dropout_rate (float, optional): Dropout rate for the convolution
                layers. Defaults to 0.
            leaky_relu_slope (float, optional): Slope of the LeakyReLU
                activation function. Defaults to 0.1.
            with_features (bool, optional): Whether to use additional 
                node features. Defaults to False.
            feature_dim_size (int, optional): The number of units in the
                additional node features. Defaults to 0.
        """
        super().__init__()

        # Define the graph convolution layers
        self.graph_conv = MultiGraphConvolutionLayers(
            in_features,
            conv_units,
            torch.nn.LeakyReLU(leaky_relu_slope),
            edge_type_num=2,
            dropout_rate=dropout_rate,
            with_features=with_features,
            feature_dim_size=feature_dim_size,
        )

        # Define the aggregation layer
        # The input size is the output size of the last graph convolution layer
        self.aggregation_layer = GraphAggregationLayer(
            conv_units[-1],
            aggregation_units,
            leaky_relu_slope=leaky_relu_slope,
        )

    def forward(
        self,
        node_features: torch.Tensor,
        adj_matrices: torch.Tensor,
        h_tensor: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """Forward pass through the RelationalGCNRegressor.

        Args:
            node_features (torch.Tensor): The node features tensor of shape
                (N, in_features), where N is the number of nodes.
            adj_matrices ([torch.Tensor]): The adjacency matrices of the graph.
        Returns:
            torch.Tensor: The regression output for the graph.
        """
        # Graph convolution layers
        hidden_features = self.graph_conv(
            node_features, adj_matrices, h_tensor
        )

        # Aggregation layer
        output = self.aggregation_layer(hidden_features)

        return output
