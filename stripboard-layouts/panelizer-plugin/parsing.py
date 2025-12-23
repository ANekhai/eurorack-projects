import json
import csv

def extract_veecad_components(per_file: str) -> list[dict]:
    try:
        with open(per_file, mode='r') as file:
            # skip header data, read json block
            file_text = file.readlines()
            
            json_data = ' '.join(file_text[3:])
            json_data = json.loads(json_data)
        
        return json_data['Components']

    except FileNotFoundError:
        print(f"Error: The file '{per_file}' was not found.")
    except json.JSONDecodeError:
        print(f"Error: Malformed JSON from file '{per_file}'")
    except Exception:
        print(f"Encountered Error while parsing {per_file}: {Exception}")


def filter_footprints(data: list[dict]) -> set:
    return {cmp['Outline'] for cmp in data}


def format_component_data(data:list[dict]) -> dict:
    return {cmp['Designator']: [cmp['Outline'], cmp['X1000']/1000, cmp['Y1000']/1000, 
                                get_rotation(cmp['EndDeltaX'], cmp['EndDeltaY'])] 
                for cmp in data}


def get_rotation(x, y) -> int:
    # converts veecad file format rotation to a 90-degree equivalent
    if y:
        if y > 0: return 0
        else: return 180
    elif x > 0:
        return 90
    else:
        return 270

if __name__ == "__main__":
    test_file = "rotation_test.per"
    components = extract_veecad_components(test_file)
    formatted_cmps = format_component_data(components)
    print(formatted_cmps)
    # print(get_rotation(0, 1))
    # print(filter_footprints(components))