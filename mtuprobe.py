import subprocess
import argparse
import platform

def send_ping(target, size, count, verbose, no_fragment, interface):
    system_type = platform.system()

    if system_type == "Windows":
        cmd = ["ping", "-n", str(count), "-l", str(size), "-w", "1000", target]
        if no_fragment:
            cmd.append('-f')
        if interface:  # In Windows, this will be the IP address of the interface.
            cmd.extend(["-S", interface])
    else:  # Assume Unix-like system (e.g., Linux, macOS)
        cmd = ["ping", "-c", str(count), "-s", str(size), "-W", "1", target]
        if no_fragment:
            cmd.extend(["-M", "do"])
        if interface:
            cmd.extend(["-I", interface])

    if verbose:
        print(f"Sending ping to {target} with packet size {size} bytes...")

    try:
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        if verbose:
            print(output.decode('utf-8'))
        return True, output.decode('utf-8')
    except subprocess.CalledProcessError as e:
        if verbose:
            print(e.output.decode('utf-8'))
        return False, e.output.decode('utf-8')

def test_interface(interface, target, verbose):
    results = []
    for no_fragment in [False, True]:
        successes = []
        failures = []

        current_size = 100
        while current_size <= 9100:
            success_counter = 0
            fail_counter = 0
            while success_counter < 1 and fail_counter < 1:
                success, _ = send_ping(target, current_size, 1, verbose, no_fragment, interface)
                if success:
                    success_counter += 1
                else:
                    fail_counter += 1

            if success_counter == 1:
                successes.append(current_size)
            if fail_counter == 1:
                failures.append(current_size)

            current_size += 100

        results.append((no_fragment, successes, failures))
    return results

def main():
    parser = argparse.ArgumentParser(description='Ping with varying packet sizes.')
    parser.add_argument('--dual-interface-test', action='store_true', help='Enable dual interface test mode.')
    parser.add_argument('--interface1', default='', help='First interface for dual test mode.')
    parser.add_argument('--interface2', default='', help='Second interface for dual test mode.')
    parser.add_argument('--target1', default='', help='Target for first interface in dual test mode.')
    parser.add_argument('--target2', default='', help='Target for second interface in dual test mode.')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose mode.')
    parser.add_argument('--target', default='8.8.8.8', help='Target IP address to ping for single interface mode.')
    parser.add_argument('--range', default='100-9100', help='Range of packet sizes for single interface mode.')
    parser.add_argument('--increment', type=int, default=100, help='Increment value for packet size for single interface mode.')
    parser.add_argument('--success-count', type=int, default=1, help='Number of successful pings before moving to next size for single interface mode.')
    parser.add_argument('--fail-count', type=int, default=1, help='Number of failed pings before moving to next size for single interface mode.')
    parser.add_argument('--no-fragment', action='store_true', help='Enable "Do Not Fragment" flag for single interface mode.')
    parser.add_argument('--interface', default='', help='Interface or source IP to use for pinging in single interface mode.')

    args = parser.parse_args()

    if args.dual_interface_test:
        print("\nTesting Interface 1 without DF flag...")
        result1_no_df = test_interface(args.interface1, args.target1, args.verbose)
        print("\nTesting Interface 1 with DF flag...")
        result1_df = test_interface(args.interface1, args.target1, args.verbose)

        print("\nTesting Interface 2 without DF flag...")
        result2_no_df = test_interface(args.interface2, args.target2, args.verbose)
        print("\nTesting Interface 2 with DF flag...")
        result2_df = test_interface(args.interface2, args.target2, args.verbose)

        # Print consolidated results
        print("\nFinal Results:")
        for label, result in [
            ("Interface 1 (No DF)", result1_no_df),
            ("Interface 1 (DF)", result1_df),
            ("Interface 2 (No DF)", result2_no_df),
            ("Interface 2 (DF)", result2_df),
        ]:
            print(f"\n{label}:")
            print("Successful pings:", result[1])
            print("Failed pings:", result[2])
    else:
        start, end = map(int, args.range.split('-'))

        successes = []
        failures = []

        total_sent = 0
        total_lost = 0

        current_size = start
        while current_size <= end:
            success_counter = 0
            fail_counter = 0
            while success_counter < args.success_count and fail_counter < args.fail_count:
                total_sent += 1
                success, _ = send_ping(args.target, current_size, 1, args.verbose, args.no_fragment, args.interface)
                if success:
                    success_counter += 1
                else:
                    fail_counter += 1
                    total_lost += 1

            if success_counter == args.success_count:
                successes.append(current_size)
            if fail_counter == args.fail_count:
                failures.append(current_size)

            current_size += args.increment

        success_percentage = 100 * (total_sent - total_lost) / total_sent
        loss_percentage = 100 * total_lost / total_sent

        print("\nSummary:")
        print("Successful pings for sizes:", successes)
        print("Failed pings for sizes:", failures)
        print(f"Total pings sent: {total_sent}")
        print(f"Total pings lost: {total_lost}")
        print(f"Success rate: {success_percentage:.2f}%")
        print(f"Loss rate: {loss_percentage:.2f}%")

if __name__ == '__main__':
    main()