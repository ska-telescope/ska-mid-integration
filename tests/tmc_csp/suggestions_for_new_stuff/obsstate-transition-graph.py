# pylint: skip-file
# flake8: noqa
import random

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrowPatch

# Flattened state machine for operational and observation state diagram
# written and validated by Giorgio Brajnik based on the diagram and spec in ADR-8.

# The graph is a MultiDiGraph with two types of nodes: operational and observational
# and two types of transitions: those triggered by commands and those triggered by internal events


# How to use this script
# - you need to install networkx and matplotlib
# - you can run this script in a Python environment
# - with the command: `python obsstate-transition-graph.py'
# - it will print all transitions in the state machine
# - it will print all pairs of consecutive transitions in the state machine
# - it will generate and plot a graph of the state machine (not plarticulary useful for such a large state machine)


def create_merged_graph():
    G = nx.MultiDiGraph()

    # Operational states
    op_states = ["INIT", "OFF", "ON", "OP_FAULT"]
    G.add_nodes_from(op_states, type="operational")

    # Observational states
    obs_states = [
        "EMPTY",
        "RESOURCING",
        "IDLE",
        "CONFIGURING",
        "READY",
        "SCANNING",
        "ABORTING",
        "ABORTED",
        "RESTARTING",
        "OBS_FAULT",
    ]
    G.add_nodes_from(obs_states, type="observational")

    op_transitions = [
        ("INIT", "OFF", {"label": "Initialised", "type": "event"}),
        ("INIT", "OP_FAULT", {"label": "fatal error", "type": "event"}),
        ("OFF", "EMPTY", {"label": "On", "type": "command"}),
        ("OFF", "OP_FAULT", {"label": "fatal error", "type": "event"}),
        ("OP_FAULT", "OFF", {"label": "Reset", "type": "command"}),
    ]
    # Operational transitions
    G.add_edges_from(op_transitions)

    # Observational transitions
    obs_transitions = [
        (
            "EMPTY",
            "RESOURCING",
            {"label": "AssignResources", "type": "command"},
        ),
        ("EMPTY", "OFF", {"label": "Off", "type": "command"}),
        (
            "EMPTY",
            "OBS_FAULT",
            {"label": "Observation Fault", "type": "event"},
        ),
        ("EMPTY", "OP_FAULT", {"label": "Fatal error", "type": "event"}),
        ("RESOURCING", "IDLE", {"label": "Assigned", "type": "event"}),
        ("RESOURCING", "IDLE", {"label": "Released", "type": "event"}),
        ("RESOURCING", "ABORTING", {"label": "Abort", "type": "command"}),
        ("RESOURCING", "EMPTY", {"label": "All released", "type": "event"}),
        (
            "RESOURCING",
            "OBS_FAULT",
            {"label": "Observation fault", "type": "event"},
        ),
        ("RESOURCING", "OP_FAULT", {"label": "Fatal error", "type": "event"}),
        ("IDLE", "CONFIGURING", {"label": "Configure", "type": "command"}),
        (
            "IDLE",
            "RESOURCING",
            {"label": "ReleaseResources", "type": "command"},
        ),
        (
            "IDLE",
            "RESOURCING",
            {"label": "AssignResources", "type": "command"},
        ),
        ("IDLE", "ABORTING", {"label": "Abort", "type": "command"}),
        ("IDLE", "OBS_FAULT", {"label": "Observation Fault", "type": "event"}),
        ("IDLE", "OP_FAULT", {"label": "Fatal error", "type": "event"}),
        ("CONFIGURING", "READY", {"label": "Ready", "type": "event"}),
        (
            "CONFIGURING",
            "OBS_FAULT",
            {"label": "Observation Fault", "type": "event"},
        ),
        ("CONFIGURING", "OP_FAULT", {"label": "Fatal error", "type": "event"}),
        ("CONFIGURING", "ABORTING", {"label": "Abort", "type": "command"}),
        ("READY", "SCANNING", {"label": "Scan", "type": "command"}),
        ("READY", "IDLE", {"label": "End", "type": "command"}),
        ("READY", "ABORTING", {"label": "Abort", "type": "command"}),
        ("READY", "CONFIGURING", {"label": "Configure", "type": "command"}),
        (
            "READY",
            "OBS_FAULT",
            {"label": "Observation Fault", "type": "event"},
        ),
        ("READY", "OP_FAULT", {"label": "Fatal error", "type": "event"}),
        ("SCANNING", "READY", {"label": "EndScan", "type": "command"}),
        ("SCANNING", "ABORTING", {"label": "Abort", "type": "command"}),
        ("SCANNING", "READY", {"label": "ScanComplete", "type": "event"}),
        (
            "SCANNING",
            "OBS_FAULT",
            {"label": "Observation Fault", "type": "event"},
        ),
        ("SCANNING", "OP_FAULT", {"label": "Fatal error", "type": "event"}),
        ("ABORTING", "ABORTED", {"label": "Abort complete", "type": "event"}),
        (
            "ABORTING",
            "OBS_FAULT",
            {"label": "Observation Fault", "type": "event"},
        ),
        ("ABORTING", "OP_FAULT", {"label": "Fatal error", "type": "event"}),
        ("ABORTED", "RESTARTING", {"label": "Restart", "type": "command"}),
        (
            "ABORTED",
            "OBS_FAULT",
            {"label": "Observation Fault", "type": "event"},
        ),
        ("ABORTED", "OP_FAULT", {"label": "Fatal error", "type": "event"}),
        (
            "RESTARTING",
            "EMPTY",
            {"label": "Restart Complete", "type": "event"},
        ),
        (
            "RESTARTING",
            "OBS_FAULT",
            {"label": "Observation Fault", "type": "event"},
        ),
        ("RESTARTING", "OP_FAULT", {"label": "Fatal error", "type": "event"}),
        ("OBS_FAULT", "RESTARTING", {"label": "Restart", "type": "command"}),
        (
            "OBS_FAULT",
            "OBS_FAULT",
            {"label": "Observation Fault", "type": "event"},
        ),
        ("OBS_FAULT", "OP_FAULT", {"label": "Fatal error", "type": "event"}),
    ]
    G.add_edges_from(obs_transitions)

    # Connections between operational and observational states
    cross_transitions = [
        # ('ON', 'EMPTY', {'label': 'initialized', 'type': 'event'}),
        # ('OFF', 'EMPTY', {'label': 'Power On', 'type': 'event'}),
        # ('EMPTY', 'OFF', {'label': 'Power Off', 'type': 'event'}),
        # ('OBS_FAULT', 'OP_FAULT', {'label': 'Escalate Fault', 'type': 'event'})
    ]
    G.add_edges_from(cross_transitions)

    return G


