from policyengine_us.model_api import *
import datetime
import math


class va_age_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia age deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=16"
    defined_for = StateCode.VA

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.va.tax.income.subtractions.age_deduction
        filing_status = tax_unit("filing_status", period)
        # input the age of the head of household (and the spouse if applicable)
        filing_statuses = filing_status.possible_values
        single = filing_status == filing_statuses.SINGLE
        joint = filing_status == filing_statuses.JOINT
        separate = filing_status == filing_statuses.SEPARATE

        age_head = tax_unit("age_head", period)
        age_spouse = where(single, 0, tax_unit("age_spouse", period))
        # age_spouse = tax_unit("age_spouse", period)

        AFAGI = tax_unit("AFAGI", period)
        # People who were born on or before the threshold date are eligible for a full deduction
        threshhold_date = datetime.datetime.strptime("1939-01-01", "%Y-%m-%d")

        # calcualte the number of people eligble for age deduction in a household (people who are 65 and older)
        eligible_count = sum(
            where(age_head >= p.va_age, 1, 0),
            where(age_spouse >= p.va_age, 1, 0),
        )

        # calculate the number of people age >=84 and is eligible for a full deduction
        birth_year_head = period.start.year - age_head
        birth_year_spouse = period.start.year - age_spouse
        full_deduction_count = sum(
            where(birth_year_head < int(threshhold_date.year), 1, 0),
            where(birth_year_spouse < int(threshhold_date.year), 1, 0),
        )

        age_deduction = (
            p.maximum_allowable_amount * eligible_count
            - (where(eligible_count == full_deduction_count, 0, 1))
            * (
                AFAGI
                - where(joint | separate, p.married_limit, p.single_limit)
            )
        ) / where(joint, 1, eligible_count)
        return where(math.isnan(age_deduction), 0, age_deduction)
