from __future__ import annotations

import streamlit as st

from app.finance import annuity_loan_schedule, first_year_loan_payments
from app.formatting import nok, signed_nok


def render_mortgage_tab(tab, ctx: dict, default, description) -> None:
    with tab:
        st.subheader("Mortgage payment plan")
        st.caption("Annuity-loan view aligned more closely with the DNB-style calculator, with an optional sale-driven prepayment.")
        use_sidebar_loan_used = st.checkbox(
            "Use actual bank loan used from sidebar",
            value=default("mortgage", "use_sidebar_loan_used", True),
            help=description("mortgage", "use_sidebar_loan_used", "When enabled, the Mortgage Plan loan principal follows the actual bank loan used from the sidebar rather than a separate manual value."),
        )
        use_sidebar_financing_terms = st.checkbox(
            "Use rate and term from sidebar",
            value=default("mortgage", "use_sidebar_financing_terms", True),
            help=description("mortgage", "use_sidebar_financing_terms", "When enabled, the Mortgage Plan rate and loan term follow the sidebar financing assumptions so coverage and schedule views stay aligned."),
        )

        col1, col2 = st.columns(2)
        with col1:
            mortgage_principal_input = st.number_input(
                "Loan principal",
                min_value=0,
                value=default("mortgage", "principal", 16_000_000),
                step=250_000,
                help=description("mortgage", "principal", "Principal borrowed from the bank. Increasing it improves purchase capacity but raises repayment and interest burden."),
                disabled=use_sidebar_loan_used,
            )
            mortgage_principal = ctx["loan_used"] if use_sidebar_loan_used else mortgage_principal_input
            establishment_fee = st.number_input("Establishment fee", min_value=0, value=default("mortgage", "establishment_fee", 120_000), step=10_000, help=description("mortgage", "establishment_fee", "One-off fee charged when the loan is set up."))
            monthly_term_fee = st.number_input("Monthly term fee", min_value=0, value=default("mortgage", "monthly_term_fee", 70), step=10, help=description("mortgage", "monthly_term_fee", "Monthly bank fee added to each payment."))
            mortgage_rate_input = st.slider(
                "Nominal annual rate %",
                0.0,
                12.0,
                default("mortgage", "rate", 6.85),
                0.01,
                help=description("mortgage", "rate", "Nominal bank interest rate. Increasing it raises the interest portion of every payment."),
                disabled=use_sidebar_financing_terms,
            )
            mortgage_rate = ctx["nominal_rate"] if use_sidebar_financing_terms else mortgage_rate_input
        with col2:
            mortgage_years_input = st.slider(
                "Loan term (years)",
                1,
                30,
                default("mortgage", "years", 15),
                help=description("mortgage", "years", "Loan duration. Shorter terms increase monthly principal payments but reduce debt faster."),
                disabled=use_sidebar_financing_terms,
            )
            mortgage_years = ctx["amort_years"] if use_sidebar_financing_terms else mortgage_years_input
            sale_delay_months = st.slider("Months until current-building sale", 0, 36, default("mortgage", "sale_delay_months", 9), help=description("mortgage", "sale_delay_months", "Delay before the current building is sold. Increasing it delays the benefit of any prepayment and keeps interest higher for longer."))
            sale_prepayment_share = st.slider("Share of loan repaid on sale %", 0.0, 100.0, default("mortgage", "sale_prepayment_share", 75.0), 1.0, help=description("mortgage", "sale_prepayment_share", "Planning assumption for how much of the outstanding loan is repaid when the sale occurs. Higher values lower later interest and payment burden."))
            include_sale_prepayment = st.checkbox("Apply sale prepayment in schedule", value=True, help=description("mortgage", "include_sale_prepayment", "Turn this on to model a lump-sum loan reduction when the current building is sold."))

        if use_sidebar_loan_used or use_sidebar_financing_terms:
            st.write(
                f"Mortgage plan is currently using sidebar financing assumptions: principal `{nok(mortgage_principal)}`, rate `{mortgage_rate:.2f}%`, term `{mortgage_years}` years."
            )

        schedule = annuity_loan_schedule(
            principal=mortgage_principal,
            annual_rate_pct=mortgage_rate,
            years=mortgage_years,
            upfront_fee=establishment_fee,
            monthly_fee=monthly_term_fee,
            prepayment_month=sale_delay_months if include_sale_prepayment and sale_delay_months > 0 else None,
            prepayment_share=sale_prepayment_share / 100 if include_sale_prepayment else 0.0,
        )

        if schedule:
            first_year = schedule[:12]
            year_one_total = sum(item["total_payment"] for item in first_year)
            last_payment = schedule[-1]["total_payment"]
            first_payment = schedule[0]["total_payment"]
            remaining_after_12 = first_year[-1]["closing_balance"] if first_year else mortgage_principal

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Month 1 payment", nok(first_payment))
            c2.metric("Month 12 payment", nok(schedule[min(11, len(schedule) - 1)]["total_payment"]))
            c3.metric("Year 1 total", nok(year_one_total))
            c4.metric("Balance after 12 months", nok(remaining_after_12))

            st.write(
                f"Without rate changes, the payment stays broadly level because this is now modeled as an annuity loan. "
                f"The last scheduled payment is about `{nok(last_payment)}`."
            )

            stress_rate_addition = st.slider(
                "Rate stress test: extra percentage points",
                0.0,
                5.0,
                float(default("mortgage", "stress_rate_addition", 1.5)),
                0.1,
                help="Use this to test how much the yearly mortgage burden rises if the interest environment worsens above the base case.",
            )
            stressed_year_one_total = first_year_loan_payments(
                mortgage_principal,
                mortgage_rate + stress_rate_addition,
                mortgage_years,
                monthly_fee=monthly_term_fee,
            ) + establishment_fee
            m1, m2 = st.columns(2)
            m1.metric("Base year-1 mortgage burden", nok(year_one_total))
            m2.metric(
                f"Year-1 burden at {mortgage_rate + stress_rate_addition:.2f}%",
                nok(stressed_year_one_total),
                signed_nok(stressed_year_one_total - year_one_total),
            )

            if include_sale_prepayment and sale_delay_months > 0:
                prepay_rows = [row for row in schedule if row["extra_prepayment"] > 0]
                if prepay_rows:
                    prepay = prepay_rows[0]
                    st.info(
                        f"Sale assumption applied in month {int(prepay['month'])}: extra prepayment `{nok(prepay['extra_prepayment'])}`."
                    )
                    before_sale = prepay
                    after_sale_candidates = [row for row in schedule if row["month"] == prepay["month"] + 1]
                    if after_sale_candidates:
                        after_sale = after_sale_candidates[0]
                        k1, k2, k3, k4 = st.columns(4)
                        k1.metric("Interest before sale", nok(before_sale["interest_payment"]))
                        k2.metric("Interest after sale", nok(after_sale["interest_payment"]))
                        k3.metric("Payment before sale", nok(before_sale["total_payment"]))
                        k4.metric("Payment after sale", nok(after_sale["total_payment"]))
                        st.write(
                            f"The model assumes interest drops from about `{nok(before_sale['interest_payment'])}` "
                            f"to about `{nok(after_sale['interest_payment'])}` after the sale-driven repayment."
                        )

            st.markdown("First 12 months")
            first_12_rows = []
            for row in first_year:
                first_12_rows.append(
                    {
                        "Month": int(row["month"]),
                        "Opening balance": nok(row["opening_balance"]),
                        "Principal": nok(row["principal_payment"]),
                        "Interest": nok(row["interest_payment"]),
                        "Fee": nok(row["monthly_fee"]),
                        "Extra prepay": nok(row["extra_prepayment"]),
                        "Total payment": nok(row["total_payment"]),
                        "Closing balance": nok(row["closing_balance"]),
                    }
                )
            st.table(first_12_rows)

            st.caption(
                "This schedule is a planning approximation. The bank's actual repayment plan may differ slightly because of exact day-count, rounding, fees, and disbursement timing."
            )

        ctx["mortgage_principal"] = mortgage_principal
        ctx["mortgage_rate"] = mortgage_rate
        ctx["mortgage_years"] = mortgage_years
        ctx["mortgage_establishment_fee"] = establishment_fee
        ctx["mortgage_monthly_term_fee"] = monthly_term_fee
        ctx["sale_delay_months"] = sale_delay_months
        ctx["sale_prepayment_share"] = sale_prepayment_share
        ctx["include_sale_prepayment"] = include_sale_prepayment
        ctx["mortgage_schedule"] = schedule