fontsize = 15


def compute_edge_label(label, edge_type):
    if edge_type == "command":
        return f"CMD: {label}"
    else:
        return f"AUTO: {label}"


def draw_curved_edge(
    ax, posA, posB, label, edge_type, connectionstyle="arc3,rad=0.2"
):
    if edge_type == "command":
        color = "blue"
    else:
        color = "red"
    label = compute_edge_label(label, edge_type)

    arrow = FancyArrowPatch(
        posA,
        posB,
        arrowstyle="->",
        color=color,
        connectionstyle=connectionstyle,
        mutation_scale=30,  # Increased from 20 to 30
        linewidth=2,  # Increased from 1 to 2
        shrinkA=20,  # Added to start arrow further from node
        shrinkB=29,
    )
    ax.add_patch(arrow)

    # Calculate the position for the label closer to the source node
    t = 0.1  # Adjust this value to move label closer (smaller) or further (larger) from source
    label_pos = posA + t * (np.array(posB) - np.array(posA))

    # Add a small offset perpendicular to the edge direction
    diff = np.array(posB) - np.array(posA)
    perp = np.array([-diff[1], diff[0]])
    norm = np.linalg.norm(perp)
    if norm != 0:
        perp = perp / norm
    offset = perp * 0.01  # Adjust this value for perpendicular offset

    label_pos = label_pos + offset

    ax.text(
        label_pos[0],
        label_pos[1],
        label,
        fontsize=fontsize,
        ha="center",
        va="center",
        color=color,
        bbox=dict(facecolor="white", edgecolor="none", alpha=0.7, pad=0.5),
    )


