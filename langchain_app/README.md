# Simple LangGraph Application

This is a simple example demonstrating a LangGraph setup with a few nodes that append messages to a shared state.

The application defines a graph with two nodes, `node_one` and `node_two`.
- `node_one` is the entry point. It appends a message to the `messages` list in the graph's state.
- `node_two` is the next node. It also appends a message to the `messages` list.
- The graph then transitions to the `END` state.

The final list of messages is printed to the console.

## How to Run

To run this application:
1. Ensure you have Python installed.
2. Install the necessary dependencies by running `pip install -r requirements.txt` in the root directory of this project (if you haven't already).
3. Navigate to the `langchain_app` directory:
   ```bash
   cd langchain_app
   ```
4. Execute the application script:
   ```bash
   python app.py
   ```

You should see output indicating the execution of each node and the final state containing all accumulated messages.
