import streamlit as st

# --- Billing Rule Constants ---
# For Consultations
K023_CONSULT_THRESHOLDS = [20, 46, 76, 106, 136, 166, 196, 226] 
BASE_CONSULT_MIN_TIME = 50
BASE_CONSULT_CODE = "A945/C945"

# For Follow-ups
K023_CODE = "K023"
FOLLOWUP_ADDON_CODE = "C882" # Simplified as requested

# --- Calculation Functions ---
def calculate_consult_k023_units(time_in_minutes):
    """Calculates K023 units for CONSULTATIONS using the threshold list."""
    billable_units = 0
    for i, threshold in enumerate(K023_CONSULT_THRESHOLDS):
        if time_in_minutes >= threshold:
            billable_units = i + 1
    return billable_units

# --- Streamlit User Interface ---
st.set_page_config(page_title="OHIP Billing Calculator", layout="centered")
st.title("OHIP Palliative Care Calculator")
st.write("A tool to calculate billing codes for consultations and follow-ups.")

# --- UI remains the same ---
encounter_type = st.radio(
    "Select the encounter type:",
    ('Special Palliative Care Consultation', 'Palliative Care Follow-up'),
    horizontal=True
)

duration_in_minutes = st.number_input(
    "Enter the total duration in minutes:",
    min_value=0, 
    step=1,
    format="%d"
)

if st.button("Calculate Billing Codes"):
    if duration_in_minutes > 0:
        # --- CONSULTATION LOGIC (UNCHANGED) ---
        if encounter_type == 'Special Palliative Care Consultation':
            if duration_in_minutes < BASE_CONSULT_MIN_TIME:
                st.error(f"Duration ({duration_in_minutes} min) is less than the required {BASE_CONSULT_MIN_TIME} minutes. "
                         f"Cannot bill {BASE_CONSULT_CODE}. Use a standard consultation code instead.")
            else:
                time_for_k023 = duration_in_minutes - BASE_CONSULT_MIN_TIME
                num_k023_units = calculate_consult_k023_units(time_for_k023)
                
                st.success(f"For a {duration_in_minutes} minute CONSULT, you should bill:")
                st.subheader(f"• {BASE_CONSULT_CODE}")
                if num_k023_units > 0:
                    st.subheader(f"• {K023_CODE} x {num_k023_units} unit(s)")
                
                with st.expander("See Time Breakdown"):
                    st.write(f"**First {BASE_CONSULT_MIN_TIME} min:** Covered by {BASE_CONSULT_CODE}.")
                    st.write(f"**Remaining {time_for_k023} min:** Used for {K023_CODE} calculation.")

        # --- FINAL FOLLOW-UP LOGIC (DYNAMIC AND EXTENSIBLE) ---
        elif encounter_type == 'Palliative Care Follow-up':
            st.success(f"For a {duration_in_minutes} minute FOLLOW-UP, you should bill:")

            # 1. Handle the initial special cases from the chart
            if duration_in_minutes < 20:
                st.subheader(f"• {FOLLOWUP_ADDON_CODE}")
            elif duration_in_minutes <= 30:
                st.subheader(f"• {K023_CODE} x 1")
            elif duration_in_minutes <= 45:
                st.subheader(f"• {K023_CODE} x 1")
                st.subheader(f"• {FOLLOWUP_ADDON_CODE}")
            
            # 2. Handle the repeating, dynamic pattern for all longer durations
            else: # This block covers any duration >= 46 minutes
                # The pattern starts at 46 mins. We calculate time relative to that start.
                time_in_pattern = duration_in_minutes - 46
                
                # The number of K023 units increases by 1 for every 30-minute cycle.
                # Base units are 2 (for the 46-60 min block), plus 1 for each cycle.
                cycles = time_in_pattern // 30
                num_k023_units = 2 + cycles
                st.subheader(f"• {K023_CODE} x {num_k023_units}")
                
                # Within each 30-min cycle, the addon is billable in the second 15 mins.
                # We use the remainder (modulo) to find our position in the cycle.
                position_in_cycle = time_in_pattern % 30
                if position_in_cycle > 14:
                    st.subheader(f"• {FOLLOWUP_ADDON_CODE}")

    else:
        st.warning("Please enter a duration greater than 0.")