# Create the merged graph
merged_graph = create_merged_graph()





class StateGraphAnalyzer:
    """MISSION: implement the following methods to analyze a state graph:
    - print_transitions(): prints all individual transitions in the graph
    """

    def __init__(self, graph):
        self.graph = graph

    def print_transitions(self):
        """
        Prints each transition in the format:
        start-state --> (trigger) --> end-state
        """
        for i, (start_state, end_state, data) in enumerate(
            self.graph.edges(data=True), 1
        ):
            trigger = data["label"]
            label = compute_edge_label(data["label"], data["type"])
            print(f"{i}. {start_state} --> ({label}) --> {end_state}")

    def get_outgoing_transitions(self, state):
        """
        Returns a list of outgoing transitions from the given state.
        Each transition is a tuple: (end_state, trigger, type)
        """
        return [
            (end_state, data["label"], data["type"])
            for end_state, data in self.graph[state].items()
        ]

    def get_incoming_transitions(self, state):
        """
        Returns a list of incoming transitions to the given state.
        Each transition is a tuple: (start_state, trigger, type)
        """
        return [
            (start_state, data["label"], data["type"])
            for start_state, data in self.graph.pred[state].items()
        ]

    def get_all_commands(self):
        """
        Returns a list of all unique commands in the graph.
        """
        return list(
            set(
                data["label"]
                for _, _, data in self.graph.edges(data=True)
                if data["type"] == "command"
            )
        )

    def get_all_events(self):
        """
        Returns a list of all unique events in the graph.
        """
        return list(
            set(
                data["label"]
                for _, _, data in self.graph.edges(data=True)
                if data["type"] == "event"
            )
        )

    def get_states_with_self_transitions(self):
        """
        Returns a list of states that have self-transitions.
        """
        return [
            node
            for node in self.graph.nodes()
            if self.graph.has_edge(node, node)
        ]


    def print_consecutive_transition_pairs(self):
        """
        Prints a numbered list of pairs of consecutive transitions in the graph.
        Format:
        n. start-state --> (trigger1) --> intermediate-state --> (trigger2) --> end-state
        """
        transition_pairs = []
        for start_state in self.graph.nodes():
            for mid_state, data1 in self.graph[start_state].items():
                data1=data1[0]
                for end_state, data2 in self.graph[mid_state].items():
                    data2=data2[0]
                    if start_state != end_state:  # Avoid cycles
                        print(data1)
                        trigger1 = compute_edge_label(data1["label"], data1["type"])
                        trigger2 = compute_edge_label(data2["label"], data2["type"])
                        transition_pairs.append((start_state, mid_state, end_state, trigger1, trigger2))

        for i, (start, mid, end, trigger1, trigger2) in enumerate(transition_pairs, 1):
            print(f"{i}. {start} --> ({trigger1}) --> {mid} --> ({trigger2}) --> {end}")

    def get_path_between_states(self, start_state, end_state):
        """
        Returns the shortest path between two states as a list of transitions.
        Each transition is a tuple: (from_state, to_state, trigger, type)
        """
        try:
            path = nx.shortest_path(self.graph, start_state, end_state)
            return [
                (
                    path[i],
                    path[i + 1],
                    self.graph[path[i]][path[i + 1]]["label"],
                    self.graph[path[i]][path[i + 1]]["type"],
                )
                for i in range(len(path) - 1)
            ]
        except nx.NetworkXNoPath:
            return None

    def print_transition_matrix(self):
        G = self.graph
        # Get all nodes in the graph
        nodes = list(G.nodes())

        # Create an empty DataFrame to store the transition matrix
        matrix = pd.DataFrame(index=nodes, columns=nodes)
        matrix = matrix.fillna('')

        # Populate the matrix
        for edge in G.edges(data=True):
            source, target, data = edge
            label = data.get('label', '')
            edge_type = data.get('type', '')

            # Combine label and type information
            info = f"{label} ({edge_type})"

            # If there are multiple edges between the same nodes, append the new info
            if matrix.at[source, target]:
                matrix.at[source, target] += f"\n{info}"
            else:
                matrix.at[source, target] = info

        # Convert the DataFrame to a markdown table
        markdown_table = matrix.to_markdown()

        # Print the markdown table
        print("# FSM Transition Matrix")
        print()
        print(markdown_table)
