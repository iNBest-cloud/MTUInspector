import subprocess
import argparse
import platform
import sys


def send_ping(target, size, count, verbose, no_fragment, interface):
    system_type = platform.system()

    if system_type == "Windows":
        cmd = ["ping", "-n", str(count), "-l", str(size), "-w", "1000", target]
        if no_fragment:
            cmd.append("-f")
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
            print(output.decode("utf-8"))
        return True, output.decode("utf-8")
    except subprocess.CalledProcessError as e:
        if verbose:
            print(e.output.decode("utf-8"))
        return False, e.output.decode("utf-8")


def test_interface(interface, target, verbose, no_fragment, start, end, increment):
    successes = []
    failures = []
    current_size = start
    while current_size <= end:
        success_counter = 0
        fail_counter = 0
        while success_counter < 1 and fail_counter < 1:
            success, _ = send_ping(
                target, current_size, 1, verbose, no_fragment, interface
            )
            if success:
                success_counter += 1
            else:
                fail_counter += 1

        if success_counter == 1:
            successes.append(current_size)
        if fail_counter == 1:
            failures.append(current_size)

        current_size += increment

    return successes, failures


def print_results(label, successes, failures, total_sent, total_lost):
    success_percentage = 100 * (total_sent - total_lost) / total_sent
    loss_percentage = 100 * total_lost / total_sent

    print(f"\n{label}:")
    print("Successful pings for sizes:", successes)
    print("Failed pings for sizes:", failures)
    print(f"Total pings sent: {total_sent}")
    print(f"Total pings lost: {total_lost}")
    print(f"Success rate: {success_percentage:.2f}%")
    print(f"Loss rate: {loss_percentage:.2f}%")


def main():
    parser = argparse.ArgumentParser(description="Ping with varying packet sizes.")
    parser.add_argument(
        "--interface",
        required=True,
        help='Interface(s) to use for pinging. For dual interface mode, provide as "int1,int2".',
    )
    parser.add_argument(
        "--target",
        required=True,
        help='Target IP address(es) to ping. For dual interface mode, provide as "ip1,ip2".',
    )
    parser.add_argument("--range", required=True, help="Range of packet sizes.")
    parser.add_argument(
        "--increment", type=int, required=True, help="Increment value for packet size."
    )
    parser.add_argument(
        "--no-fragment", action="store_true", help='Enable "Do Not Fragment" flag.'
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose mode.")

    args = parser.parse_args()

    interfaces = args.interface.split(",")
    targets = args.target.split(",")
    start, end = map(int, args.range.split("-"))

    for interface, target in zip(interfaces, targets):
        successes, failures = test_interface(
            interface,
            target,
            args.verbose,
            args.no_fragment,
            start,
            end,
            args.increment,
        )
        total_sent = len(successes) + len(failures)
        total_lost = len(failures)
        label = f"{interface} ({'DF' if args.no_fragment else 'No DF'})"
        print_results(label, successes, failures, total_sent, total_lost)


if __name__ == "__main__":
    main()
