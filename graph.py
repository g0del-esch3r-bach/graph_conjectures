import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

class Graph:
    def __init__(self, state):
        if isinstance(state, nx.Graph):
            self.graph = self.process_nx_graph(state)
        elif isinstance(state, np.ndarray) and len(state.shape) == 1:
            self.graph = self.process_linenv_state(state)
        elif isinstance(state, dict) and all(key in state for key in ['adjacency_matrix', 'current_node']):
            self.graph = self.process_locenv_state(state)
        else:
            raise TypeError("input state must be a networkx Graph, a LinEnv state, or a LocEnv state")
        
        self.number_of_nodes = self.graph.number_of_nodes()

    def process_nx_graph(self, state):
        return state

    def process_linenv_state(self, state):
        """Here state is the state as encoded in LinEnv, that is, a (non-directed, unlabeled, without loops) graph described by a ndarray of shape (2 * edges, ), where edges (i,j) are in lessicografic order"""
        
        # Remove the timestep part
        number_of_edges = len(state) // 2
        print(f"number of edges2 {number_of_edges}")
        graph = state[:number_of_edges]
        assert all(element in [0, 1] for element in graph), "graph is a ndarray, but it contains elements other than 0 and 1"
        
        # Recover number_of_nodes from number_of_edges
        number_of_nodes = int((1 + np.sqrt(1 + 8 * number_of_edges)) / 2)
        condition = (number_of_nodes == (1 + np.sqrt(1 + 8 * number_of_edges)) / 2)
        print(f"number of nodes2 {number_of_nodes}")
        assert condition, f"wrong len(graph): 'number_of_nodes' = (1 + np.sqrt(1 + 8 * len(graph))) / 2 = {(1 + np.sqrt(1 + 8 * number_of_edges)) / 2} should be integer"

        # Create an empty graph
        G = nx.Graph()

        # Add nodes
        G.add_nodes_from(range(number_of_nodes))

        # Add edges ordered by the order of the nodes
        edge_index = 0
        for i in range(number_of_nodes):
            for j in range(i + 1, number_of_nodes):
                if graph[edge_index] == 1:
                    G.add_edge(i, j)
                edge_index += 1
        return G

    def process_locenv_state(self, state):
        # Get the adjacency matrix from the LocEnv state
        graph = state['adjacency_matrix']
        # Create a networkx graph from the adjacency matrix
        G = nx.Graph(graph)
        return G

    def wagner1(self):
        const = 1 + np.sqrt(self.number_of_nodes - 1)
        radius = max(np.real(nx.adjacency_spectrum(self.graph)))
        weight = len(nx.max_weight_matching(self.graph))
        return const - (radius + weight)

    def is_connected(self):
        return nx.is_connected(self.graph)

    def is_star(self):
        # Compute star condition: one central node of degree number_of_nodes - 1, every other node of degree 1
        degree_sequence = [d for n, d in self.graph.degree()]
        is_star = degree_sequence.count(1) == len(degree_sequence) - 1 and degree_sequence.count(len(degree_sequence) - 1) == 1
        return is_star

    def draw(self, title=None, ax=None):
        # If no axes are provided, create a new figure and axes
        if ax is None:
            _, ax = plt.subplots()
        pos = nx.spring_layout(self.graph)
        # Create the title string
        title_string = f"wagner1 score = {self.wagner1()}"
        if title is not None:
            title_string = f"{title}\n{title_string}"
        # Draw the new graph
        ax.set_title(title_string)
        nx.draw(self.graph, pos=pos, ax=ax, with_labels=True, node_color='lightyellow', font_color='black', edgecolors='black')
        # If no axes were provided, keep the window open
        if ax is None:
            plt.show()