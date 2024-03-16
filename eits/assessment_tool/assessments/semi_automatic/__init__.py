from django.db.models import Q
from django.urls import reverse

from ..base import BaseAssessment


class NET22M3Assessment(BaseAssessment):
    type = 'semi_automatic'

    def run(self):
        archi_constraints = self.company_assessment.company.archimate_objects.filter(
            Q(type='Constraint') & (Q(name__icontains="VPN") | Q(documentation__icontains="VPN"))
        )
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
