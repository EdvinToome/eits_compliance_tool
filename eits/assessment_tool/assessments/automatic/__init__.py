from ..base import BaseAssessment


class APP31M20Assessment(BaseAssessment):
    help_text = "JSON to provide: {'ipv4': ['list_your_ipv4']}"
    type = "automatic"

    def run(self):
        ipv4s = self.extra_input_data.get('ipv4')
        if not ipv4s or not isinstance(ipv4s, list):
            ipv4s = self.get_ext_ipv4()

        success = True
        for ip in ipv4s:
            result = self.run_nmap_scan(ip, "http-waf-detect", "443")
            output = result.get('nmaprun', {}).get('host', {}).get('ports', {}).get('port', {}).get(
                'script', {}).get('@output', '')
            if 'IDS/IPS/WAF detected' not in output:
                success = False
                self.comments += f"{ip} IDS/IPS/WAF not detected \n\n"
                if output:
                    self.extra_return_data.update({ip: output})
                else:
                    self.extra_return_data.update({ip: "IDS/IPS/WAF not found"})
            else:
                self.comments += f"{ip} IDS/IPS/WAF detected \n\n"
                self.extra_return_data.update({ip: "IDS/IPS/WAF detected"})

        self.passed = success
        if success:
            self.comments = 'All IPv4 addresses have WAF'


class CON10M14Assessment(BaseAssessment):
    help_text = "JSON to provide: {'ipv4': ['list_your_ipv4']}"
    type = "automatic"

    def check_x_frame_options_compliance(self, value):
        if isinstance(value, list):
            return any(item.startswith("Header: X-Frame-Options: DENY") for item in value)
        return value.startswith("Header: X-Frame-Options: DENY")

    def run(self):
        ipv4s = self.extra_input_data.get('ipv4')
        if not ipv4s or not isinstance(ipv4s, list):
            ipv4s = self.get_ext_ipv4()
        success = True
        for ip in ipv4s:
            result = self.run_nmap_scan(ip, "http-security-headers", "443")
            http_headers = result['nmaprun']['host']['ports']['port']['script']['table']
            parsed_headers = {header['@key']: header['elem'] for header in http_headers}

            compliance_checks = {
                "Strict_Transport_Security": "Strict_Transport_Security" in parsed_headers,
                "X_Frame_Options": self.check_x_frame_options_compliance(parsed_headers.get("X_Frame_Options", "")),
                "X_XSS_Protection": "X_XSS_Protection" in parsed_headers and "1; mode=block" in str(
                    parsed_headers["X_XSS_Protection"]),
                "X_Content_Type_Options": "X_Content_Type_Options" in parsed_headers and "nosniff" in str(
                    parsed_headers["X_Content_Type_Options"]),
                "Content_Security_Policy": "Content_Security_Policy" in parsed_headers,
                "Cache_Control": "Cache_Control" in parsed_headers,
                "Cookie": "Cookie" in parsed_headers and 'Cookies are secured with Secure Flag in HTTPS Connection' in
                          parsed_headers["Cookie"]
            }
            if not all(compliance_checks.values()):
                success = False
                self.comments += f"{ip} failed in several areas: {', '.join([key for key, value in compliance_checks.items() if not value])} \n\n"
                self.extra_return_data.update({ip: [compliance_checks, parsed_headers]})
            else:
                self.extra_return_data.update({ip: compliance_checks})
        self.passed = success


class NET12M31Assessment(BaseAssessment):
    help_text = "JSON to provide: {'ipv4': ['list_your_ipv4']}"
    type = "automatic"

    def run(self):
        ipv4s = self.extra_input_data.get('ipv4')
        if not ipv4s or not isinstance(ipv4s, list):
            ipv4s = self.get_ext_ipv4()
        success = True
        for ip in ipv4s:
            tls = []
            result = self.run_nmap_scan(ip, "ssl-enum-ciphers", "443")
            cipher_ver_tables = result['nmaprun']['host']['ports']['port']['script']['table']
            cipher_tables = []
            if isinstance(cipher_ver_tables, list):
                for ver in cipher_ver_tables:
                    if ver['@key'] not in ['TLSv1.2', 'TLSv1.3']:
                        tls.append(ver['@key'])
                        success = False
                    cipher_tables.extend(ver['table'])
            else:
                cipher_tables = cipher_ver_tables['table']
                if cipher_ver_tables['@key'] not in ['TLSv1.2', 'TLSv1.3']:
                    tls.append(cipher_ver_tables['@key'])
                    success = False
            ciphers_list = next(item for item in cipher_tables if item['@key'] == 'ciphers')['table']
            extracted_ciphers = []
            for cipher in ciphers_list:
                cipher_details = {elem['@key']: elem['#text'] for elem in cipher['elem']}
                extracted_ciphers.append(cipher_details)
            if not all(cipher['strength'] == 'A' for cipher in extracted_ciphers):
                success = False
                self.comments += f"{ip} failed in several areas: {', '.join([cipher['name'] + ' Strength: ' + cipher['strength']  for cipher in extracted_ciphers if cipher['strength'] != 'A'])} \n\n"
                self.extra_return_data.update({ip: extracted_ciphers})
            else:
                self.extra_return_data.update({ip: 'Passed'})
            if tls:
                self.comments += f"IP {ip} uses insecure versions of TLS: {', '.join(tls)} \n\n"
                self.extra_return_data[ip] = f"Insecure versions of TLS: {', '.join(tls)}"
        self.passed = success
