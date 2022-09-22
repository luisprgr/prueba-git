import yaml
import os
import sys
import json


def get_layers_paths():
    paths = []
    with open("template.yml", "r") as f:
        file = f.read().replace("!Ref", "")
        template = yaml.load(file, Loader=yaml.FullLoader)
        resources = template["Resources"]
        for resource in resources.values():
            if resource["Type"] == "AWS::Serverless::LayerVersion":
                if not makefile_exist(resource["Properties"]["ContentUri"]):
                    paths.append(resource["Properties"]["ContentUri"] + "python/")
                else:
                    paths.append(resource["Properties"]["ContentUri"])
    return paths


def get_functions_paths():
    paths = []
    with open("template.yml", "r") as f:
        file = f.read().replace("!Ref", "")
        template = yaml.load(file, Loader=yaml.FullLoader)
        resources = template["Resources"]
        for resource in resources.values():
            if resource["Type"] == "AWS::Serverless::Function":
                paths.append(resource["Properties"]["CodeUri"])
    return paths


def makefile_exist(directory):
    for _, _, files in os.walk(directory):
        for file in files:
            if file == "makefile" or file == "Makefile":
                return True
    return False


def inject_layers_paths():
    paths = get_layers_paths()
    for path in paths:
        sys.path.append(path)


def inject_functions_paths():
    paths = get_functions_paths()
    for path in paths:
        sys.path.append(path)


def inject_paths_for_vscode():
    with open(".vscode/settings.json", "r+") as f:
        settings = json.loads(f.read())
        settings["python.analysis.extraPaths"] = (
            get_layers_paths() + get_functions_paths()
        )
        f.seek(0)
        f.write(json.dumps(settings))
        f.truncate()

def delete_paths_from_vscode():
    with open(".vscode/settings.json", "r+") as f:
        settings = json.loads(f.read())
        del settings["python.analysis.extraPaths"]
        f.seek(0)
        f.write(json.dumps(settings))
        f.truncate()

def inject_paths():
    inject_layers_paths()
    inject_functions_paths()


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "delete":
        delete_paths_from_vscode()
    else:
        inject_paths_for_vscode()

