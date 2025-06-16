import streamlit as st

# --- Billing Rule Constants ---
K023_TIME_THRESHOLDS = [20, 46, 76, 106, 136, 166, 196, 226]
BASE_CONSULT_MIN_TIME = 50
BASE_CONSULT_CODE = "A945/C945"
K023_CODE = "K023"

# --- Fee Constants ---
BASE_CONSULT_FEE = 159.20
K023_FEE_PER_UNIT = 74.70

# --- Calculation Functions ---
def calculate_k023_units(time_in_minutes):
    billable_units = 0
    for i, threshold in enumerate(K023_TIME_THRESHOLDS):
        if time_in_minutes >= threshold:
            billable_units = i + 1
    return billable_units

# --- Streamlit User Interface ---
st.set_page_config(page_title="Palliative Care Billing Calculator (OHIP)", layout="centered")
st.title("Palliative Care Billing Calculator (OHIP)")
st.write("A tool to calculate billing codes for consultations and follow-ups.")

# UI remains the same
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

# A button to trigger the calculation
if st.button("Calculate Billing Codes"):
    if duration_in_minutes > 0:
        # --- Consultation Logic with Payment Breakdown ---
        if encounter_type == 'Special Palliative Care Consultation':
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
                
                total_payment = BASE_CONSULT_FEE + (num_k023_units * K023_FEE_PER_UNIT)
                st.divider()
                st.metric(label="Total Payment", value=f"${total_payment:.2f}")
                
                # --- NEW: Payment Breakdown Expander ---
                with st.expander("Show Payment Breakdown"):
                    st.write(f"`{BASE_CONSULT_CODE}` Fee: `${BASE_CONSULT_FEE:.2f}`")
                    if num_k023_units > 0:
                        k023_total_fee = num_k023_units * K023_FEE_PER_UNIT
                        st.write(f"`{K023_CODE}` Fee ({num_k023_units} units x ${K023_FEE_PER_UNIT:.2f}): `${k023_total_fee:.2f}`")
                
                with st.expander("See Time Breakdown"):
                    st.write(f"**First {BASE_CONSULT_MIN_TIME} min:** Covered by `{BASE_CONSULT_CODE}`.")
                    st.write(f"**Remaining {time_for_k023} min:** Used for `{K023_CODE}` calculation.")

        # --- Follow-up Logic with Payment Breakdown ---
        elif encounter_type == 'Palliative Care Follow-up':
            num_k023_units = calculate_k023_units(duration_in_minutes)
            
            if num_k023_units == 0:
                min_time_for_one_unit = K023_TIME_THRESHOLDS[0]
                st.warning(f"Duration ({duration_in_minutes} min) is too short to bill any units of `{K023_CODE}`. "
                           f"A minimum of {min_time_for_one_unit} minutes is required.")
            else:
                st.success(f"For a {duration_in_minutes} minute FOLLOW-UP, you should bill:")
                st.subheader(f"• {K023_CODE} x {num_k023_units} unit(s)")
                
                total_payment = num_k023_units * K023_FEE_PER_UNIT
                st.divider()
                st.metric(label="Total Payment", value=f"${total_payment:.2f}")

                # --- NEW: Payment Breakdown Expander ---
                with st.expander("Show Payment Breakdown"):
                    k023_total_fee = num_k023_units * K023_FEE_PER_UNIT
                    st.write(f"`{K023_CODE}` Fee ({num_k023_units} units x ${K023_FEE_PER_UNIT:.2f}): `${k023_total_fee:.2f}`")

    else:
        st.warning("Please enter a duration greater than 0.")
