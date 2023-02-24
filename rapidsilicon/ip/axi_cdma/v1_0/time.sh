#!/bin/bash

# Function to log the time
log_time() {
    echo "$(date +%T.%N): $1"
}

# Initialize the total time variable
total_time=0

# Process 1
log_time "Starting process 1"
start_time=$(date +%s.%N)
# Run the command for process 1
python3 axi_cdma_gen.py --json-template
end_time=$(date +%s.%N)
process_time=$(echo "$end_time - $start_time" | bc)
log_time "Process 1 took $process_time seconds to complete"
total_time=$(echo "$total_time + $process_time" | bc)

# Process 2
log_time "Starting process 2"
start_time=$(date +%s.%N)
# Run the command for process 2
python3 axi_cdma_gen.py --json feedback1.json --json-template

end_time=$(date +%s.%N)
process_time=$(echo "$end_time - $start_time" | bc)
log_time "Process 2 took $process_time seconds to complete"
total_time=$(echo "$total_time + $process_time" | bc)

# Process 3
log_time "Starting process 3"
start_time=$(date +%s.%N)
# Run the command for process 3
python3 axi_cdma_gen.py --json feedback2.json --json-template
end_time=$(date +%s.%N)
process_time=$(echo "$end_time - $start_time" | bc)
log_time "Process 3 took $process_time seconds to complete"
total_time=$(echo "$total_time + $process_time" | bc)

# Process 4
log_time "Starting process 4"
start_time=$(date +%s.%N)
# Run the command for process 4
python3 axi_cdma_gen.py --json feedback3.json --json-template
end_time=$(date +%s.%N)
process_time=$(echo "$end_time - $start_time" | bc)
log_time "Process 4 took $process_time seconds to complete"
total_time=$(echo "$total_time + $process_time" | bc)

# Log the total time taken
log_time "Total time taken: $total_time seconds"