analyzer = StateGraphAnalyzer(merged_graph)

print("All transitions:")
analyzer.print_transitions()

#
print("\n\n\nAll consecutive pairs of transitions:")
analyzer.print_consecutive_transition_pairs()

analyzer.print_transition_matrix()

def plot_graph(graph):
    global data
    # Visualization
    fig, ax = plt.subplots(figsize=(40, 30))
    pos = nx.spring_layout(graph, k=2, iterations=50)
    # Draw nodes
    op_nodes = [
        node
        for node, data in graph.nodes(data=True)
        if data.get("type") == "operational"
    ]
    obs_nodes = [
        node
        for node, data in graph.nodes(data=True)
        if data.get("type") == "observational"
    ]
    nx.draw_networkx_nodes(
        graph,
        pos,
        nodelist=op_nodes,
        node_color="lightblue",
        node_size=3000,
        ax=ax,
    )
    nx.draw_networkx_nodes(
        graph,
        pos,
        nodelist=obs_nodes,
        node_color="lightgreen",
        node_size=3000,
        ax=ax,
    )
    # Draw edges with curves for bidirectional connections
    for edge in graph.edges(data=True):
        n1, n2, data = edge
        label = data["label"]
        edge_type = data["type"]

        # Unidirectional edge
        draw_curved_edge(
            ax, pos[n1], pos[n2], label, edge_type, connectionstyle="arc3,rad=0.3"
        )
    # Draw labels
    nx.draw_networkx_labels(
        graph, pos, font_size=15, font_weight="bold", ax=ax
    )
    plt.title("Merged Operational and Observational State Machine", fontsize=20)
    plt.axis("off")
    plt.tight_layout()
    plt.show()


# plot_graph(merged_graph)

# what follows are examples of the sequence based specification method
# here we are assuming 2 interacting subarrays

class Subarray:
    def __init__(self):
        """graph (nx.MultiDiGraph): The state graph
        """
        self.graph = create_merged_graph()
        self.initial_state = "INIT"

    def get_possible_triggers(self):
        """
        Returns a list of all possible triggers (commands and events) in the graph.
        """
        return list(set(data["label"] for _, _, data in self.graph.edges(data=True)))

    def simulate_transition(self, current_state, trigger):
        """
        Simulates a state transition based on the current state and trigger.

        Args:

        current_state (str): The current state of the system
        trigger (str): The trigger event or command

        Returns:
        tuple: (next_state, response) where response is one of SUCCESS, TIMEOUT, ERROR
        """
        # Check if the current state exists in the graph
        if current_state not in self.graph.nodes():
            return (None, "ERROR")

        # Find all possible transitions from the current state
        possible_transitions = [
            (end_state, data)
            for end_state, edge_data in self.graph[current_state].items()
            for data in edge_data.values()
            if data['label'] == trigger
        ]

        # If no valid transition found for the given trigger
        if not possible_transitions:
            return (current_state, "ERROR")

        # Randomly choose a transition if multiple are available
        next_state, _ = random.choice(possible_transitions)

        # Randomly choose a response
        response = random.choices(
            ["SUCCESS", "TIMEOUT", "ERROR"],
            weights=[0.8, 0.1, 0.1],  # 80% SUCCESS, 10% TIMEOUT, 10% ERROR
            k=1
        )[0]

        return (response, next_state)

