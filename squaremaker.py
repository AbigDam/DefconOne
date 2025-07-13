import re

def parse_squares_code(input_text):
    squares_data = []

    # Regex patterns to extract owner name, square name, color
    owner_pattern = re.compile(r'owner\s*=\s*Nations\.objects\.get\(game\s*=\s*game_id,\s*name\s*=\s*"([^"]+)"\)')
    name_pattern = re.compile(r'square_instance\.name\s*=\s*"([^"]+)"')
    color_pattern = re.compile(r'square_instance\.color\s*=\s*"([^"]+)"')

    # Split input into blocks by 'j += 1' which ends each square definition
    blocks = input_text.split("j += 1")

    for block in blocks:
        owner_match = owner_pattern.search(block)
        name_match = name_pattern.search(block)
        color_match = color_pattern.search(block)

        if owner_match and name_match and color_match:
            squares_data.append({
                "owner_name": owner_match.group(1),
                "name": name_match.group(1),
                "color": color_match.group(1)
            })

    return squares_data

def squares_data_to_text(squares_data):
    lines = ["squares_data = ["]
    for sq in squares_data:
        lines.append(f'    {{"name": "{sq["name"]}", "color": "{sq["color"]}", "owner_name": "{sq["owner_name"]}"}},')
    lines.append("]")
    return "\n".join(lines)


# Example usage:

with open("makegame.txt", "r") as f:
    input_text = f.read()

squares_data = parse_squares_code(input_text)
output_text = squares_data_to_text(squares_data)

with open('states_array.txt', 'w') as output:
    output.write(output_text)