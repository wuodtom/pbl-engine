# --- 2. UNIVERSAL DATA SORTER ---
    lines = raw_csv_data.strip().split('\n')
    split_index = None
    
    # We look for the word "Split" anywhere in the file to find the start
    for i, line in enumerate(lines):
        if "Split" in line and "Time" in line:
            split_index = i
            break

    if split_index is not None:
        summary_text = '\n'.join(lines[:split_index])
        splits_text = '\n'.join(lines[split_index:])
        
        # We use 'error_bad_lines' to skip messy rows
        df_summary = pd.read_csv(io.StringIO(summary_text), on_bad_lines='skip')
        df_splits = pd.read_csv(io.StringIO(splits_text), on_bad_lines='skip')
    else:
        # Fallback: if the file is just a simple list of splits
        df_splits = pd.read_csv(io.StringIO(raw_csv_data))
        df_summary = pd.DataFrame() # Empty summary if not found
