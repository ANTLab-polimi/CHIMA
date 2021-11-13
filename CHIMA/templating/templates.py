import json
import subprocess
import shlex
import os

from defines import BASE_TEMPLATE_PATH, BASE_BUILD_SCRIPT
from utils import *

## Composition and building of pipelines from templates

class TemplateParts:
    include = 0
    define = 1
    apply = 2

class Function:
    def __init__(self, include, control, id):
        self.include = include
        self.control = control
        self.id = id

REPLACE_KEYS= ["###FUNCTION_INCLUDE###", "###FUNCTION_DEFINE###", "###FUNCTION_APPLY###"]

# Reads function definitions from a json file
# and populates a list of functions with them
def read_functions(filepath, funcs_list):
    with open(filepath, "r") as file:
        data = json.load(file)
        id = 0
        for f in data:
            funcs_list.append(Function(f["include"], f["control"], id))
            id += 1

# Takes a list of functions and creates the
# appropriate content strings to use in a
# template
def create_content(funcs, content):
    for index in range(len(funcs)):
        f = funcs[index]
        content[TemplateParts.include] += f'#include "{f.include}"\n'
        content[TemplateParts.define] += f'{f.control}() {f.control}_{f.id};\n'
        content[TemplateParts.apply] += f'if(hdr.mpls_stack[index].label == {f.id}) {{ {f.control}_{f.id}.apply(hdr, local_metadata, standard_metadata); }}\n'

# Takes the content array and substitutes the
# corresponding keys in the template with it,
# outputting the result to the output file
def write_output(content, template_path, output_path):
    # Open template file
    with open(template_path, "r") as template:
        lines = template.readlines()

        # Replace the key with the content
        replaced = 0
        for n in range(len(lines)):
            for index in range(len(REPLACE_KEYS)):
                if REPLACE_KEYS[index] in lines[n]:
                    lines[n] = lines[n].replace(REPLACE_KEYS[index], content[index])
                    replaced += 1
        
        if replaced < len(REPLACE_KEYS):
            print("ERROR: Not all keys were found in the template file.")
            exit(1)

        # Write it to the output file
        create_file(output_path)
        with open(output_path, "w") as output:
            output.writelines(lines)

# Takes the template file, fills it with the functions from the list
# and outputs the result in the desired path
def make_template(functions_list, output_path, template_path=BASE_TEMPLATE_PATH):
    funcs = functions_list
    replace_content = ["", "", ""]
    
    template_path = absolute_path(template_path)
    if not file_exists(template_path): return
    
    output_path = absolute_path(output_path)
    if os.path.isdir(output_path):
        print("ERROR: Output file cannot be a directory.")
        return

    create_content(funcs, replace_content)
    write_output(replace_content, template_path, output_path)

# Runs a makefile with the desired options to build a pipeline
def build_pipeline(p4_path, output_dir, output_name, args="", build_script=BASE_BUILD_SCRIPT):
    p4_path = absolute_path(p4_path)
    if not file_exists(p4_path): return

    build_script = absolute_path(build_script)
    if not file_exists(build_script): return

    output_dir = absolute_path(output_dir)
    if not os.path.exists(output_dir):
        try:
            os.mkdir(output_dir)
        except:
            pass
    elif not os.path.isdir(output_dir):
        print(f"ERROR: {output_dir} is not a directory.")
        return

    command = f"{build_script} {p4_path} {output_dir} {output_name} {args}"
    subprocess.run( shlex.split(command), stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)