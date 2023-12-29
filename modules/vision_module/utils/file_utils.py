import base64
import os
import sys

root = os.path.dirname(__file__)
root = os.path.dirname(root)
sys.path.append(root)


def get_config(problem_name):
    """
    return configuration json files for Problem
    user can customize only parts of configuration json files, other files will be left for default
    Args:
        problem_name: customized configuration name under Problems/

    Returns:
        path problem config, input images/text, solutions: [problem_config_path, problem_statements_path, solutions_path]
    """
    config_dir = os.path.join(root, "Problems", problem_name)
    default_config_dir = os.path.join(root, "Problems", "PhotoCircuit")

    config_files = [
        "problem_config.json",
        "problem_statements",
        "solutions"
    ]

    config_paths = []

    for config_file in config_files:
        problem_config_path = os.path.join(config_dir, config_file)
        default_config_path = os.path.join(default_config_dir, config_file)

        if os.path.exists(problem_config_path):
            config_paths.append(problem_config_path)
        else:
            config_paths.append(default_config_path)

    return tuple(config_paths)


# Function to encode the image
def encode_image(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def load_txt_file(txt_file_path):
    contents = None
    with open(txt_file_path, 'r', encoding='utf-8') as file:
        contents = file.read()
    return contents


def join_json_string(inp) -> str:
    if isinstance(inp, list):
        return '\n'.join(inp)
    else:
        return str(inp)


def save_new_prompt(problem_name, version, new_prompt, epoch, training_example, start_time):
    prompt_file_path = os.path.join(root, "Workspace", problem_name, version, "intermediate_prompts", str(start_time))
    os.makedirs(prompt_file_path, exist_ok=True)
    prompt_file_path = os.path.join(prompt_file_path, f"prompt_epoch{epoch}_example{training_example}.txt")
    with open(prompt_file_path, 'w') as f:
        f.writelines(new_prompt)