from collections import Counter
from typing import List, Tuple, Dict, Callable

# Type aliases
Stimulus = str
Response = str
State = str

def generate_random_sequence(max_length: int, stimuli: List[Stimulus]) -> List[Stimulus]:
    length = random.randint(1, max_length)
    return [random.choice(stimuli) for _ in range(length)]

def sequence_based_specification(
    num_tests: int,
    max_sequence_length: int,
    fsm1_fsm: Subarray,
    fsm2_fsm: Subarray,
    initial_fsm1_state: State,
    initial_fsm2_state: State,
    stimuli: List[Stimulus]
) -> List[Tuple[List[Stimulus], List[Tuple[Stimulus, Response, State, Response, State]]]]:
    sequences = []

    def process_stimulus(stim: Stimulus, s_state: State, r_state: State) -> Tuple[Stimulus, Response, State, Response, State]:
        s_response, new_s_state = fsm1_fsm.simulate_transition(s_state, stim)
        r_response, new_r_state = fsm2_fsm.simulate_transition(r_state, stim)
        return (stim, s_response, new_s_state, r_response, new_r_state)

    for length in range(1, max_sequence_length + 1):
        new_sequences = []
        for seq in [[],] if length == 1 else sequences:
            for stimulus in stimuli:
                print(seq)
                print(stimulus)
                new_seq = seq + [stimulus]
                fsm1_state = initial_fsm1_state
                fsm2_state = initial_fsm2_state
                result = []
                for s in new_seq:
                    step_result = process_stimulus(s, fsm1_state, fsm2_state)
                    result.append(step_result)
                    fsm1_state = step_result[2]
                    fsm2_state = step_result[4]
                new_sequences.append((new_seq, result))
                print(f"new sequences: {new_sequences}")
        sequences = new_sequences

    # Randomly sample from the generated sequences to match num_tests
    if len(sequences) > num_tests:
        sequences = random.sample(sequences, num_tests)
    elif len(sequences) < num_tests:
        # Generate additional random sequences if we don't have enough
        while len(sequences) < num_tests:
            random_seq = generate_random_sequence(max_sequence_length, stimuli)
            fsm1_state = initial_fsm1_state
            fsm2_state = initial_fsm2_state
            result = []
            for s in random_seq:
                step_result = process_stimulus(s, fsm1_state, fsm2_state)
                result.append(step_result)
                fsm1_state = step_result[2]
                fsm2_state = step_result[4]
            sequences.append((random_seq, result))

    return sequences

def analyze_results(sequences: List[Tuple[List[Stimulus], List[Tuple[Stimulus, Response, State, Response, State]]]]) -> None:
    state_transitions = Counter()
    response_pairs = Counter()
    stimuli_distribution = Counter()

    for _, results in sequences:
        for step in results:
            stimulus, s_response, s_state, r_response, r_state = step
            state_transitions[(s_state, r_state)] += 1
            response_pairs[(s_response, r_response)] += 1
            stimuli_distribution[stimulus] += 1

    print("State Transition Frequencies:")
    for (sender_state, receiver_state), count in state_transitions.most_common():
        print(f"  Sender: {sender_state}, Receiver: {receiver_state} - Count: {count}")

    print("\nResponse Pair Frequencies:")
    for (sender_response, receiver_response), count in response_pairs.most_common():
        print(f"  Sender: {sender_response}, Receiver: {receiver_response} - Count: {count}")

    print("\nStimuli Distribution:")
    for stimulus, count in stimuli_distribution.most_common():
        print(f"  {stimulus}: {count}")

SA1 = Subarray()
SA2 = Subarray()
test_results = sequence_based_specification(
    num_tests=1000,
    max_sequence_length=5,
    fsm1_fsm=SA1,
    fsm2_fsm=SA2,
    initial_fsm1_state=SA1.initial_state,
    initial_fsm2_state=SA2.initial_state,
    stimuli=SA1.get_possible_triggers()
)

analyze_results(test_results)