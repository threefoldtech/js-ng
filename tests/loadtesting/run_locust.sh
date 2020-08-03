#!/bin/bash
helpFunction() {
    echo ""
    echo "Usage: $0 -u user_number -r hatch_rate -h host"
    echo -e "\t-u Number of concurrent Locust users"
    echo -e "\t-r The rate per second in which users are spawned"
    echo -e "\t-h Host to load test"
    exit 1 # Exit script after printing help
}

while getopts "u:r:h:" opt; do
    case "$opt" in
    u) user_number="$OPTARG" ;;
    r) hatch_rate="$OPTARG" ;;
    h) host="$OPTARG" ;;
    ?) helpFunction ;; # Print helpFunction in case parameter is non-existent
    esac
done

# Print helpFunction in case parameters are empty
if [ -z "$user_number" ] || [ -z "$hatch_rate" ] || [ -z "$host" ]; then
    echo "Some or all of the parameters are empty"
    helpFunction
fi

# Begin script in case all parameters are correct
echo "$user_number"
echo "$hatch_rate"
echo "$host"

locust --headless -u $user_number -r $hatch_rate --host $host -f /home/rafy/sandbox/code/github/threefoldtech/js-ng/tests/loadtesting/admin.py
