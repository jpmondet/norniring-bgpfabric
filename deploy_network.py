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

    args = parser.parse_args()

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
            host.platform = "linux"

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
