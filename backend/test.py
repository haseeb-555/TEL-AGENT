import json

# Original agent output with extra characters around the JSON
agent_output = """
     ```json\n{\n  "Name": "Goldman Sachs",\n  "Event Title": "GOLDMAN SACHS SUMMER ANALYST INTERNSHIP",\n  "Deadline": "2025-04-20 14:00:00",\n  "Description": "Goldman Sachs is a leading global investment banking, securities, and investment management firm. It provides a wide range of financial services to a substantial and diversified client base. Headquartered in New York, it has offices in all major financial centers around the world. Recent news includes focus on technological advancements in finance. Careers: https://www.goldmansachs.com/careers/"\n}\n```
"""

# Clean the agent_output to get the actual JSON string
cleaned_output = agent_output.strip().replace('```json\n', '').replace('\n```', '')

# Parse the cleaned JSON output
parsed_data = json.loads(cleaned_output)

# Map to the new key-value format
converted_data = {
    "name": parsed_data.get("Name"),
    "event": parsed_data.get("Event Title"),
    "deadline": parsed_data.get("Deadline"),
    "description": parsed_data.get("Description")
}

# Print the converted dictionary
print(converted_data)
