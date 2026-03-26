"""Report tab renderer.

Generates Excel reports using Riskfolio-lib.
"""

from __future__ import annotations

import pathlib
from datetime import datetime

import pandas as pd
import riskfolio as rp
import streamlit as st


def render_report_tab(
    returns: pd.DataFrame,
    selected_weights: dict[str, float],
    portfolio_choice: str,
    portfolio_label: str,
    portfolio_name: str,
) -> None:
    """Render the Report tab for Excel report generation."""
    st.subheader("Portfolio Excel Report Generator")
    st.write(
        "Generate comprehensive Excel reports for your optimized portfolios using Riskfolio-lib."
    )

    st.info(f"**Current Strategy**: {portfolio_choice}")

    if st.button("Generate Report", key="generate_excel_report"):
        reports_dir = pathlib.Path(__file__).resolve().parent.parent.parent / "exports" / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)

        report_weights_df = pd.DataFrame.from_dict(
            selected_weights, orient="index", columns=[portfolio_name]
        )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_base = f"{portfolio_name}_{timestamp}"
        filepath_base = reports_dir / filename_base

        rp.excel_report(returns=returns, w=report_weights_df, name=str(filepath_base))

        st.success("Excel report generated successfully!")

        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Portfolio**: {portfolio_label}")
        with col2:
            st.info(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        filepath_xlsx = filepath_base.with_suffix(".xlsx")
        with filepath_xlsx.open("rb") as file:
            st.download_button(
                label="Download Excel Report",
                data=file.read(),
                file_name=filename_base + ".xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help=f"Download the {portfolio_label} portfolio Excel report",
            )

        file_size = pathlib.Path(filepath_xlsx).stat().st_size / 1024
        st.caption(f"File: {filename_base}.xlsx ({file_size:.1f} KB)")

    else:
        st.info(
            "Select a portfolio strategy and click 'Generate Report'"
            " to create a comprehensive Excel analysis."
        )

        st.markdown("### Report Contents")
        st.markdown("""
        The Excel report will include:
        - **Portfolio Weights**: Detailed allocation percentages
        - **Performance Metrics**: Returns, volatility, and Sharpe ratio
        - **Risk Analysis**: Comprehensive risk assessment
        - **Asset Statistics**: Individual asset performance data
        - **Correlation Matrix**: Asset correlation analysis
        """)