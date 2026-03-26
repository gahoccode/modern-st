"""Tab renderer modules for Streamlit application.

Each module contains a single render function responsible for
rendering its corresponding tab in the main application.
"""

from frontend.tabs.efficient_frontier import render_efficient_frontier_tab
from frontend.tabs.hrp import render_hrp_tab
from frontend.tabs.allocation import render_allocation_tab
from frontend.tabs.report import render_report_tab
from frontend.tabs.risk_analysis import render_risk_analysis_tab

__all__ = [
    "render_efficient_frontier_tab",
    "render_hrp_tab",
    "render_allocation_tab",
    "render_report_tab",
    "render_risk_analysis_tab",
]