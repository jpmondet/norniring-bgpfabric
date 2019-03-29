#! /usr/bin/env python3
"""
    Deploy all the BGP fabric (Cumulus switches + servers)
"""

import ipdb
from pprint import pprint
import json

from nornir import InitNornir
from fabric import Fabric




def main():
    """ Main func to initialize Nornir and get started """

    nr = InitNornir(
        core={"num_workers": 5},
        inventory={
            "plugin": "nornir.plugins.inventory.ansible.AnsibleInventory",
            "options": {
                "hostsfile": "hosts"
            }
        }
    )
    print("~~~~~~ Deploying with this inventory ~~~~~~")
    for name, host in nr.inventory.hosts.items():
        vals = host.items()
        print(name, vals)
    print("########## GROUPS ##############")
    for name in nr.inventory.groups:
        print(name, nr.inventory.children_of_group(name))

    fabric = Fabric(nr)
    #fabric.linux_local_cmd('ls -alh')
    #fabric.calling_api("https://api.chucknorris.io/jokes/random", 'get')
    #fabric.deploy()
    rendered = fabric.render_template('interfaces.j2')
    for name, config in rendered.items():
        fabric.to_file(f'interfaces-{name}.conf', config)

if __name__ == "__main__":
    main()
