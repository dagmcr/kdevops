#!/bin/bash
# Generate vars

# Create or clear the output file
output_file=$1

# Add the initial "---" to the final file
echo "---" > "$output_file"

# Find all roles and their corresponding defaults/*.yml files
find roles/ -type f -path "*/defaults/*.yml" | while read file; do
    # Extract the role name and file name
    role_name=$(basename "$(dirname "$(dirname "$file")")")
    file_name=$(basename "$file")

    # Append the role name and file name as headers to the output file
    echo "# Role: $role_name" >> "$output_file"
    echo "# File: $file_name" >> "$output_file"
    echo "" >> "$output_file"

    # Append the content of the .yml file, removing any leading "---"
    sed '/^---$/d' "$file" >> "$output_file"
    echo "" >> "$output_file"
done

# Remove any empty lines at the end of the final file
sed -i '${/^$/d;}' "$output_file"

echo "Content appended to $output_file successfully."
