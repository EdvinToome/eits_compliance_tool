import os
import subprocess

from ..base import BaseAssessment
import xmltodict


class APP31M20Assessment(BaseAssessment):
    help_text = "JSON to provide: {'ipv4': ['list_your_ipv4']}"
    type = "automatic"

    def run(self):
        ipv4s = self.extra_input_data.get('ipv4')
        if not ipv4s or not isinstance(ipv4s, list):
            self.passed = False
            self.comments = 'Provide valid list'
            return

        success = True
        for ip in ipv4s:
            result = self.run_nmap_scan(ip)
            output = result.get('nmaprun', {}).get('host', {}).get('ports', {}).get('port', {}).get(
                'script', {}).get('@output', '')
            if 'IDS/IPS/WAF detected' not in output:
                success = False
                self.comments = 'Not all IPv4 addresses have WAF'
                self.extra_return_data.update({ip: output})
            else:
                self.extra_return_data.update({ip: "IDS/IPS/WAF detected"})

        self.passed = success
        if success:
            self.comments = 'All IPv4 addresses have WAF'

    def run_nmap_scan(self, ext_ipv4):
        command = f"nmap -oX - --script http-waf-detect -p 443 {ext_ipv4}"
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0:
            print(f"Error executing nmap: {result.stderr}")
            return None

        return xmltodict.parse(result.stdout)
