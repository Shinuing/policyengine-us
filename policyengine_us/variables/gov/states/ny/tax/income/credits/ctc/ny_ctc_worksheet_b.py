from policyengine_us.model_api import *


class ny_ctc_worksheet_a(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY Worksheet A for Form IT-213"
    documentation = "New York's Empire State Child Credit Worksheet B"
    unit = USD
    definition_period = YEAR
    reference = "https://www.tax.ny.gov/pdf/2021/inc/it213i_2021.pdf#page=3"
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ny.tax.income.credits.ctc
        person = tax_unit.members
        # Line 1
        ctc_qualifying_child = person("ctc_qualifying_child", period)
        qualifying_children = tax_unit.sum(ctc_qualifying_child)
        base_credit = qualifying_children * p.amount.base
        # Line 2 NY recomputed FAGI - use normal FAGI
        fagi = tax_unit("adjusted_gross_income", period)
        # Line 3
        total_exclusions = add(tax_unit, period, ["foreign_earned_income_exclusion", "puerto_rico_income"])
        # Line 4
        agi_with_exclusion_amount = total_exclusions + fagi
        # Line 5
        federal_threshold = gov.irs.credits.ctc.phase_out.threshold[
            tax_unit("filing_status", period)
        ]
        # Line 6
        agi_over_threshold = agi_with_exclusion_amount > federal_threshold
        # The reduced AGI is rounded up to the nearest NY CTC base amount
        rounded_reduced_agi_multiple = np.ceil(agi_with_exclusion_amount - federal_threshold / p.amount.base)
        rounded_reduced_agi_amount =rounded_reduced_agi_multiple * p.amount.base
        rounded_reduced_agi = where(agi_over_threshold, rounded_reduced_agi_amount, 0)
        # Line 7
        subtraction_amount = rounded_reduced_agi * p.amount.match
        # Line 8
        adjusted_base_credit = max_(base_credit - subtraction_amount, 0)
        # Part 2 from Worksheet B
        # Line 9
        tax = tax_unit("income_tax", period)
        # Line 10 ccompare agi and recomputed FAGI - skip here, assume they are same
        selected_credit_amount = tax_unit("ny_ctc_federal_credits", period)

        # Line 12 
        reduced_income_tax = max_(0, tax - selected_credit_amount)
        #Line 13
        base_credit_over_reduced_income_tax = adjusted_base_credit > reduced_income_tax
        return where(base_credit_over_reduced_income_tax, reduced_income_tax, 0)
