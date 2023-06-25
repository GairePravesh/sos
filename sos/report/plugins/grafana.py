# Copyright (C) 2016 Red Hat, Inc., Pratik Bandarkar <pbandark@redhat.com>

# This file is part of the sos project: https://github.com/sosreport/sos
#
# This copyrighted material is made available to anyone wishing to use,
# modify, copy, or redistribute it subject to the terms and conditions of
# version 2 of the GNU General Public License.
#
# See the LICENSE file in the source distribution for further information.

from sos.report.plugins import Plugin, IndependentPlugin


class Grafana(Plugin, IndependentPlugin):

    short_desc = 'Fetch Grafana configuration, logs and CLI output'
    plugin_name = "grafana"
    profiles = ('services', 'openstack', 'openstack_controller')

    packages = ('grafana',)

    def _is_snap_installed(self):
        grafana_pkg = self.policy.package_manager.pkg_by_name('grafana')
        if grafana_pkg:
            return grafana_pkg['pkg_manager'] == 'snap'
        return False

    def setup(self):
        self._is_snap = self._is_snap_installed()
        if self._is_snap:
            self.add_cmd_output([
                'snap info grafana',
                'grafana.grafana-cli plugins ls',
                'grafana.grafana-cli plugins list-remote'
            ])
            if self.get_option("all_logs"):
                self.add_copy_spec([
                    "/var/snap/grafana/common/data/log/grafana.log*",
                ])
            else:
                self.add_copy_spec([
                    "/var/snap/grafana/common/data/log/grafana.log"
                ])
            self.add_copy_spec("/var/snap/grafana/current/conf/grafana.ini")
        else:
            if self.get_option("all_logs"):
                self.add_copy_spec("/var/log/grafana/*.log*")
            else:
                self.add_copy_spec("/var/log/grafana/*.log")

            self.add_cmd_output([
                "grafana-cli plugins ls",
                "grafana-cli plugins list-remote",
                "grafana-cli -v",
                "grafana-server -v",
            ])

            self.add_copy_spec([
                "/etc/grafana/",
                "/etc/sysconfig/grafana-server",
            ])

    def postproc(self):
        protect_keys = [
            "admin_password",
            "secret_key",
            "password",
            "client_secret"
        ]
        if self._is_snap:
            regexp = r"((?m)^\s*(%s)\s*=\s*)(.*)" % "|".join(protect_keys)
            self.do_path_regex_sub(
                "/var/snap/grafana/current/conf/grafana.ini",
                regexp,
                r"\1*********"
            )
        else:
            regexp = r"((?m)^\s*(%s)\s*=\s*)(.*)" % "|".join(protect_keys)
            self.do_path_regex_sub(
                "/etc/grafana/grafana.ini",
                regexp,
                r"\1*********"
            )
