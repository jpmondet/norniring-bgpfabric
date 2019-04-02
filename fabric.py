#! /usr/bin/env python
# pylint: disable=missing-docstring

from __future__ import print_function, unicode_literals
from nornir.plugins.tasks import networking, commands, apis, text, files
from nornir.plugins.functions.text import print_result
from nornir.core.filter import F


class Fabric:
    def __init__(self, nornir):
        self._nornir = nornir

    def linux_local_cmd(self, cmd):
        local = self._nornir.filter(F(platform="linux"))
        cmd_res = local.run(task=commands.command, command=cmd)
        print_result(cmd_res)

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

    def send_j2_command(self, filtered_nr, command_j2):
        commands_rendered = filtered_nr.run(
            text.template_string, template=command_j2
        )
        for _, cmds in commands_rendered.items():
            filtered_nr.run(commands.remote_command, command=cmds.result)

    def configuring_interfaces(self):
        rendered = self.render_template("interfaces.j2")
        for name, config in rendered.items():
            self.to_remote_file(f"interfaces", config, name, "/etc/network/")

    def flushing_interfaces(self):
        # hosts = self._nornir.filter(~F(platform="linux"))
        hosts = self._nornir.filter(
            F(role="servers") | F(role="spine") | F(role="leaf")
        )
        command_j2 = "sudo su ; {% for intf in host.interfaces -%} ip addr flush dev {{ intf.name }} && ifup {{ intf.name }} --force ; {% endfor -%}"
        self.send_j2_command(hosts, command_j2)

    def net_restart(self):
        # hosts = self._nornir.filter(~F(platform="linux"))
        hosts = self._nornir.filter(
            F(role="servers") | F(role="spine") | F(role="leaf")
        )
        command = "sudo systemctl restart networking"
        hosts.run(commands.remote_command, command=command)

    def install_frr(self):
        srvs = self._nornir.filter(F(role="servers"))
        # Trick to retrieve the frr version from the set of servers
        first_srv = next(iter(srvs.inventory.hosts.keys()))
        frr_ver = self._nornir.inventory.hosts[first_srv]["frr_version"]
        install_cmds = f"sudo su ; curl -s https://deb.frrouting.org/frr/keys.asc | sudo apt-key add -i ; echo deb https://deb.frrouting.org/frr $(lsb_release -s -c) {frr_ver} | sudo tee -a /etc/apt/sources.list.d/frr.list ; sudo apt update && sudo apt install frr frr-pythontools"
        srvs.run(commands.remote_command, command=install_cmds)

    def configuring_frr(self):
        rendered_bgp = self.render_template("bgp.j2")
        for name, config in rendered_bgp.items():
            self.to_remote_file(name, f"frr.conf", config, "/etc/frr/")

        with open('./templates/daemons', 'r') as daemons:
            self.to_remote_file(f"daemons", daemons, "/etc/frr/")

    def restart_frr(self):
        hosts = self._nornir.filter(
            F(role="servers") | F(role="spine") | F(role="leaf")
        )
        command = "sudo systemctl restart frr"
        hosts.run(commands.remote_command, command=command)

    def deploy(self):
        """ Workflow """

        # self.linux_local_cmd('ls -alh')
        # self.calling_api("https://api.chucknorris.io/jokes/random", 'get')

        # Installing FRR on servers
        self.install_frr()

        # Handling interfaces
        self.configuring_interfaces()
        self.flushing_interfaces()
        self.net_restart()

        # Configuring BGP and restarting FRR on all nodes
        self.configuring_frr()
        self.restart_frr()
