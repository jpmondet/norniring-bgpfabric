#! /usr/bin/env python3
"""
    Deploy all the BGP fabric (Cumulus switches + servers)
"""
from __future__ import (
    absolute_import,
    division,
    generators,
    generator_stop,
    unicode_literals,
    print_function,
    nested_scopes,
    with_statement,
)

#    annotations,

from argparse import ArgumentParser

from nornir import InitNornir
from nornir_ansible.plugins.inventory.ansible import AnsibleInventory
from fabric import Fabric


def main():
    """ Main func to initialize Nornir and get started """

    parser = ArgumentParser(
        description="Script to deploy a working RFC5549 BGP Fabric (and to undeploy it as well)"
    )
    parser.add_argument(
        "-u",
        "--undeploy",
        default=False,
        type=bool,
        help="If True, try to unconfigure the deployed Fabric (default: False)",
    )
    #TODO: Add an option to do some connectivity tests

    args = parser.parse_args()

    nr = InitNornir(
        runner={
            #"plugin": "serial",
            "plugin": "threaded",
            "options": {
                "num_workers": 10,
            },
        },
        inventory={
            "plugin": "AnsibleInventory",
            "options": {"hostsfile": "hosts"},
        },
    )
    for key, host in nr.inventory.hosts.items():
        if host.hostname is None:
            host.hostname = key

    print("~~~~~~ Deploying with this inventory ~~~~~~")
    for name, host in nr.inventory.hosts.items():
        vals = host.items()
        print(name, vals)
    print("########## GROUPS ##############")
    for name in nr.inventory.groups:
        print(name, nr.inventory.children_of_group(name))

    fabric = Fabric(nr)

    if args.undeploy:
        fabric.undeploy()
    else:
        fabric.deploy()


if __name__ == "__main__":
    main()
