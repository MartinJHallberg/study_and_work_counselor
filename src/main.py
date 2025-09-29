from agent.graph import graph


def stream_graph_updates(current_state: dict, user_input: str):
    # Add the new user message to the existing state
    if "messages" not in current_state:
        current_state["messages"] = []
    
    current_state["messages"].append({"role": "user", "content": user_input})
    
    # Stream updates starting from the current state
    for event in graph.stream(current_state):
        # Display the state information for each event
        print(f"State: {event}")
        for node_name, value in event.items():
            print(f"Node '{node_name}' output:")
            if "messages" in value and value["messages"]:
                print("Assistant:", value["messages"][-1].content)
            else:
                print(f"Value: {value}")
            # Update the current state with the new values
            current_state.update(value)
        print("-" * 50)  # Separator for clarity
    
    return current_state


if __name__ == "__main__":
    print("Study and Work Counselor - Type 'quit', 'exit', or 'q' to stop")
    print("=" * 60)
    
    # Initialize persistent state
    conversation_state = {}
    
    while True:
        user_input = input("\nUser: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        
        # Update the state with the new input and get the updated state back
        conversation_state = stream_graph_updates(conversation_state, user_input)