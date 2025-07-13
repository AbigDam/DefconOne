def extract_coastal_states_from_txt(txt_file_path):
    with open(txt_file_path, 'r') as file:
        lines = file.readlines()

    coastal_states = []

    for line in lines:
        if "Square.objects.get" in line and "name =" in line:
            name_part = line.split("name =")[1]
            name = name_part.split("'")[1]
            coastal_states.append(name)

    return coastal_states

coastal_states = extract_coastal_states_from_txt("costal_code.txt")
with open('costal_array.txt', 'w') as output:
    output.write("coastal_states =" + str(coastal_states))