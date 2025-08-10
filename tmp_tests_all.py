import subprocess
import re
import sys

# List of test files; you can adjust the order here
tests_list = [
    'test_ssd_write.py',
    'test_ssd_erase.py',
    'test_ssd.py',
    'test_shell_mock.py',
    'test_shell.py',
    'test_read.py',
    'test_logger.py',
    'test_buffer.py',
    'test_cmd_buffer_ignore_cmd.py',
    'test_fast_read.py',
    'test_buffer_fastread.py',
]

summary_lines = []

for test_file in tests_list:
    # Run pytest with explicit UTF-8 encoding to fix Windows cp949 issues
    result = subprocess.run([sys.executable, '-m', 'pytest', "tests/" + test_file], capture_output=True,
                            encoding='utf-8')
    # Safely handle potential None in stdout/stderr
    output = (result.stdout or '') + (result.stderr or '')

    # Print the intermediate output as is
    print(output)

    # Parse the summary more flexibly (from previous fix)
    failed_match = re.search(r'(\d+) failed', output)
    passed_match = re.search(r'(\d+) passed', output)
    skipped_match = re.search(r'(\d+) skipped', output)

    failed = int(failed_match.group(1)) if failed_match else 0
    passed = int(passed_match.group(1)) if passed_match else 0
    skipped = int(skipped_match.group(1)) if skipped_match else 0
    total = failed + passed + skipped

    if total > 0:
        summary_line = f"{test_file} - {failed} failed, {passed} passed, {skipped} skipped in total {total} test cases"
    else:
        summary_line = f"{test_file} - No summary found (check for errors)"

    summary_lines.append(summary_line)

# Print the final summary at the end
print("<Test Summary>")
for line in summary_lines:
    print(line)