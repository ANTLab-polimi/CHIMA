from cmd import Cmd
import shlex

from defines import network, int_funcs
from containers import *
from utils import *
from pipelines import *
from templating.templates import *
from deployment import *
from triggers import *

#Used to get user commands
class CHIMAshell(Cmd):
    prompt="chima> "
    intro = """ _____  _   _ ________  ___  ___  
/  __ \| | | |_   _|  \/  | / _ \ 
| /  \/| |_| | | | | .  . |/ /_\ \\
| |    |  _  | | | | |\/| ||  _  |
| \__/\| | | |_| |_| |  | || | | |
 \____/\_| |_/\___/\_|  |_/\_| |_/
"""

    def do_topo(self, args):
        print(dump_topology(network, int_funcs))
    
    def help_topo(self):
        print("topo\n  Show a textual representation of the network")

    def do_compose(self, args):
        args = shlex.split(args)
        if len(args) != 2:
            self.help_compose()
        else:
            composeUp([args[0]], args[1])

    def help_compose(self):
        print("compose (compose_file) (host_ip)\n  Deploy the Docker Compose specification on the specified host")

    def do_decompose(self, args):
        args = shlex.split(args)
        if len(args) != 2:
            self.help_decompose()
        else:
            composeStop(args[0], args[1])

    def help_decompose(self):
        print("decompose (compose_file) (host_ip)\n  Stop the Docker Compose specification on the specified host")

    def do_install(self, args):
        args = shlex.split(args)
        if len(args) != 3:
            self.help_install()
        else:
            install_pipeline(args[0], absolute_path(args[1]), absolute_path(args[2]))
    
    def help_install(self):
        print("install (device_id) (json_file) (p4info_file)\n  Install a P4 program on the specified device at runtime")

    def do_template(self, args):
        args = shlex.split(args)
        if len(args) != 3 and len(args) != 2:
            self.help_template()
        else:
            funcs = []
            functions_path = absolute_path(args[0])
            if file_exists(functions_path):
                read_functions(functions_path, funcs)
                if len(args) == 2:
                    make_template(funcs, args[1])
                elif len(args) == 3:
                    make_template(funcs, args[1], args[2])
    
    def help_template(self):
        print("template (functions_file) (p4_output_file) [template_path]\n  Output a P4 file that is the composition of a template and a set of functions")

    def do_build(self, args):
        args = shlex.split(args)
        if len(args) < 3 or len(args) >5:
            self.help_build()
        elif len(args) == 3:
            build_pipeline(args[0], args[1], args[2])
        elif len(args) == 4:
            build_pipeline(args[0], args[1], args[2], args[3])
        elif len(args) == 5:
            build_pipeline(args[0], args[1], args[2], args[3], args[4])
    
    def help_build(self):
        print("build (p4_program_file) (output_dir) (output_name) [args] [build_script]\n  Build a pipeline with the specified makefile")

    def do_deploy(self, args):
        args = shlex.split(args)
        if len(args) == 1:
            testcase = "../measurements/%s/" % args[0]
            load_deployment(testcase+"service.yaml", testcase+"dep.yaml")
        elif len(args) != 2:
            self.help_deploy()
        else:
            load_deployment(args[0], args[1])            
    
    def help_deploy(self):
        print("deploy (service_yaml) (deployment_yaml)\n  Execute a deployment described by a deployment yaml file")
        print("deploy (testcase)\n  Execute the deployment of a testcase in the standard location")

    def do_redeploy(self, args):
        args = shlex.split(args)
        if len(args) != 2:
            self.help_redeploy()
        else:
            redeploy(args[0], args[1])            
    
    def help_redeploy(self):
        print("redeploy (old_yaml_file) (new_yaml_file)\n  Change a deployment")
    
    def do_dismantle(self, args):
        args = shlex.split(args)
        if len(args) != 1:
            self.help_dismantle()
        else:
            undo_deployment_file(args[0])
    
    def help_dismantle(self):
        print("dismantle (yaml_file)\n  Dismantle a deployment described by a deployment yaml file")

    def do_triggers(self, args):
        args = shlex.split(args)
        if len(args) != 0:
            self.help_deploy()
        else:
            show_triggers(triggers)
    
    def help_triggers(self):
        print("triggers\n  Show result of triggers evaluation")
    
    def do_exit(self, args):
        return True

    def help_exit(self):
        print("exit\n  Close CHIMA")
    
    def emptyline(self):
         pass