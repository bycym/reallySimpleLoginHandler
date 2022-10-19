#!/usr/bin/env python3
DESC="This is a login tool. Collect servers from ~/.ssh/config"
import string
import click
from pathlib import Path
import re
import subprocess
from typing import List
import os
from pathlib import Path

from pyfzf.pyfzf import FzfPrompt
fzf = FzfPrompt()
import re

class Util:
  def searchableSelect(list,listHeaderText):
    originalResult =  fzf.prompt(list,"--layout=reverse --header=\""+listHeaderText+"\"")
    if originalResult is None or len(originalResult) == 0:
      return []
    originalResult = originalResult[0]
    result = originalResult
    result = result.replace("\"","")
    result = result.replace(",","")
    result = result.lstrip()
    result = result.rstrip()
    index = list.index(originalResult)
    return result, index

  def exec(cmd, description="", silent=False, lscWorkingDirectory=True):
      if(description != ""):
          description = description + " : "

      if(silent == False):
          click.echo(description + "".join(cmd))

      workingDirectory = os.path.dirname(os.path.abspath(__file__))
      if(lscWorkingDirectory == False):
        workingDirectory = None

      outs, errs = subprocess.Popen(
          cmd, shell=True, cwd=workingDirectory).communicate()

      if(silent == False):
          click.echo(outs)
      return errs

# UseKeychain yes
# AddKeysToAgent yes
# Host 0.0.0.0
#         ## server type comment
#         HostName 0.0.0.0
#         User yolo
#         IdentityFile ~/.ssh/yolo_id
# Host 0.0.0.1
#         ## server 2
#         HostName 0.0.0.1
#         User yolo1
class ServerConfig:
  def __init__(self, Host, HostComment, Hostname, User, IdentityFile):
    self.Host = Host
    self.HostComment = HostComment
    self.Hostname = Hostname
    self.User = User
    self.IdentityFile = IdentityFile
  Host: string
  HostComment: string
  Hostname: string
  User: string
  IdentityFile: string

@click.command(short_help=DESC)
@click.option('--simple',is_flag=True, default=True, show_default=True, help='Show simple list of servers with comments')
@click.option('-d', '--details', is_flag=True, help="Show detailed server list")
def cli(details, simple):

  home = str(Path.home())
  sshConfigFile = os.path.join(home, ".ssh/config")
  rx = re.compile(r"^Host\s(.*)$\n^\s+##\s?(.*)$\n^\s+HostName\s(.*)$\n^\s+User\s(.*)($\n^\s+IdentityFile\s.*)?$", re.MULTILINE)

  configsRegex = []
  configs = []
  with open(sshConfigFile, 'r') as sshConfigs:
    configsText = sshConfigs.read()
    configsRegex = rx.findall(configsText)

  for config in configsRegex:
    configs.append(ServerConfig(config[0], config[1], config[2], config[3], config[4]))
  
  sshConfigString = ""
  if(details):
    sshConfigString = ([f"{config.User}@{config.Host} # Comment: {config.HostComment}" for config in configs])
  else:
    sshConfigString = ([f"{config.Host} # {config.HostComment}" for config in configs])

  try: 
    selected,index = Util.searchableSelect(sshConfigString,"Select a server") 
  except:
    print("Force quit from fzf")
    exit(1)
  command = f"ssh {configs[index].Host}"
  Util.exec(command)

if __name__ == '__main__':
  cli()