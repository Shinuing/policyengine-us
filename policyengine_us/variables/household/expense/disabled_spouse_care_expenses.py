from policyengine_us.model_api import *


class disabled_spouse_care_expenses(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax unit disabled spouse care expenses"
    unit = USD
    definition_period = YEAR
    defined_for = "disabled_spouse"
