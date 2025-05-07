#!/bin/bash

# Bash script to fix whitespace and end-of-file issues

echo "Fixing trailing whitespace and end-of-file issues..."

# Find all text files in the repository
find . -type f \
  -not -path "*/\.*/" \
  -not -path "*/venv/*" \
  -not -path "*/node_modules/*" \
  -not -path "*/dist/*" \
  -not -path "*/build/*" \
  -regex ".*\.\(md\|yaml\|yml\|json\|sh\|py\|go\|js\|jsx\|ts\|tsx\|css\|scss\|html\|htm\|xml\|txt\|conf\|cfg\|ini\|toml\|sql\)$" \
  -print0 |
while IFS= read -r -d '' file; do
  echo "Processing $file"

  # Create a temporary file
  temp_file=$(mktemp)

  # Fix trailing whitespace
  sed 's/[[:space:]]*$//' "$file" > "$temp_file"

  # Ensure there's exactly one newline at the end of the file
  if [ -s "$temp_file" ]; then
    # Ensure file ends with a newline
    if [ "$(tail -c1 "$temp_file" | wc -l)" -eq 0 ]; then
      echo "" >> "$temp_file"
    fi
  fi

  # Remove any blank lines at the end except for the last one
  sed -i -e :a -e '/^\n*$/{$!N;ba' -e '}' "$temp_file"

  # Move the temp file back to the original
  mv "$temp_file" "$file"
done

echo "All files fixed!"
