# Simple CSV Sampler

This script calculates the ideal sample size and extracts the appropriate number of random rows from an input CSV file depending on the desired level of confidence, margin of error, and some random seed (with sensible default values). It also writes a log by default that provides evidence that neither the input nor the output files have been tempered with after the sample was taken.

## Usage

To use this script, either use the compiled variant or call upon the Python script via Python3 from your terminal/console of choice.

**Positional Arguments:**

| Argument   | Effect              |
| ---------- | ------------------- |
| input_file | Input CSV file path |

**Options:**

| Option                                                | Effect                                   |
| ----------------------------------------------------- | ---------------------------------------- |
| -h, --help                                            | show this help message and exit          |
| --confidence CONFIDENCE, -c CONFIDENCE                | Confidence level (default: 0.95)         |
| --margin-of-error MARGIN_OF_ERROR, -m MARGIN_OF_ERROR | Margin of error (default: 0.05)          |
| --output OUTPUT, -o OUTPUT                            | Output CSV file path                     |
| --verbose, -v                                         | Verbose mode                             |
| --seed SEED, -s SEED                                  | Random seed                              |
| --language {en,de}, -l {en,de}                        | Language for output text (default: en)   |
| --log-to-shell                                        | Print the log to the shell               |
| --no-log-to-file, -n                                  | Do not print the log to a separate file. |
| --dry-run, -d                                         | Do not write to any files.               |
