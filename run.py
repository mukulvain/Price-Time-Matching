import multiprocessing
import subprocess
import sys

dates = []
commands = []
INTERVAL = sys.argv[1]
for date in dates:
    commands.append[f"python3 main.py {date} {INTERVAL}"]


def run_command(cmd):
    """Runs a shell command and prints the output."""
    process_id = multiprocessing.current_process().pid
    print(f"Executing: {cmd} on Process ID {process_id}")

    # Execute the command
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    print(f"Output from Process ID {process_id}: {result.stdout.strip()}")


if __name__ == "__main__":
    num_cores = multiprocessing.cpu_count()

    # Create a pool of workers, each mapped to a different core
    with multiprocessing.Pool(processes=num_cores) as pool:
        pool.map(run_command, commands)  # Distribute commands dynamically

    print("\nAll commands executed.")
