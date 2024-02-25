# Dependencies
import argparse  # For parsing command-line arguments
from colorama import Fore, Back, Style, just_fix_windows_console  # For terminal colors
import csv  # For CSV file operations
import hashlib # For calculating hash sums
import math  # For mathematical operations
import os  # For operating system related operations
import platform  # For platform information
import random  # For random number generation
import scipy.stats as stats  # For statistical operations
import sys  # For system-related operations
import time  # For time-related operations

# Function to set localization based on language
def set_localization(language):
    # German language
    if language == 'de':
        return {
            'SAMPLE_SIZE': "Berechnete Stichprobengröße:",
            'EXPORTED_ROWS': "Anzahl exportierter Zeilen:",
            'SEED': "Seed:",
            'OUTPUT_FILE': "Name der Output-Datei:",
            'FILE_EXISTS': Fore.YELLOW+"Datei '{file}' existiert bereits. Möchten Sie sie überschreiben? (j/N): "+Style.RESET_ALL,
            'OPERATION_CANCELLED': Fore.RED+"Vorgang abgebrochen."+Style.RESET_ALL,
            'EXIT': "Beende Programm...",
            'YES': "j",
            'CONFIDENCE_LEVEL': "Konfidenzniveau:",
            'MARGIN_OF_ERROR': "Fehlermarge:",
            'INPUT_FILE': "Name der Input-Datei:",
            'SUCCESS': Fore.GREEN+"OK!"+Style.RESET_ALL,
            'FAILURE': Fore.RED+"FEHLER!"+Style.RESET_ALL,
            'WARNING': Fore.YELLOW+"WARNUNG!"+Style.RESET_ALL,
            'SEED_SELECTION': "Bestimme Seed für zufällige Auswahl...",
            'NOT_CSV': Fore.RED+"[Datei nicht gefunden oder keine valide CSV-Datei]"+Style.RESET_ALL,
            'READ_INPUT': "Lese Input-Datei '{file}'...",
            'SAMPLE_SIZE_CALC': "Berechne Stichprobenumfang...",
            'SELECT_ROWS': "Wähle zufällige Zeilen aus...",
            'READ_FROM_SYSTEM_TIME': "aus Systemzeit gelesen",
            'READ_FROM_USER_INPUT': "aus Nutzer-Input gelesen",
            'WRITE_OUTPUT': "Schreibe zur Output-Datei '{output}'...",
            'OVERWRITE_OUTPUT': "Überschreibe Output-Datei '{output}'...",
            'WRITE_LOG': "Schreibe Log-Datei...",
            'OUT_OF_BOUNDS': Fore.RED+"'Konfidenzniveau' und 'Fehlermarge' müssen beide Werte zwischen 0 and 1 haben (exkl. 0 und 1)!"+Style.RESET_ALL,
            'OUTPUT_SHA': "SHA-256-Prüfsumme der Output-Datei:",
            'INPUT_SHA': "SHA-256-Prüfsumme der Input-Datei:",
            'TOTAL_POPULATION': "Grundgesamtheit:",
            'DRY_RUN_SHA': "Keine SHA-256-Prüfsummen der Output-Datei in Probeläufe!"
        }
    # English language (default)
    else:
        return {
            'SAMPLE_SIZE': "Calculated Sample Size:",
            'EXPORTED_ROWS': "Number of Exported Rows:",
            'SEED': "Seed:",
            'OUTPUT_FILE': "Name of the Output File:",
            'FILE_EXISTS': Fore.YELLOW+"File '{file}' already exists. Do you want to overwrite it? (y/N): "+Style.RESET_ALL,
            'OPERATION_CANCELLED': Fore.RED+"Operation cancelled."+Style.RESET_ALL,
            'EXIT': "Exiting program...",
            'YES': "y",
            'CONFIDENCE_LEVEL': "Confidence Level:",
            'MARGIN_OF_ERROR': "Margin of Error:",
            'INPUT_FILE': "Name of the Input File:",
            'SUCCESS': Fore.GREEN+"OK!"+Style.RESET_ALL,
            'FAILURE': Fore.RED+"ERROR!"+Style.RESET_ALL,
            'WARNING': Fore.YELLOW+"WARNING!"+Style.RESET_ALL,
            'SEED_SELECTION': "Setting seed for random selection...",
            'NOT_CSV': Fore.RED+"[file not found or not a valid CSV file]"+Style.RESET_ALL,
            'READ_INPUT': "Reading input file '{file}'...",
            'SAMPLE_SIZE_CALC': "Calculating sample size...",
            'SELECT_ROWS': "Selecting random rows...",
            'READ_FROM_SYSTEM_TIME': "read from system time",
            'READ_FROM_USER_INPUT': "read from user input",
            'WRITE_OUTPUT': "Writing to output file '{output}'...",
            'OVERWRITE_OUTPUT': "Overwriting output file '{output}'...",
            'WRITE_LOG': "Writing log file...",
            'OUT_OF_BOUNDS': Fore.RED+"'Confidence Level' and 'Margin of Error' must both have values between 0 and 1 (excl. 0 and 1)!"+Style.RESET_ALL,
            'OUTPUT_SHA': "SHA-256 Checksum of the Output File:",
            'INPUT_SHA': "SHA-256 Checksum of the Input File:",
            'TOTAL_POPULATION': "Total Population:",
            'DRY_RUN_SHA': "No SHA-256 checksum of the Output File in Dry Runs!"
        }

