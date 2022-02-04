for f in scripts/*.gst; do
  if [[ "$f" == *"$1"*  ]] || [ -z "$1" ]; then
    python terminal.py "$f" || break  # execute successfully or break
    # Or more explicitly: if this execution fails, then stop the `for`:
    # if ! bash "$f"; then break; fi
  fi
done
