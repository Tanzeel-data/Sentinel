import sys
from pathlib import Path

import streamlit as st


# ============================================================
# Ensure project root is on Python path
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from app.graph.graph import sentinel_graph
# ============================================================
# Page Configuration
# ============================================================

st.set_page_config(
    page_title="Sentinel | AI Infrastructure Operations",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# Custom Styling
# ============================================================

st.markdown(
    """
    <style>

    .main {
        padding-top: 1rem;
    }

    .sentinel-title {
        font-size: 2.6rem;
        font-weight: 800;
        margin-bottom: 0;
    }

    .sentinel-subtitle {
        font-size: 1rem;
        opacity: 0.7;
        margin-top: 0;
        margin-bottom: 2rem;
    }

    .section-title {
        font-size: 1.25rem;
        font-weight: 700;
        margin-top: 1rem;
        margin-bottom: 0.75rem;
    }

    .approval-warning {
        padding: 1.1rem;
        border-radius: 10px;
        border: 1px solid #d97706;
        background: rgba(217, 119, 6, 0.10);
        margin-top: 0.75rem;
        margin-bottom: 1rem;
    }

    .resolved {
        padding: 1rem;
        border-radius: 10px;
        background: rgba(34, 197, 94, 0.10);
        border: 1px solid rgba(34, 197, 94, 0.4);
        margin-top: 0.75rem;
    }

    .not-resolved {
        padding: 1rem;
        border-radius: 10px;
        background: rgba(239, 68, 68, 0.10);
        border: 1px solid rgba(239, 68, 68, 0.4);
        margin-top: 0.75rem;
    }

    .metric-label {
        font-size: 0.85rem;
        opacity: 0.7;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# Header
# ============================================================

st.markdown(
    '<div class="sentinel-title">🛡️ Sentinel</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="sentinel-subtitle">'
    "AI Infrastructure Investigation & Safe Remediation"
    "</div>",
    unsafe_allow_html=True,
)


# ============================================================
# Sidebar
# ============================================================

with st.sidebar:

    st.header("Sentinel")

    st.caption(
        "AI-powered infrastructure operations assistant"
    )

    st.divider()

    st.markdown("### Workflow")

    st.markdown(
        """
        **1.** 🔍 Monitor  
        **2.** 🧠 Diagnose  
        **3.** 🛠️ Recommend  
        **4.** ✅ Verify
        """
    )

    st.divider()

    st.markdown("### Safety")

    st.caption(
        "Sentinel prioritizes investigation and "
        "non-destructive actions."
    )

    st.caption(
        "Potentially disruptive remediation requires "
        "explicit human approval."
    )

    st.divider()

    st.caption("Sentinel • AI Infrastructure Operations")


# ============================================================
# User Request
# ============================================================

st.markdown(
    '<div class="section-title">Infrastructure Request</div>',
    unsafe_allow_html=True,
)

user_query = st.text_area(
    "Describe the infrastructure issue you want Sentinel to investigate.",
    value=(
        "Investigate servers with high CPU or memory usage "
        "and recommend safe remediation."
    ),
    height=100,
    label_visibility="collapsed",
)

run_button = st.button(
    "🔍 Run Sentinel Investigation",
    type="primary",
    use_container_width=True,
)


# ============================================================
# Run Workflow
# ============================================================

if run_button:

    if not user_query.strip():

        st.warning("Please enter an infrastructure request.")

        st.stop()

    initial_state = {
        "user_query": user_query.strip(),
        "retry_count": 0,
        "max_retries": 2,
    }

    with st.spinner(
        "Sentinel is investigating the infrastructure..."
    ):

        try:

            result = sentinel_graph.invoke(initial_state)

            st.session_state["sentinel_result"] = result

        except Exception as exc:

            st.error("Sentinel workflow failed.")

            st.exception(exc)

            st.stop()


# ============================================================
# Display Results
# ============================================================

if "sentinel_result" in st.session_state:

    result = st.session_state["sentinel_result"]

    st.divider()

    # ========================================================
    # Workflow Status
    # ========================================================

    st.markdown(
        '<div class="section-title">Workflow Status</div>',
        unsafe_allow_html=True,
    )

    verification_result = result.get("verification_result", "")

    verification_text = str(
        verification_result
    ).upper()

    if "NOT_RESOLVED" in verification_text:
        verify_label = "🔴 Verify — NOT RESOLVED"
    elif "RESOLVED" in verification_text:
        verify_label = "🟢 Verify — RESOLVED"
    else:
        verify_label = "✓ Verify"

    progress = st.columns(4)

    with progress[0]:
        st.success("✓ Monitor")

    with progress[1]:
        st.success("✓ Diagnose")

    with progress[2]:
        st.success("✓ Recommend")

    with progress[3]:
        if "NOT_RESOLVED" in verification_text:
            st.error(verify_label)
        else:
            st.success(verify_label)

    # ========================================================
    # Resource Metrics
    # ========================================================

    cpu = result.get("cpu_usage")
    memory = result.get("memory_usage")

    if cpu is not None or memory is not None:

        st.markdown(
            '<div class="section-title">Current Resource Usage</div>',
            unsafe_allow_html=True,
        )

        metric_cols = st.columns(2)

        with metric_cols[0]:

            st.metric(
                "CPU Usage",
                f"{cpu:.1f}%" if cpu is not None else "N/A",
            )

        with metric_cols[1]:

            st.metric(
                "Memory Usage",
                f"{memory:.1f}%" if memory is not None else "N/A",
            )

    # ========================================================
    # Monitoring
    # ========================================================

    monitoring_result = result.get("monitoring_result")

    if monitoring_result:

        st.markdown(
            '<div class="section-title">🔍 Monitoring</div>',
            unsafe_allow_html=True,
        )

        with st.expander(
            "View monitoring analysis",
            expanded=True,
        ):

            st.markdown(monitoring_result)

    # ========================================================
    # Diagnosis
    # ========================================================

    diagnosis_result = result.get("diagnosis_result")

    if diagnosis_result:

        st.markdown(
            '<div class="section-title">🧠 Diagnosis</div>',
            unsafe_allow_html=True,
        )

        with st.expander(
            "View diagnostic analysis",
            expanded=True,
        ):

            st.markdown(diagnosis_result)

    # ========================================================
    # Remediation
    # ========================================================

    remediation_result = result.get("remediation_result")

    remediation_validation = result.get(
        "remediation_validation"
    )

    if remediation_result:

        st.markdown(
            '<div class="section-title">🛠️ Remediation Recommendation</div>',
            unsafe_allow_html=True,
        )

        # Remove duplicated safety section from agent output.
        clean_remediation = str(
            remediation_result
        ).split("### Safety Guardrail")[0].strip()

        with st.expander(
            "View recommended remediation",
            expanded=True,
        ):

            st.markdown(clean_remediation)

    # ========================================================
    # Safety Guardrail
    # ========================================================

    if remediation_validation:

        requires_approval = remediation_validation.get(
            "requires_approval",
            False,
        )

        if requires_approval:

            st.markdown(
                """
                <div class="approval-warning">

                ⚠️ <strong>Human Approval Required</strong>

                <br><br>

                Sentinel identified a potentially disruptive
                remediation action.

                <br><br>

                <strong>No remediation action has been executed.</strong>

                </div>
                """,
                unsafe_allow_html=True,
            )

        else:

            st.success(
                "🛡️ Safety Guardrail: "
                "Recommendation passed validation. "
                "No disruptive action requires approval."
            )

    # ========================================================
    # Verification
    # ========================================================

    if verification_result:

        st.markdown(
            '<div class="section-title">✅ Verification</div>',
            unsafe_allow_html=True,
        )

        with st.expander(
            "View verification evidence",
            expanded=True,
        ):

            st.markdown(verification_result)

        # ----------------------------------------------------
        # Verification Status
        # ----------------------------------------------------

        if "NOT_RESOLVED" in verification_text:

            st.markdown(
                """
                <div class="not-resolved">

                🔴 <strong>Verification Status: NOT RESOLVED</strong>

                <br><br>

                The infrastructure issue remains active.
                Further investigation or approved remediation
                may be required.

                </div>
                """,
                unsafe_allow_html=True,
            )

        elif "RESOLVED" in verification_text:

            st.markdown(
                """
                <div class="resolved">

                🟢 <strong>Verification Status: RESOLVED</strong>

                <br><br>

                The latest telemetry indicates that the
                investigated issue has been resolved.

                </div>
                """,
                unsafe_allow_html=True,
            )

    # ========================================================
    # Technical State
    # ========================================================

    with st.expander("🔧 View Sentinel State"):

        st.json(result)