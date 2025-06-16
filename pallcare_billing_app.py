import streamlit as st
import math # Import the math library for the ceiling function

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
    """Calculates K023 units dynamically."""
    if time_in_minutes < K023_TIME_THRESHOLDS[0]:
        return 0
        
    billable_units = 0
    for i, threshold in enumerate(K023_TIME_THRESHOLDS):
        if time_in_minutes >= threshold:
            billable_units = i + 1
        else:
            return billable_units
            
    last_threshold_units = len(K023_TIME_THRESHOLDS)
    last_threshold_time = K023_TIME_THRESHOLDS[-1]
    time_past_table = time_in_minutes - last_threshold_time
    additional_units = math.ceil(time_past_table / 30.0)
    return last_threshold_units + additional_units

# --- NEW: Helper function to find the next billing threshold ---
def find_next_threshold_info(time_in_minutes):
    """
    Finds the time required for the next K023 unit and the difference.
    Returns (next_threshold_time, minutes_to_next) or (None, None).
    """
    current_units = calculate_k023_units(time_in_minutes)
    next_unit_count = current_units + 1

    # Case 1: The next unit is within our predefined table.
    if next_unit_count <= len(K023_TIME_THRESHOLDS):
        # The index for N units is N-1.
        next_threshold = K023_TIME_THRESHOLDS[next_unit_count - 1]
        minutes_to_next = next_threshold - time_in_minutes
        return next_threshold, minutes_to_next

    # Case 2: The next unit is beyond the table and must be calculated.
    else:
        # We need to find the threshold for unit N, where N > 8.
        # The formula is: Threshold(N) = 226 + ceil((Threshold(N)-226)/30-epsilon)*30
        # A simpler way is to find the end of the current 30-min bucket and add 1.
        time_past_last_threshold = time_in_minutes - K023_TIME_THRESHOLDS[-1]
        
        # This formula finds the *end* of the current 30-minute block.
        end_of_current_block = K023_TIME_THRESHOLDS[-1] + math.ceil(time_past_last_threshold / 30.0) * 30
        next_threshold = end_of_current_block + 1
        
        minutes_to_next = next_threshold - time_in_minutes
        return next_threshold, minutes_to_next

# --- Streamlit User Interface ---
st.set_page_config(page_title="Palliative Care Billing Calculator (OHIP)", layout="centered")
st.title("Palliative Care Billing Calculator (OHIP)")
st.write("A tool to calculate billing codes for consultations and follow-ups.")

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
        # --- Consultation Logic ---
        if encounter_type == 'Special Palliative Care Consultation':
            if duration_in_minutes < BASE_CONSULT_MIN_TIME:
                st.error(f"Duration ({duration_in_minutes} min) is less than the required {BASE_CONSULT_MIN_TIME} minutes...")
            else:
                time_for_k023 = duration_in_minutes - BASE_CONSULT_MIN_TIME
                num_k023_units = calculate_k023_units(time_for_k023)
                
                # --- NEW: Proximity check ---
                next_thresh, mins_needed = find_next_threshold_info(time_for_k023)
                if mins_needed is not None and 1 <= mins_needed <= 10:
                    st.info(f"💡 You are just {mins_needed} minute(s) away from billing the next unit at {next_thresh} minutes of K023 time.")

                st.success(f"For a {duration_in_minutes} minute CONSULT, you should bill:")
                st.subheader(f"• {BASE_CONSULT_CODE}")
                if num_k023_units > 0:
                    st.subheader(f"• {K023_CODE} x {num_k023_units} unit(s)")
                
                total_payment = BASE_CONSULT_FEE + (num_k023_units * K023_FEE_PER_UNIT)
                st.divider()
                st.metric(label="Total Payment", value=f"${total_payment:.2f}")
                
                with st.expander("Show Payment Breakdown"):
                    st.write(f"`{BASE_CONSULT_CODE}` Fee: `${BASE_CONSULT_FEE:.2f}`")
                    if num_k023_units > 0:
                        k023_total_fee = num_k023_units * K023_FEE_PER_UNIT
                        st.write(f"`{K023_CODE}` Fee ({num_k023_units} units x ${K023_FEE_PER_UNIT:.2f}): `${k023_total_fee:.2f}`")
                
                with st.expander("See Time Breakdown"):
                    st.write(f"**First {BASE_CONSULT_MIN_TIME} min:** Covered by `{BASE_CONSULT_CODE}`.")
                    st.write(f"**Remaining {time_for_k023} min:** Used for `{K023_CODE}` calculation.")

        # --- Follow-up Logic ---
        elif encounter_type == 'Palliative Care Follow-up':
            num_k023_units = calculate_k023_units(duration_in_minutes)
            
            # --- NEW: Proximity check ---
            next_thresh, mins_needed = find_next_threshold_info(duration_in_minutes)
            if mins_needed is not None and 1 <= mins_needed <= 10:
                st.info(f"💡 You are just {mins_needed} minute(s) away from billing the next unit at {next_thresh} minutes.")

            if num_k023_units == 0:
                st.warning(f"Duration ({duration_in_minutes} min) is too short to bill any units...")
            else:
                st.success(f"For a {duration_in_minutes} minute FOLLOW-UP, you should bill:")
                st.subheader(f"• {K023_CODE} x {num_k023_units} unit(s)")
                
                total_payment = num_k023_units * K023_FEE_PER_UNIT
                st.divider()
                st.metric(label="Total Payment", value=f"${total_payment:.2f}")

                with st.expander("Show Payment Breakdown"):
                    k023_total_fee = num_k023_units * K023_FEE_PER_UNIT
                    st.write(f"`{K023_CODE}` Fee ({num_k023_units} units x ${K023_FEE_PER_UNIT:.2f}): `${k023_total_fee:.2f}`")

    else:
        st.warning("Please enter a duration greater than 0.")

st.divider()
st.caption("A tool created by LC.")
