class BaseAssessment:
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
