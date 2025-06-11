from typing import TypedDict, Annotated
import operator

from langgraph.graph import StatefulGraph, END

class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        messages: A list of messages that have been processed.
    """
    messages: Annotated[list, operator.add]

def node_one(state: GraphState):
    """
    First node in the graph.
    """
    print("Executing Node One")
    state['messages'].append("Message from Node One")
    return state

def node_two(state: GraphState):
    """
    Second node in the graph.
    """
    print("Executing Node Two")
    state['messages'].append("Message from Node Two")
    return state

# Instantiate the graph
workflow = StatefulGraph(GraphState)

# Add nodes
workflow.add_node("node_one", node_one)
workflow.add_node("node_two", node_two)

# Set the entry point
workflow.set_entry_point("node_one")

# Add edges
workflow.add_edge("node_one", "node_two")
workflow.add_edge("node_two", END)

# Compile the graph
app = workflow.compile()

if __name__ == "__main__":
    initial_input = {"messages": ["Initial message"]}
    final_state = app.invoke(initial_input)
    print("\nFinal State:")
    for message in final_state['messages']:
        print(message)
