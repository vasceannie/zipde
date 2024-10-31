"""
Contract File Comparison Tool

This script compares two CSV files containing lists of files within contract-related ZIP archives
and generates a side-by-side comparison. It handles different contract number formats
while preserving FG contract distinctions.

Input Files:
    - zip_contents_orig.csv: Original list of files in ZIP archives
    - zip_contents_staged.csv: New/staged list of files in ZIP archives

Output:
    - zip_contents_diff_YYYYMMDD_HHMMSS.csv: CSV file containing side-by-side comparison
    - zip_contents_duplicates_YYYYMMDD_HHMMSS.csv: CSV file containing duplicate file occurrences
    
CSV Format:
    Input files should have columns: Level, Name, Type
    Output diff file has columns: Contract, Original_Files, Staged_Files, Status
    Output duplicates file has columns: Filename, Contracts

Contract Number Formats Handled:
    - Standard: /OL_12489/ -> OL_12489
    - FG Format: /OL_FG_0000000000000000003479/ -> OL_FG_0000000000000000003479
    FG contracts preserve all leading zeros

Author: [Your Name]
Date: [Current Date]
Version: 1.4
"""

import csv
import re
from collections import defaultdict
from datetime import datetime

def extract_contract_number(path):
    """
    Extract contract numbers from file paths, preserving FG distinction and leading zeros.
    
    Args:
        path (str): File path containing contract number
        
    Returns:
        str or None: Contract number with appropriate prefix,
                    or None if no contract number is found
    
    Examples:
        >>> extract_contract_number('/OL_12489/OL_12489_LA.zip')
        'OL_12489'
        >>> extract_contract_number('/OL_FG_0000000000000000003479/file.zip')
        'OL_FG_0000000000000000003479'
    """
    # Check for FG format first - preserve all zeros
    fg_match = re.search(r'/OL_FG_(\d+)', path)
    if fg_match:
        return f'OL_FG_{fg_match.group(1)}'
    
    # Check for standard format
    std_match = re.search(r'/OL_(\d+)', path)
    if std_match:
        return f'OL_{std_match.group(1)}'
    
    return None

def build_contract_files_map(csv_filename):
    """
    Build a mapping of contract numbers to their associated files.
    
    Attempts to read the CSV file with multiple encodings to handle different
    file encodings that might be encountered.
    
    Args:
        csv_filename (str): Path to the CSV file to process
        
    Returns:
        defaultdict: Dictionary mapping contract numbers to sets of file paths
        
    Raises:
        ValueError: If the file cannot be read with any of the attempted encodings
    """
    contract_files = defaultdict(set)
    # List of encodings to try, in order of preference
    encodings = ['utf-8', 'cp1252', 'iso-8859-1']
    
    for encoding in encodings:
        try:
            with open(csv_filename, newline='', encoding=encoding) as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  # Skip header row
                
                # Process each row in the CSV
                for row in reader:
                    level, name, file_type = row
                    contract_number = extract_contract_number(name)
                    if contract_number:
                        contract_files[contract_number].add(name)
            
            return contract_files  # Return on successful processing
        except UnicodeDecodeError:
            continue  # Try next encoding if current one fails
    
    # If we get here, none of the encodings worked
    raise ValueError(f"Could not read {csv_filename} with any of the attempted encodings")

def get_file_status(orig_files, staged_files):
    """
    Determine the status of files between original and staged versions.
    
    Args:
        orig_files (set): Set of files in original version
        staged_files (set): Set of files in staged version
        
    Returns:
        str: Status indicating if files were added, removed, or unchanged
    """
    if orig_files == staged_files:
        return "UNCHANGED"
    elif not orig_files:
        return "ADDED"
    elif not staged_files:
        return "REMOVED"
    else:
        return "MODIFIED"

def find_duplicate_files(contract_files_map):
    """
    Find files that appear in multiple contracts.
    
    Args:
        contract_files_map (defaultdict): Dictionary mapping contract numbers to sets of file paths
        
    Returns:
        dict: Dictionary mapping filenames to lists of contracts containing them
    """
    file_locations = defaultdict(set)
    
    # Build mapping of files to the contracts they appear in
    for contract, files in contract_files_map.items():
        for filepath in files:
            # Extract just the filename from the path
            filename = filepath.split('/')[-1]
            file_locations[filename].add(contract)
    
    # Filter to only files that appear in multiple contracts
    return {filename: contracts for filename, contracts in file_locations.items() 
            if len(contracts) > 1}

def write_duplicate_report(timestamp, orig_files_map, staged_files_map):
    """
    Write report of duplicate files found in either original or staged files.
    
    Args:
        timestamp (str): Timestamp string for filename
        orig_files_map (defaultdict): Mapping of contracts to files in original CSV
        staged_files_map (defaultdict): Mapping of contracts to files in staged CSV
    """
    output_filename = f'zip_contents_duplicates_{timestamp}.csv'
    
    # Find duplicates in both original and staged files
    orig_duplicates = find_duplicate_files(orig_files_map)
    staged_duplicates = find_duplicate_files(staged_files_map)
    
    # Combine all filenames that are duplicated in either version
    all_duplicate_files = sorted(set(orig_duplicates.keys()) | set(staged_duplicates.keys()))
    
    with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Filename', 'Original_Contracts', 'Staged_Contracts'])
        
        for filename in all_duplicate_files:
            orig_contracts = sorted(orig_duplicates.get(filename, set()))
            staged_contracts = sorted(staged_duplicates.get(filename, set()))
            
            writer.writerow([
                filename,
                '; '.join(orig_contracts) if orig_contracts else 'Not Present',
                '; '.join(staged_contracts) if staged_contracts else 'Not Present'
            ])
    
    print(f"Duplicate file report has been written to {output_filename}")

def main():
    """
    Main function to orchestrate the comparison process.
    
    Workflow:
    1. Build file mappings from both input CSVs
    2. Create timestamped output files
    3. Compare files for each contract
    4. Write side-by-side comparison to output CSV
    5. Generate and write duplicate files report
    """
    # Load file mappings from both CSV files
    orig_files_map = build_contract_files_map('zip_contents_orig.csv')
    staged_files_map = build_contract_files_map('zip_contents_staged.csv')

    # Generate timestamp for output files
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Write the main comparison results
    output_filename = f'zip_contents_diff_{timestamp}.csv'
    
    with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Contract', 'Original_Files', 'Staged_Files', 'Status'])

        for contract_number in sorted(set(orig_files_map.keys()) | set(staged_files_map.keys())):
            orig_files = orig_files_map.get(contract_number, set())
            staged_files = staged_files_map.get(contract_number, set())
            status = get_file_status(orig_files, staged_files)

            orig_files_list = sorted(orig_files)
            staged_files_list = sorted(staged_files)

            max_length = max(len(orig_files_list), len(staged_files_list))
            orig_files_list.extend([''] * (max_length - len(orig_files_list)))
            staged_files_list.extend([''] * (max_length - len(staged_files_list)))

            writer.writerow([contract_number,
                           orig_files_list[0] if orig_files_list else '',
                           staged_files_list[0] if staged_files_list else '',
                           status])

            for i in range(1, max_length):
                writer.writerow(['',
                               orig_files_list[i] if i < len(orig_files_list) else '',
                               staged_files_list[i] if i < len(staged_files_list) else '',
                               ''])

            writer.writerow(['', '', '', ''])

    print(f"Side-by-side comparison has been written to {output_filename}")
    
    # Generate and write the duplicate files report
    write_duplicate_report(timestamp, orig_files_map, staged_files_map)

if __name__ == "__main__":
    main()
