import time
import csv
from enum import IntEnum

# =========================
# STATE DEFINITIONS
# =========================
class AHUState(IntEnum):
    IDLE = 0
    NORMAL = 1
    VENT = 2

class TESState(IntEnum):
    IDLE = 0
    CHARGING = 1
    DISCHARGE = 2


# =========================
# FSM LOGIC (same as yours)
# =========================
def tes_ahu_simple(T_amb, T_des, T_tank, peak):
    T_low = 40
    T_full = 60

    need_heat = T_amb < T_des
    tank_low = T_tank <= T_low
    tank_full = T_tank >= T_full

    if need_heat:
        if peak:
            if not tank_low:
                return AHUState.VENT, TESState.DISCHARGE, 1
            else:
                return AHUState.NORMAL, TESState.IDLE, 2
        else:
            if not tank_full:
                return AHUState.NORMAL, TESState.CHARGING, 3
            else:
                return AHUState.NORMAL, TESState.IDLE, 4
    else:
        if peak:
            return AHUState.IDLE, TESState.IDLE, 5
        else:
            if not tank_full:
                return AHUState.IDLE, TESState.CHARGING, 6
            else:
                return AHUState.IDLE, TESState.IDLE, 7


def actuation_fsm(ahu, tes):
    valve = False
    blower = False
    pump = False
    heater = False

    if tes == TESState.CHARGING:
        heater = True
        pump = True

    elif tes == TESState.DISCHARGE:
        valve = True
        pump = True

    if ahu == AHUState.VENT and tes == TESState.DISCHARGE:
        blower = True

    return valve, blower, pump, heater


# =========================
# TEST SCENARIOS
# =========================
test_cases = [
    # (T_amb, T_des, T_tank, peak, description)
    (20, 25, 50, 1, "Peak + Need Heat + Tank OK → DISCHARGE"),
    (20, 25, 35, 1, "Peak + Need Heat + Tank LOW → IDLE TES"),
    (20, 25, 50, 0, "Off-peak + Need Heat → CHARGING"),
    (26, 25, 50, 1, "Peak + No Heat → IDLE"),
    (26, 25, 50, 0, "Off-peak + No Heat → CHARGING"),
]


# =========================
# CSV LOGGING
# =========================
LOG_FILE = "fsm_test_log.csv"

def init_log():
    with open(LOG_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            "timestamp",
            "test_case",
            "T_amb",
            "T_des",
            "T_tank",
            "peak",
            "ahu_state",
            "tes_state",
            "case_id",
            "valve",
            "blower",
            "pump",
            "heater"
        ])


def log_row(case_desc, T_amb, T_des, T_tank, peak,
            ahu, tes, case_id, valve, blower, pump, heater):

    with open(LOG_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            time.strftime("%H:%M:%S"),
            case_desc,
            T_amb,
            T_des,
            T_tank,
            peak,
            ahu.name,
            tes.name,
            case_id,
            valve,
            blower,
            pump,
            heater
        ])


# =========================
# MAIN TEST LOOP
# =========================
def main():
    init_log()

    for case in test_cases:
        T_amb, T_des, T_tank, peak, desc = case

        print("\n======================================")
        print("RUNNING TEST CASE:")
        print(desc)

        start_time = time.time()

        while time.time() - start_time < 60:   # 1 minute
            ahu, tes, case_id = tes_ahu_simple(T_amb, T_des, T_tank, peak)
            valve, blower, pump, heater = actuation_fsm(ahu, tes)

            # Print live
            print(f"[{desc}]")
            print(f"T_amb={T_amb}, T_des={T_des}, T_tank={T_tank}, peak={peak}")
            print(f"AHU={ahu.name}, TES={tes.name}, Case={case_id}")
            print(f"Valve={valve}, Blower={blower}, Pump={pump}, Heater={heater}")
            print("--------------------------------------")

            # Log
            log_row(desc, T_amb, T_des, T_tank, peak,
                    ahu, tes, case_id, valve, blower, pump, heater)

            time.sleep(2)

    print("\nALL TEST CASES COMPLETE")


if __name__ == "__main__":
    main()