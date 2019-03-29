#! /usr/bin/env python

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

    def calling_api(self, url, method):
        local = self._nornir.filter(F(platform="linux"))
        api_res = local.run(task=apis.http_method, method=method, url=url)
        print_result(api_res)

    def render_template(self, tplate, path='./templates'):
        hosts = self._nornir.filter(~F(platform="linux"))
        rendered_cfg = hosts.run(text.template_file, template=tplate, path=path)
        #print_result(rendered_cfg)
        rendered_cfg_dict = dict()
        for name, res in rendered_cfg.items():
            rendered_cfg_dict[name] = res.result

        return rendered_cfg_dict

    def to_local_file(self, filename, content, path='./resources/'):
        hosts = self._nornir.filter(~F(platform="linux"))
        hosts.run(files.write_file, filename=path + filename, content=content)

    def to_remote_file(self, filename, content, path='./resources/'):
        hosts = self._nornir.filter(~F(platform="linux"))
        hosts.run(commands.command('echo 

    def configure_interfaces(self):
        for intf in self._nornir.inventory.hosts['leaf01']['interfaces']:
            cmd_res = local.run(task=commands.command, command=cmd)

    def deploy(self):
        pass
