import re

def parse_neighbors_code(input_text):
    neighbors_data = []

    # Regex to extract the square name
    name_pattern = re.compile(r"name\s*=\s*'([^']+)'")
    
    # Regex to extract all neighbor names
    neighbor_pattern = re.compile(r"name\s*=\s*'([^']+)'")

    # Split into blocks by "square_instance.save()" or new square instance
    blocks = input_text.split("square_instance.save()")

    for block in blocks:
        name_matches = name_pattern.findall(block)
        if len(name_matches) < 1:
            continue
        square_name = name_matches[0]
        neighbor_names = name_matches[1:]  # the rest are neighbors
        neighbors_data.append({
            "name": square_name,
            "neighbors": neighbor_names
        })

    return neighbors_data

def neighbors_data_to_text(neighbors_data):
    lines = ["neighbors_data = ["]
    for entry in neighbors_data:
        neighbor_list = ", ".join(f'"{n}"' for n in entry["neighbors"])
        lines.append(f'    {{"name": "{entry["name"]}", "neighbors": [{neighbor_list}]}},')
    lines.append("]")
    return "\n".join(lines)


# Example usage:
with open("neighbors_code.txt", "r") as f:
    input_text = f.read()

neighbors_data = parse_neighbors_code(input_text)
output_text = neighbors_data_to_text(neighbors_data)

with open('neighbor_array.txt', 'w') as output:
    output.write(output_text)