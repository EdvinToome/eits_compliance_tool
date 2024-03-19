import re
import subprocess

import xmltodict


class BaseAssessment:
    """
    Name of superclass must be control group_id without dots and Assessment appended to the end,
    example: NET22M3Assessment
    """

    def __init__(self, company_assessment, extra_input_data):
        self.company_assessment = company_assessment
        self.passed: bool = False
        self.comments: str = ''
        self.extra_input_data = extra_input_data
        self.extra_return_data: dict = {}

    help_text = ""
    type = ""

    def run(self):
        raise NotImplementedError("Each assessment must implement the 'run' method.")

    def get_result_data(self):
        return {"status": self.passed, "comments": self.comments, "extra_fields": self.extra_return_data}

    def run_nmap_scan(self, ext_ipv4, script, port):
        command = f"nmap -oX - --script {script} -p {port} {ext_ipv4}"
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0:
            print(f"Error executing nmap: {result.stderr}")
            return None

        return xmltodict.parse(result.stdout)

    def get_ext_ipv4(self) -> list[str]:
        valid_domains = []
        domains = self.company_assessment.company.archimate_objects.filter(
            type="ApplicationInterface"
        )

        for domain in domains:
            domain_name = domain.name
            pattern = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,6}$'

            if re.match(pattern, domain_name):
                try:
                    subprocess.check_output(['ping', '-c', '1', '-W', '1', domain_name], stderr=subprocess.STDOUT)
                    valid_domains.append(domain_name)
                except subprocess.CalledProcessError:
                    pass

        return valid_domains


class BaseManualAssessment(BaseAssessment):
    type = 'manual'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.comments = f"You have to manually test this assessment \n\n {self.company_assessment.control.description}"

    def run(self):
        return
