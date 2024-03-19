from django.db.models import Q

from ..base import BaseAssessment


class NET22M3Assessment(BaseAssessment):
    type = 'semi_automatic'

    def run(self):
        archi_constraints = self.company_assessment.company.archimate_objects.filter(
            Q(type='Constraint') & (Q(name__icontains="VPN") | Q(documentation__icontains="VPN"))
        )

        if not archi_constraints:
            self.comments = "Couldn't find any archimate objects related to VPN"

        for archi_constraint in archi_constraints:
            self.extra_return_data[archi_constraint.name] = {"description": archi_constraint.documentation,
                                                             "related_objects": [
                                                                 {
                                                                     "name": str(related_obj),
                                                                     "documentation": related_obj.documentation,
                                                                     "properties": related_obj.properties
                                                                 }
                                                                 for related_obj in
                                                                 archi_constraint.get_related_objects()
                                                             ]}
            self.comments = ("VPN access rule found. Verify that it complies with the requirement: "
                             "Võõrast raadiokohtvõrgust saab kasutaja organisatsiooni siseressursside "
                             "poole pöörduda ainult virtuaalse privaatvõrgu (VPN)"
                             " kaudu (vt NET.3.3: Virtuaalne privaatvõrk (VPN)).")


class CON8M10Assessment(BaseAssessment):
    type = 'semi_automatic'

    def run(self):
        search_terms = ["Source code", "Bitbucket", "GitHub", "GitLab"]
        query_conditions = Q()
        for term in search_terms:
            query_conditions |= Q(name__icontains=term) | Q(documentation__icontains=term)
        archi_objects = self.company_assessment.company.archimate_objects.filter(query_conditions)
        if not archi_objects:
            self.comments("Couldn't find any archimate objects related to source code management")
        for archi_object in archi_objects:
            self.extra_return_data[archi_object.name] = {"description": archi_object.documentation,
                                                         "related_objects": [
                                                             {
                                                                 "name": str(related_obj),
                                                                 "documentation": related_obj.documentation,
                                                                 "properties": related_obj.properties
                                                             }
                                                             for related_obj in
                                                             archi_object.get_related_objects()
                                                         ]}
            self.comments = (
                "Source code management system found. Verify that it complies with the measure:"
                " a. Tarkvara lähtekoodi (ingl source code) turvalisuse tagamiseks ja koodimuudatuste haldamiseks on "
                "rakendatud sobivad versioonihalduse tööriistad. b. Koodis tehtud muudatused salvestatakse "
                "versioonihalduse käigus eraldi versioonina. Vajadusel on võimalik tehtud muudatusi tagasi võtta "
                "(taastada muudatuse-eelne lähtekoodi versioon). "
                "c. Andmevarunduse kontseptsioon arvestab tarkvara versiooni muutusi. Enne ja pärast uue "
                "tarkvaraversiooni paigaldamist varundatakse tarkvaras kasutatavad andmed.")
