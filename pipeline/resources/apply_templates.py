import json

class TemplateParts:
    include = 0
    define = 1
    apply = 2

class Function:
    def __init__(self, include, control):
        self.include = include
        self.control = control

TEMPLATE_PATH="include/mpls_template.p4"
OUTPUT_PATH = "include/mpls.p4"
REPLACE_KEYS= ["###FUNCTION_INCLUDE###", "###FUNCTION_DEFINE###", "###FUNCTION_APPLY###"]

# Reads function definitions from a json file
# and populates a list of functions with them
def read_functions(filepath, funcs):
    with open(filepath, "r") as file:
        data = json.load(file)
        for f in data:
            funcs.append(Function(f["include"], f["control"]))

# Takes a list of functions and creates the
# appropriate content strings to use in a
# template
def create_content(funcs, content):
    for index in range(len(funcs)):
        f = funcs[index]
        content[TemplateParts.include] += f'#include "{f.include}"\n'
        content[TemplateParts.define] += f'{f.control}() {f.control}_{index};\n'
        content[TemplateParts.apply] += f'if(hdr.mpls_stack[index].label == {index}) {{ {f.control}_{index}.apply(hdr, local_metadata, standard_metadata); }}\n'

# Takes the content array and substitutes the
# corresponding keys in the template with it,
# outputting the result to the output file
def make_output(content):
    # Open template file
    with open(TEMPLATE_PATH, "r") as template:
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
        with open(OUTPUT_PATH, "w") as output:
            output.writelines(lines)

if __name__ == "__main__":
    funcs = []
    replace_content = ["", "", ""]

    read_functions("functions.json", funcs)
    create_content(funcs, replace_content)
    make_output(replace_content)