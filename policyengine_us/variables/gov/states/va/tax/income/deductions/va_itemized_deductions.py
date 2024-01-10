from policyengine_us.model_api import *


class va_itemized_deductions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia itemized deductions"
    unit = USD
    definition_period = YEAR
    reference = "https://www.tax.virginia.gov/sites/default/files/taxforms/individual-income-tax/2021/schedule-2021.pdf"
    defined_for = StateCode.VA

    def formula(tax_unit, period, parameters):
        year = period.start.year
        # Viginia applies the federal itemized deduction rate which was established before 2018
        if year >= 2018 and year <= 2026:
            instant_str = f"2017-01-01"

        irs = parameters(instant_str).gov.irs.deductions.itemized.limitation
        p = parameters(period).gov.irs.deductions.itemized.limitation
        # va itemized deductions
        itm_deds_less_salt = tax_unit("itemized_deductions_less_salt", period)
        uncapped_property_taxes = add(tax_unit, period, ["real_estate_taxes"])
        va_itm_deds = itm_deds_less_salt + uncapped_property_taxes

        # Part A: If AGI from federal return is over a certain amount, then
        # limitations to the itemized deduction are applied
        federal_agi = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)
        applicable_amount = p.applicable_amount[filing_status]
        agi_adjustment = irs.agi_rate * max_(
            federal_agi - applicable_amount, 0
        )
        itm_deds_adjustment = irs.itemized_deduction_rate * va_itm_deds
        va_itm_deds_adjustment = min_(agi_adjustment, itm_deds_adjustment)

        # Part B: state and local income tax modification
        # the foreign income tax is considered but not modeled here
        adjustment_fraction = np.zeros_like(va_itm_deds)
        mask = va_itm_deds != 0
        adjustment_fraction[mask] = (
            va_itm_deds_adjustment[mask] / va_itm_deds[mask]
        )

        # Virginia Schedule A fails to mention if state and local income taxes cannot be negative
        salt = tax_unit("state_and_local_sales_or_income_tax", period)
        state_and_local_income_tax_adjustment = (
            salt - salt * adjustment_fraction
        )

        va_limited_itm_deds = max_(
            va_itm_deds_adjustment - state_and_local_income_tax_adjustment, 0
        )

        return where(
            federal_agi > applicable_amount, va_limited_itm_deds, va_itm_deds
        )
