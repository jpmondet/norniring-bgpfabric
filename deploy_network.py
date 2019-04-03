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
        core={"num_workers": 1},
        inventory={
            "plugin": "nornir.plugins.inventory.ansible.AnsibleInventory",
            "options": {"hostsfile": "hosts"},
        },
    )
    for key, host in nr.inventory.hosts.items():
        if host.hostname is None:
            host.hostname = key
            host.port = 22
            host.platform = 'linux'

    print("~~~~~~ Deploying with this inventory ~~~~~~")
    for name, host in nr.inventory.hosts.items():
        vals = host.items()
        print(name, vals)
    print("########## GROUPS ##############")
    for name in nr.inventory.groups:
        print(name, nr.inventory.children_of_group(name))

    fabric = Fabric(nr)
    fabric.deploy()

if __name__ == "__main__":
    main()
