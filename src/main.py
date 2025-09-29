from agent.parsing import graph


def stream_graph_updates(user_input: str):
    # Pass the user input as a proper message format
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        # Display the state information for each event
        print(f"State: {event}")
        for node_name, value in event.items():
            print(f"Node '{node_name}' output:")
            if "messages" in value and value["messages"]:
                print("Assistant:", value["messages"][-1].content)
            else:
                print(f"Value: {value}")
        print("-" * 50)  # Separator for clarity

if __name__ == "__main__":
    print("Study and Work Counselor - Type 'quit', 'exit', or 'q' to stop")
    print("=" * 60)
    
    while True:
        user_input = input("\nUser: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break  # Fix: This should be inside the if statement
        
        stream_graph_updates(user_input)