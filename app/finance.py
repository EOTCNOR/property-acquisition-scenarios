from __future__ import annotations


def annuity_payment(principal: float, monthly_rate: float, months: int) -> float:
    if principal <= 0 or months <= 0:
        return 0.0
    if monthly_rate <= 0:
        return principal / months
    factor = (1 + monthly_rate) ** months
    return principal * monthly_rate * factor / (factor - 1)


def annuity_loan_schedule(
    principal: float,
    annual_rate_pct: float,
    years: int,
    upfront_fee: float = 0.0,
    monthly_fee: float = 0.0,
    prepayment_month: int | None = None,
    prepayment_share: float = 0.0,
) -> list[dict[str, float]]:
    if principal <= 0 or years <= 0:
        return []

    months = years * 12
    monthly_rate = annual_rate_pct / 100 / 12
    balance = principal
    schedule: list[dict[str, float]] = []

    for month in range(1, months + 1):
        opening_balance = balance
        remaining_months = months - month + 1
        scheduled_payment = annuity_payment(opening_balance, monthly_rate, remaining_months)
        interest = opening_balance * monthly_rate
        principal_payment = min(max(scheduled_payment - interest, 0.0), opening_balance)
        extra_prepayment = 0.0

        if prepayment_month and month == prepayment_month and prepayment_share > 0:
            extra_prepayment = max(opening_balance - principal_payment, 0.0) * prepayment_share

        total_payment = principal_payment + interest + monthly_fee + extra_prepayment
        closing_balance = max(opening_balance - principal_payment - extra_prepayment, 0.0)
        schedule.append(
            {
                "month": month,
                "opening_balance": opening_balance,
                "principal_payment": principal_payment,
                "interest_payment": interest,
                "monthly_fee": monthly_fee,
                "extra_prepayment": extra_prepayment,
                "total_payment": total_payment,
                "closing_balance": closing_balance,
            }
        )
        balance = closing_balance
        if balance <= 0:
            break

    if schedule and upfront_fee:
        schedule[0]["total_payment"] += upfront_fee
    return schedule


def first_year_loan_payments(loan_amount: float, rate_pct: float, amort_years: int, monthly_fee: float = 0.0) -> float:
    schedule = annuity_loan_schedule(
        principal=loan_amount,
        annual_rate_pct=rate_pct,
        years=amort_years,
        monthly_fee=monthly_fee,
    )
    return sum(item["total_payment"] for item in schedule[:12])
