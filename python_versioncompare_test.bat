#!/bin/bash

# Get Python versions
py37_version=$("C:\py37\python" --version 2>&1)
py38_version=$("C:\py38\python" --version 2>&1)

# Extract only the version numbers (e.g., 3.8.0)
py37_version_number=$(echo $py37_version | awk '{print $2}')
py38_version_number=$(echo $py38_version | awk '{print $2}')

# Compare the versions
if [[ "$py37_version_number" > "$py38_version_number" ]]; then
    printf "Python version in C:\\py37 is greater (%s > %s)\n" "$py37_version_number" "$py38_version_number"
elif [[ "$py37_version_number" < "$py38_version_number" ]]; then
    printf "Python version in C:\\py38 is greater (%s > %s)\n" "$py38_version_number" "$py37_version_number"
else
    printf "Python versions in C:\\py37 and C:\\py38 are the same (%s)\n" "$py37_version_number"
fi