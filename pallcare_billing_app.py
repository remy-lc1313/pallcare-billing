import streamlit as st

# --- Billing Rule Constants (Same as before) ---
K023_TIME_THRESHOLDS = [20, 46, 76, 106, 136, 166, 196, 226]
BASE_CONSULT_MIN_TIME = 50
BASE_CONSULT_CODE = "A945/C945"
K023_CODE = "K023"

# --- Calculation Functions (Same as before) ---
def calculate_k023_units(time_in_minutes):
    billable_units = 0
    for i, threshold in enumerate(K023_TIME_THRESHOLDS):
        if time_in_minutes >= threshold:
            billable_units = i + 1
    return billable_units

# --- Streamlit User Interface ---
st.set_page_config(page_title="OHIP Billing Calculator", layout="centered")
st.title("OHIP Palliative Care Calculator")
st.write("A tool to calculate billing codes for consultations and follow-ups.")

# Use radio buttons for a cleaner interface
encounter_type = st.radio(
    "Select the encounter type:",
    ('Special Palliative Care Consultation', 'Palliative Care Follow-up'),
    horizontal=True
)

# Use a number input field for the duration
duration_in_minutes = st.number_input(
    "Enter the total duration in minutes:",
    min_value=0, 
    step=1,
    format="%d"
)

# A button to trigger the calculation
if st.button("Calculate Billing Codes"):
    if duration_in_minutes > 0:
        if encounter_type == 'Special Palliative Care Consultation':
            # --- Consultation Logic ---
            if duration_in_minutes < BASE_CONSULT_MIN_TIME:
                st.error(f"Duration ({duration_in_minutes} min) is less than the required {BASE_CONSULT_MIN_TIME} minutes. "
                         f"Cannot bill {BASE_CONSULT_CODE}. Use a standard consultation code instead.")
            else:
                time_for_k023 = duration_in_minutes - BASE_CONSULT_MIN_TIME
                num_k023_units = calculate_k023_units(time_for_k023)
                
                st.success(f"For a {duration_in_minutes} minute CONSULT, you should bill:")
                st.subheader(f"• {BASE_CONSULT_CODE}")
                if num_k023_units > 0:
                    st.subheader(f"• {K023_CODE} x {num_k023_units} unit(s)")
                
                with st.expander("See Time Breakdown"):
                    st.write(f"**First {BASE_CONSULT_MIN_TIME} min:** Covered by {BASE_CONSULT_CODE}.")
                    st.write(f"**Remaining {time_for_k023} min:** Used for {K023_CODE} calculation.")

        elif encounter_type == 'Palliative Care Follow-up':
            # --- Follow-up Logic ---
            num_k023_units = calculate_k023_units(duration_in_minutes)
            
            if num_k023_units == 0:
                min_time_for_one_unit = K023_TIME_THRESHOLDS[0]
                st.warning(f"Duration ({duration_in_minutes} min) is too short to bill any units of {K023_CODE}. "
                           f"A minimum of {min_time_for_one_unit} minutes is required.")
            else:
                st.success(f"For a {duration_in_minutes} minute FOLLOW-UP, you should bill:")
                st.subheader(f"• {K023_CODE} x {num_k023_units} unit(s)")
    else:
        st.warning("Please enter a duration greater than 0.")