def calculate_sha256(file_path):
    # Initialize the SHA-256 hash object
    sha256 = hashlib.sha256()

    try:
        # Open the file in binary mode
        with open(file_path, 'rb') as file:
            # Read the file chunk by chunk to handle large files
            for chunk in iter(lambda: file.read(4096), b''):
                # Update the hash object with the current chunk
                sha256.update(chunk)

        # Get the hexadecimal digest of the hash
        sha256_checksum = sha256.hexdigest()

        return sha256_checksum

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        exit(1)
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

# Function to calculate the sample size
def calculate_sample_size(total_population, confidence_level=0.95, margin_of_error=0.05):
    z = stats.norm.ppf(1 - (1 - confidence_level) / 2)
    p = 0.5  # Assuming maximum variance which gives maximum sample size
    q = 1 - p
    e = margin_of_error

    n_0 = ((z ** 2) * p * q) / (e ** 2)

    # Adjustment for finite population
    n = n_0 / (1 + ((n_0 - 1) / total_population))

    # Round up using the ceiling function
    n = math.ceil(n)

    return int(n)

# Main function to execute the sampling process
def main(input_file, confidence_level=0.95, margin_of_error=0.05, output=None, verbose=False, seed=None, language='en', log_to_shell=False, no_log_to_file=False, dry_run=False):
    # Set localization
    localization = set_localization(language)

    # Check if confidence and margin of error are not equal to 0 or 1
    if confidence_level <= 0 or confidence_level >= 1 or margin_of_error <= 0 or margin_of_error >= 1:
        print(f"{localization['FAILURE']} {localization['OUT_OF_BOUNDS']}")
        print(f"{localization['OPERATION_CANCELLED']}")
        sys.exit(1)

    # Get file name without file extension
    input_file_no_ext = os.path.splitext(os.path.basename(input_file))[0]

    # Set output file name if user didn't specify anything
    if output is None:
        output = f"{input_file_no_ext}_sampled.csv"

    # Get string lengths for alignment with dots
    if verbose:
        alignment_length = max(
        len(str(localization['READ_INPUT'].format(file=input_file))),
        len(str(localization['SEED_SELECTION'])),
        len(str(localization['SAMPLE_SIZE_CALC'])),
        len(str(localization['WRITE_OUTPUT'].format(output=output))),
        len(str(localization['OVERWRITE_OUTPUT'].format(output=output))),
        len(str(localization['SELECT_ROWS'])),
        len(str(localization['WRITE_LOG']))
        )

    # Read CSV input file
    if verbose:
        print(f"{localization['READ_INPUT'].format(file=input_file)}"+"."*(alignment_length-len(localization['READ_INPUT'].format(file=input_file))),end="")

    try:
        with open(input_file, 'r') as file:
            reader = csv.reader(file)
            headers = next(reader)
            data = list(reader)
            total_population = len(data)
    except:
        print(f"{localization['FAILURE']} {localization['NOT_CSV']}")
        print(f"{localization['OPERATION_CANCELLED']}")
        sys.exit(1)

    if verbose:
        print(f"{localization['SUCCESS']}")
    
    if not(no_log_to_file) or log_to_shell:
        input_hash = calculate_sha256(input_file)

    # Set the random seed
    if verbose:
        print(f"{localization['SEED_SELECTION']}"+"."*(alignment_length-len(localization['SEED_SELECTION'])),end="")
    # Take system time in nanoseconds for seed if user didn't specify anything
    if seed is None:
        random_seed = int(time.time_ns())
        if verbose:
            print(f"{localization['SUCCESS']} [{localization['READ_FROM_SYSTEM_TIME']}; seed = {random_seed}]")
    # Take user input for seed if user specified the seed to be used
    else:
        random_seed = seed
        if verbose:
            print(f"{localization['SUCCESS']} [{localization['READ_FROM_USER_INPUT']}, seed = {random_seed}]")
    random.seed(random_seed)
    
    # Calculate the recommended sample size
    if verbose:
        print(f"{localization['SAMPLE_SIZE_CALC']}"+"."*(alignment_length-len(localization['SAMPLE_SIZE_CALC'])),end="")

    sample_size = calculate_sample_size(total_population, confidence_level, margin_of_error)

    if verbose:
        print(f"{localization['SUCCESS']} [sample size = {sample_size}]")

    # Select the appropriate number of random rows
    if verbose:
        print(f"{localization['SELECT_ROWS']}"+"."*(alignment_length-len(localization['SELECT_ROWS'].format(file=input_file))),end="")

    sampled_rows = random.sample(data, sample_size)

    if verbose:
        print(f"{localization['SUCCESS']}")

    # Write the randomly chosen rows to a new file
    if verbose:
        print(f"{localization['WRITE_OUTPUT'].format(output=output)}"+"."*(alignment_length-len(localization['WRITE_OUTPUT'].format(output=output))),end="")

    # Check if the output file already exists, and ask for overwriting confirmation if it does
    if os.path.exists(output):
        if verbose:
            print(f"{localization['WARNING']}")
        overwrite = input(localization['FILE_EXISTS'].format(file=output)).strip().lower()
        if overwrite != localization['YES']:
            print(f"{localization['OPERATION_CANCELLED']}")
            sys.exit(1)
        if overwrite == localization['YES']:
            if verbose:
                print(f"{localization['OVERWRITE_OUTPUT'].format(output=output)}"+"."*(alignment_length-len(localization['OVERWRITE_OUTPUT'].format(output=output))),end="")

    ## Writing the actual output file itself
    if not(dry_run):
        with open(output, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            writer.writerows(sampled_rows)

    if verbose:
        print(f"{localization['SUCCESS']}")

    if not dry_run:
        if not(no_log_to_file) or log_to_shell:
            output_hash = calculate_sha256(output)
    else:
        if not(no_log_to_file) or log_to_shell:
            output_hash = f"{localization['DRY_RUN_SHA']}"

    if not(no_log_to_file) or log_to_shell:
        max_label_length = max(len(localization['SAMPLE_SIZE']), len(localization['EXPORTED_ROWS']), len(localization['SEED']), len(localization['OUTPUT_FILE']), len(localization['CONFIDENCE_LEVEL']), len(localization['MARGIN_OF_ERROR']), len(localization['INPUT_FILE']), len(localization['INPUT_SHA']), len(localization['OUTPUT_SHA']), len(localization['TOTAL_POPULATION']))
        max_value_length = max(len(f"{input_file}"),len(f"{confidence_level}"),len(f"{margin_of_error}"),len(f"{random_seed}"),len(f"{sample_size}"),len(f"{len(sampled_rows)}"),len(f"{confidence_level}"),len(f"{output}"),len(f"{output_hash}"),len(f"{input_hash}"),len(f"{total_population}"))
    
    # Log
    ## Write log to file if not specified otherwise
    if not no_log_to_file:
        if verbose:
            print(f"{localization['WRITE_LOG']}"+"."*(alignment_length-len(localization['WRITE_LOG'])),end="")
        log_file_path = f"{output}.log"
        if not dry_run:
            with open(log_file_path, 'a') as log_file:
                sys.stdout = log_file
                print(f"{localization['INPUT_FILE']: <{max_label_length + 2}} {input_file}")
                print(f"{localization['INPUT_SHA']: <{max_label_length + 2}} {input_hash}")
                print(f"{localization['TOTAL_POPULATION']: <{max_label_length + 2}} {total_population}")
                print(f"{localization['SEED']: <{max_label_length + 2}} {random_seed}")
                print(f"{localization['CONFIDENCE_LEVEL']: <{max_label_length + 2}} {confidence_level}")
                print(f"{localization['MARGIN_OF_ERROR']: <{max_label_length + 2}} {margin_of_error}")
                print(f"{localization['SAMPLE_SIZE']: <{max_label_length + 2}} {sample_size}")
                print(f"{localization['OUTPUT_FILE']: <{max_label_length + 2}} {output}")
                print(f"{localization['OUTPUT_SHA']: <{max_label_length + 2}} {output_hash}")
                print(f"{localization['EXPORTED_ROWS']: <{max_label_length + 2}} {len(sampled_rows)}")
            sys.stdout = sys.__stdout__
        if verbose:
            print(f"{localization['SUCCESS']}")

    ## Print results in console only if specified
    if log_to_shell:
        total_length = max_label_length + 3 + max_value_length
        if total_length % 2 == 0:
            log_line_top="-"*(int((max_label_length+3+max_value_length)/2)-1)+"LOG"+"-"*(int((max_label_length+3+max_value_length)/2)-2)
        else:
            log_line_top="-"*(int((max_label_length+3+max_value_length)/2)-1)+"LOG"+"-"*(int((max_label_length+3+max_value_length)/2)-1)
        log_line_bottom="-"*int((max_label_length+3+max_value_length))
        print(f"{log_line_top}")
        print(f"{localization['INPUT_FILE']: <{max_label_length + 2}} {input_file}")
        print(f"{localization['INPUT_SHA']: <{max_label_length + 2}} {input_hash}")
        print(f"{localization['TOTAL_POPULATION']: <{max_label_length + 2}} {total_population}")
        print(f"{localization['SEED']: <{max_label_length + 2}} {random_seed}")
        print(f"{localization['CONFIDENCE_LEVEL']: <{max_label_length + 2}} {confidence_level}")
        print(f"{localization['MARGIN_OF_ERROR']: <{max_label_length + 2}} {margin_of_error}")
        print(f"{localization['SAMPLE_SIZE']: <{max_label_length + 2}} {sample_size}")
        print(f"{localization['OUTPUT_FILE']: <{max_label_length + 2}} {output}")
        print(f"{localization['OUTPUT_SHA']: <{max_label_length + 2}} {output_hash}")
        print(f"{localization['EXPORTED_ROWS']: <{max_label_length + 2}} {len(sampled_rows)}")
        print(f"{log_line_bottom}")

    # Exit program
    if verbose:
        print(f"{localization['EXIT']}")
    sys.exit(0)

# Start program
if __name__ == "__main__":
    # Check if Windows colour fix is required
    if platform.system()=='Windows':
        just_fix_windows_console()

    # Parse user input
    parser = argparse.ArgumentParser(prog="simple-csv-sampler",description="This program calculates the ideal sample size and extracts the appropriate number of random rows from an input CSV file depending on the desired level of confidence, margin of error, and some random seed (with sensible default values). It also writes a log by default that provides evidence that neither the input nor the output files have been tempered with after the sample was taken.",epilog="Written by Dr. David Krassnig")
    parser.add_argument("input_file", help="Input CSV file path")
    parser.add_argument("--confidence", "-c", type=float, default=0.95, help="Confidence level (default: 0.95)")
    parser.add_argument("--margin-of-error", "-m", type=float, default=0.05, help="Margin of error (default: 0.05)")
    parser.add_argument("--output", "-o", help="Output CSV file path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose mode")
    parser.add_argument("--seed", "-s", type=int, help="Random seed")
    parser.add_argument("--language", "-l", choices=['en', 'de'], default='en', help="Language for output text (default: en)")
    parser.add_argument("--log-to-shell", action="store_true", help="Print the log to the shell")
    parser.add_argument("--no-log-to-file", "-n", action="store_true", help="Do not print the log to a separate file.")
    parser.add_argument("--dry-run", "-d", action="store_true", help="Do not write to any files.")
    args = parser.parse_args()

    # Pass user input to main function
    main(args.input_file, args.confidence, args.margin_of_error, args.output, args.verbose, args.seed, args.language, args.log_to_shell, args.no_log_to_file, args.dry_run)
