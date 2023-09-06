from policyengine_us.model_api import *


class wv_social_security_deduction_eligible(Variable):
    value_type = float
    entity = TaxUnit
    label = "West Virginia social security deduction eligible"
    unit = USD
    definition_period = YEAR
    reference = "https://tax.wv.gov/Documents/PIT/2022/PersonalIncomeTaxFormsAndInstructions.2022.pdf#Page=25"
    defined_for = StateCode.WV

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        adjusted_gross_income = tax_unit("wv_agi", period)
        p = parameters(
            period
        ).gov.states.wv.tax.income.subtractions.social_security_benefit
        return adjusted_gross_income <= p.income_limit[filing_status]