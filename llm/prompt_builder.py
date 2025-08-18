def build_prompt(user_query: str, tools: list = None, resources: list = None) -> str:
    prompt_parts = []
    # Add the user query
    prompt_parts.append(f"User question: {user_query}")

    # Optionally add available tools
    # 
    if tools:
        tool_lines = ["Available tools:"]
        for tool in tools:
            tool_lines.append(f"- {tool['name']}: {tool['description']}")
        prompt_parts.append("\n".join(tool_lines))

    # Optionally add available resources
    if resources:
        resource_lines = ["Available data files:"]
        for res in resources:
            resource_lines.append(f"- {res['name']}: {res['description']}")
        prompt_parts.append("\n".join(resource_lines))

    return "\n\n".join(prompt_parts)
