import subprocess
import shlex
import os
from utils import absolute_path, file_exists

## Management of containers installation on correctly configured hosts

# The port for the host is assumed to be 2375
# It is the same one used to check if a host
# exposes a docker engine

def composeUp(composeFilePaths, host):
    try:
        files = ""
        for path in composeFilePaths:
            path = absolute_path(path)
            if not file_exists(path): return
            files += f"-f {path} "

        command = f"docker-compose {files} up -d"
        result = subprocess.run( shlex.split(command), env={**os.environ, "DOCKER_HOST": host+":2375"}, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

        if(result.returncode != 0):
            print(result.stderr)

        return result.returncode
    except:
        print(f"ERROR: Unable to run '{command}' on the host {host}:2375")
        return 1

def composeBuild(composeFilePath, host):
    try:
        composeFilePath = absolute_path(composeFilePath)
        if not file_exists(composeFilePath): return

        command = f"docker-compose -f {composeFilePath} build"
        result = subprocess.run( shlex.split(command), env={**os.environ, "DOCKER_HOST": host+":2375"}, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE )

        if(result.returncode != 0):
            print(result.stderr)

        return result.returncode
    except:
        print(f"ERROR: Unable to run '{command}' on the host {host}:2375")
        return 1

def composeStop(composeFilePath, host):
    try:
        composeFilePath = absolute_path(composeFilePath)
        if not file_exists(composeFilePath): return
        
        command = f"docker-compose -f {composeFilePath} stop"
        result = subprocess.run( shlex.split(command), env={**os.environ, "DOCKER_HOST": host+":2375"}, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE )

        if(result.returncode != 0):
            print(result.stderr)

        return result.returncode
    except:
        print(f"ERROR: Unable to run '{command}' on the host {host}:2375")
        return 1