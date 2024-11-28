import math

# Set time value for temp below table range to highest value (ideally infinity)
max_time = 999
verbose = True
safe_D = 6.5 # according to FDA

def get_D_value(T):
    temperatures = [137, 140, 145, 150, 155, 160]
    D_values = [82, 35, 14, 5, 1, 0.1]
    log_D_values = [math.log10(D) for D in D_values]
    
    if T < temperatures[0]:
        D_value = max_time
        if verbose:
            print(f"Temperature {T}°F is below the minimum table value of {temperatures[0]}°F.")
        print(f"Using D-value: D = {D_value} minutes\n")
        return D_value
    elif T > temperatures[-1]:
        D_value = D_values[-1]
        if verbose:
            print(f"Temperature {T}°F is above the maximum table value of {temperatures[-1]}°F.")
        print(f"Using D-value: D = {D_value} minutes\n")
        return D_value
    else:
        for i in range(len(temperatures)-1):
            T1 = temperatures[i]
            T2 = temperatures[i+1]
            if T1 <= T <= T2:
                log_D1 = log_D_values[i]
                log_D2 = log_D_values[i+1]
                # Linear interpolation on log_D
                log_D = log_D1 + (log_D2 - log_D1)*(T - T1)/(T2 - T1)
                D_value = 10 ** log_D
                if verbose:
                    print(f"Interpolating D-value for T = {T}°F between {T1}°F and {T2}°F:")
                    print(f"log_D1 = log10({D_values[i]}) = {log_D1:.1f}")
                    print(f"log_D2 = log10({D_values[i+1]}) = {log_D2:.1f}")
                    print(f"Interpolated log_D = {log_D:.1f}")
                print(f"Interpolated D-value = 10^{log_D:.1f} = {D_value:.1f} minutes\n")
                return D_value
    return None

def run_tests():
    print("\nRunning core computation logic tests...\n")
    tests_passed = True

    # Test cases for get_D_value function
    test_temperatures = [130, 137, 138.5, 140, 142.5, 145, 147.5, 150, 155, 160, 162]
    expected_D_values = [max_time, 82, None, 35, None, 14, None, 5, 1, 0.1, 0.1]

    print("Testing D-value interpolation and edge cases:")
    for T in test_temperatures:
        D_value = get_D_value(T)
        # Manually compute expected D_value for interpolation points
        if T == 138.5:
            # Between 137°F and 140°F
            expected_log_D = math.log10(82) + (math.log10(35) - math.log10(82)) * (T - 137)/(140 - 137)
            expected_D = 10 ** expected_log_D
        elif T == 142.5:
            # Between 140°F and 145°F
            expected_log_D = math.log10(35) + (math.log10(14) - math.log10(35)) * (T - 140)/(145 - 140)
            expected_D = 10 ** expected_log_D
        elif T == 147.5:
            # Between 145°F and 150°F
            expected_log_D = math.log10(14) + (math.log10(5) - math.log10(14)) * (T - 145)/(150 - 145)
            expected_D = 10 ** expected_log_D
        else:
            expected_D = expected_D_values[test_temperatures.index(T)]
        
        if expected_D is not None and abs(D_value - expected_D) > 0.0001:
            print(f"Test failed for T = {T}°F. Expected D-value: {expected_D} mins, Got: {D_value} mins")
            tests_passed = False
        else:
            print(f"Test passed for T = {T}°F.")

    # Test cases for incremental kill-D calculations
    print("\nTesting incremental kill-D calculations:")
    test_intervals = [
        {'prev_time': 0, 'current_time': 10, 'prev_temp': 140, 'current_temp': 145},
        {'prev_time': 10, 'current_time': 20, 'prev_temp': 145, 'current_temp': 150},
    ]
    cumulative_kill_D = 0.0
    for interval in test_intervals:
        delta_t = interval['current_time'] - interval['prev_time']
        temp_interval = (interval['prev_temp'] + interval['current_temp']) / 2
        D_value = get_D_value(temp_interval)
        incremental_kill_D = delta_t / D_value
        cumulative_kill_D += incremental_kill_D
        print(f"Interval from {interval['prev_time']} to {interval['current_time']} minutes:")
        print(f"Average Temp: {temp_interval}°F, D-value: {D_value:.1f} mins")
        print(f"Incremental kill-D: {incremental_kill_D:.1f}, Cumulative kill-D: {cumulative_kill_D:.1f}\n")

    if tests_passed:
        print("All core computation logic tests passed successfully.\n")
    else:
        print("Some tests failed. Please review the computations.\n")

def main():
    global verbose
    global safe_D
    print("Salmonella Kill-D Factor Calculator")
    
    # Ask to run verification tests
    run_tests_input = input("Do you want to perform temperature-time tests before starting? (y/n): ").strip().lower()
    if run_tests_input == 'y':
        run_tests()

    # Ask whether the user wants more or less detailed output
    detailed_output = input("Do you want detailed output? (y/n): ").strip().lower()
    if detailed_output == 'y':
        verbose = True
    else:
        verbose = False
    
    cumulative_kill_D = 0.0
    
    # Get initial time and temperature
    while True:
        try:
            prev_time = float(input("Enter initial time (in minutes): "))
            break
        except ValueError:
            print("Invalid input. Please enter a numeric value for time (minutes).")
    while True:
        try:
            prev_temp = float(input("Enter initial temperature (in degrees F): "))
            break
        except ValueError:
            print("Invalid input. Please enter a numeric value for temperature.")
    
    print(f"\nStarting at time {prev_time} minutes with temperature {prev_temp}°F.\n")
    
    while True:
        # Get current time and temperature
        current_time_input = input("Enter current time (in minutes), or 'q' to quit: ").strip().lower()
        if current_time_input == 'q':
            print("Exiting the program.")
            break
        try:
            current_time = float(current_time_input)
        except ValueError:
            print("Invalid input. Please enter a numeric value for time or 'q' to quit.")
            continue
        try:
            current_temp = float(input("Enter current temperature (in degrees F): "))
        except ValueError:
            print("Invalid input. Please enter a numeric value for temperature.")
            continue
        
        if current_time <= prev_time:
            print("Error: Current time must be greater than previous time (use cumulative time).")
            continue
        
        # Calculate time interval
        delta_t = current_time - prev_time
        if verbose:
            print(f"\nTime interval: {prev_time} to {current_time} minutes (Δt = {delta_t} minutes)")
        
        # Calculate average temperature during interval
        temp_interval = (prev_temp + current_temp) / 2
        if verbose:
            print(f"Average temperature during interval: ({prev_temp}°F + {current_temp}°F) / 2 = {temp_interval}°F")
        
        # Get D-value at temp_interval
        D_value = get_D_value(temp_interval)
        
        # Calculate incremental kill-D
        incremental_kill_D = delta_t / D_value
        if verbose:
            print(f"Incremental kill-D: Δt / D = {delta_t}mins / {D_value:.1f}mins = {incremental_kill_D:.1f}")
        
        # Update cumulative kill-D
        cumulative_kill_D += incremental_kill_D
        print(f"Updated cumulative kill-D factor: {cumulative_kill_D:.1f}\n")

        # Print whether turkey is safe to eat
        if cumulative_kill_D >= safe_D:
            print(f"The turkey is safe to eat ({cumulative_kill_D:.1f} kill-D).")
        else:
            print(f"The turkey is not safe to eat yet (needs at least {safe_D} kill-D).")
        
        # Print a line break for better readability
        print("--------------------------------------------------\n")
        
        # Update previous time and temperature
        prev_time = current_time
        prev_temp = current_temp

if __name__ == "__main__":
    main()