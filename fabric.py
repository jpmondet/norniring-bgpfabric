#! /usr/bin/env python
# pylint: disable=missing-docstring, line-too-long, bad-continuation

from __future__ import (
    absolute_import,
    division,
    generators,
    generator_stop,
    unicode_literals,
    print_function,
    nested_scopes,
    with_statement,
)  # , annotations

from nornir.plugins.tasks import commands, apis, text, files
from nornir.plugins.functions.text import print_result
from nornir.core.filter import F


class Fabric:
    def __init__(self, nornir):
        self._nornir = nornir

    def linux_local_cmd(self, cmd):
        local = self._nornir.filter(F(role="local"))
        cmd_res = local.run(task=commands.command, command=cmd)
        print_result(cmd_res)

    @staticmethod
    def run_remote_cmd(task, cmd):
        res = task.run(commands.remote_command, command=cmd)
        print_result(res)

    def to_local_file(self, filename, content, path="./resources/"):
        hosts = self._nornir.filter(F(platform="linux"))
        hosts.run(files.write_file, filename=path + filename, content=content)

    def calling_api(self, url, method):
        local = self._nornir.filter(F(platform="linux"))
        api_res = local.run(task=apis.http_method, method=method, url=url)
        print_result(api_res)

    def render_template(self, tplate, path="./templates"):
        # hosts = self._nornir.filter(~F(platform="linux"))
        hosts = self._nornir.filter(
            F(role="servers") | F(role="spine") | F(role="leaf")
        )
        rendered_cfg = hosts.run(
            text.template_file, template=tplate, path=path
        )
        # print_result(rendered_cfg)
        rendered_cfg_dict = dict()
        for name, res in rendered_cfg.items():
            rendered_cfg_dict[name] = res.result

        return rendered_cfg_dict

    def to_remote_file(
        self, filename, content, name=None, path="./resources/"
    ):
        # hosts = self._nornir.filter(~F(platform="linux"))
        if not name:
            hosts = self._nornir.filter(
                F(role="servers") | F(role="spine") | F(role="leaf")
            )
        else:
            hosts = self._nornir.filter(F(hostname=name))
        command = f'sudo su ; echo "{content}" > {path}{filename}'
        hosts.run(commands.remote_command, command=command)
        # print_result(res)

    @staticmethod
    def copy_files(task, src_file, dst_file, named=True):
        if named:
            task.run(
                files.sftp,
                action="put",
                src=f"{src_file}-{task.host.name}",
                dst=dst_file,
            )
        else:
            task.run(files.sftp, action="put", src=f"{src_file}", dst=dst_file)

    def send_j2_command(self, filtered_nr, command_j2):
        commands_rendered = filtered_nr.run(
            text.template_string, template=command_j2
        )
        for name, cmds in commands_rendered.items():
            unique_srv = self._nornir.filter(F(hostname=name))
            unique_srv.run(self.run_remote_cmd, cmd=cmds.result)

    def configuring_interfaces(self):
        rendered = self.render_template("interfaces.j2")
        for name, config in rendered.items():
            self.to_local_file(f"interfaces-{name}", config)

        hosts = self._nornir.filter(
            F(role="servers") | F(role="spine") | F(role="leaf")
        )
        res = hosts.run(
            task=self.copy_files,
            src_file="./resources/interfaces",
            dst_file="/tmp/interfaces",
        )
        print_result(res)
        hosts.run(
            task=self.run_remote_cmd,
            cmd="sudo cp /tmp/interfaces /etc/network/interfaces",
        )

    def flushing_interfaces(self):
        # hosts = self._nornir.filter(~F(platform="linux"))
        hosts = self._nornir.filter(
            F(role="servers") | F(role="spine") | F(role="leaf")
        )
        command_j2 = "{% for intf in host.interfaces -%} sudo ip addr flush dev {{ intf.name }} && sudo ifup {{ intf.name }} --force ; {% endfor -%}"
        self.send_j2_command(hosts, command_j2)

    def net_restart(self):
        # hosts = self._nornir.filter(~F(platform="linux"))
        hosts = self._nornir.filter(
            F(role="servers") | F(role="spine") | F(role="leaf")
        )
        command = "sudo systemctl restart networking"
        hosts.run(self.run_remote_cmd, cmd=command)

    def install_frr(self):
        hosts = self._nornir.filter(
            F(role="servers") | F(role="spine") | F(role="leaf")
        )
        # Trick to retrieve the frr version from the set of servers
        # first_srv = next(iter(srvs.inventory.hosts.keys()))
        # frr_ver = self._nornir.inventory.hosts[first_srv]["frr_version"]
        # install_cmds = f"curl -s https://deb.frrouting.org/frr/keys.asc | sudo apt-key add -i ; echo deb https://deb.frrouting.org/frr $(lsb_release -s -c) {frr_ver} | sudo tee /etc/apt/sources.list.d/frr.list ; sudo apt install -y --allow-unauthenticated frr frr-pythontools"
        # install_cmds = "curl -sLO https://github.com/FRRouting/frr/releases/download/frr-6.0.2/frr_6.0.2-0.ubuntu16.04.1_amd64.deb ; sudo apt-get install -y --allow-unauthenticated ./frr_6.0.2-0.ubuntu16.04.1_amd64.deb"
        install_cmds = "sudo apt install -y frr"
        res = hosts.run(task=self.run_remote_cmd, cmd=install_cmds)
        print_result(res)

    def configuring_frr(self):
        rendered = self.render_template("bgp.j2")
        for name, config in rendered.items():
            self.to_local_file(f"frrconf-{name}", config)

        hosts = self._nornir.filter(
            F(role="servers") | F(role="spine") | F(role="leaf")
        )
        res = hosts.run(
            task=self.copy_files,
            src_file="./resources/frrconf",
            dst_file="/tmp/frr.conf",
        )
        print_result(res)
        res = hosts.run(
            task=self.copy_files,
            src_file="./templates/daemons",
            dst_file="/tmp/daemons",
            named=False,
        )
        print_result(res)
        hosts.run(
            task=self.run_remote_cmd,
            cmd="sudo cp /tmp/frr.conf /etc/frr/frr.conf",
        )
        hosts.run(
            task=self.run_remote_cmd,
            cmd="sudo cp /tmp/daemons /etc/frr/daemons",
        )

    def restart_frr(self):
        hosts = self._nornir.filter(
            F(role="servers") | F(role="spine") | F(role="leaf")
        )
        command = "sudo systemctl restart frr"
        hosts.run(self.run_remote_cmd, cmd=command)

    @staticmethod
    def delimiter(action):
        print("#" * 50)
        print(action)
        print("#" * 50)

    def deploy(self):
        """ Workflow to deploy a fully bgp fabric on CITC """

        # self.linux_local_cmd('ls -alh')
        # self.calling_api("https://api.chucknorris.io/jokes/random", 'get')

        # Installing FRR
        self.delimiter("Installing FRR")
        self.install_frr()

        # Handling interfaces
        self.delimiter("Prep ifaces config")
        self.configuring_interfaces()
        self.delimiter("Flushing Ifaces just in case")
        self.flushing_interfaces()
        self.delimiter("Restarting the network")
        self.net_restart()

        # Configuring BGP and restarting FRR on all nodes
        self.delimiter("Prep bgp config")
        self.configuring_frr()
        self.delimiter("Restart frr")
        self.restart_frr()

    def uninstall_frr(self):
        # srvs = self._nornir.filter(F(role="servers"))
        hosts = self._nornir.filter(
            F(role="servers") | F(role="spine") | F(role="leaf")
        )
        uninstall_cmds = "sudo apt remove -y frr ; sudo rm -rf /etc/frr/ /tmp/frr.conf /tmp/interfaces /tmp/daemons"
        res = hosts.run(task=self.run_remote_cmd, cmd=uninstall_cmds)
        print_result(res)

    def unconfigure_ifaces(self):
        hosts = self._nornir.filter(
            F(role="servers") | F(role="spine") | F(role="leaf")
        )
        res = hosts.run(
            task=self.run_remote_cmd,
            cmd='echo -e "auto lo\niface lo inet loopback\nauto eth0\niface eth0 inet dhcp" > /etc/network/interfaces',
        )
        print_result(res)

    def undeploy(self):
        """ Unconfigure all the fabric """

        self.delimiter("Uninstalling FRR and removing its files")
        self.uninstall_frr()

        # Handling interfaces
        self.delimiter("Unconfigure interfaces")
        self.unconfigure_ifaces()
        self.delimiter("Flushing Ifaces")
        self.flushing_interfaces()
        self.delimiter("Restarting the network")
        self.net_restart()
