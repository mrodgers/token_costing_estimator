import argparse
import csv
import json
import logging
from datetime import datetime
from typing import Union, Optional, Dict, Any

# Import configuration management
try:
    from config import load_config, ConfigurationError
except ImportError:
    # Fallback if config module is not available
    def load_config():
        return {
            "default_prompts_per_shift": 50,
            "default_multiplier": 5,
            "default_avg_tokens_per_call": 2000,
            "default_token_cost_per_thousand": 0.06,
            "default_doctors_per_shift": 10,
            "default_shifts_per_day": 3
        }
    
    class ConfigurationError(Exception):
        pass

class OpenAICostCalculator:
    """
    A class to calculate the cost of using OpenAI's API for an application.
    
    Attributes:
        prompts_per_shift (float): The number of prompts sent per doctor's shift.
        multiplier (float): The multiplier for chain interactions or augmentations.
        avg_tokens_per_call (float): Average tokens used per API call.
        token_cost_per_thousand (float): Cost of OpenAI API per 1000 tokens.
    """

    def __init__(self, prompts_per_shift: Union[int, float], multiplier: Union[int, float], 
                 avg_tokens_per_call: Union[int, float], token_cost_per_thousand: Union[int, float]) -> None:
        # Validates the input parameters.
        self.validate_inputs(prompts_per_shift, multiplier, avg_tokens_per_call, token_cost_per_thousand)
        self.prompts_per_shift = prompts_per_shift
        self.multiplier = multiplier
        self.avg_tokens_per_call = avg_tokens_per_call
        self.token_cost_per_thousand = token_cost_per_thousand

    @staticmethod
    def validate_inputs(prompts_per_shift: Union[int, float], multiplier: Union[int, float], 
                       avg_tokens_per_call: Union[int, float], token_cost_per_thousand: Union[int, float]) -> None:
        # Ensures all input parameters are positive numbers.
        if not all(isinstance(arg, (int, float)) and arg > 0 for arg in [prompts_per_shift, multiplier, avg_tokens_per_call, token_cost_per_thousand]):
            raise ValueError("All parameters should be positive numbers.")

    def calculate_tokens_per_shift(self) -> float:
        # Calculates the total number of tokens used per shift.
        return self.prompts_per_shift * self.multiplier * self.avg_tokens_per_call

    def calculate_cost_per_shift(self) -> float:
        # Calculates the total cost per shift based on the number of tokens used.
        tokens_per_shift = self.calculate_tokens_per_shift()
        return (tokens_per_shift / 1000) * self.token_cost_per_thousand

    def calculate_cost_per_hospital_per_shift(self, doctors_per_shift: Union[int, float]) -> float:
        # Calculates the total cost per hospital per shift.
        return self.calculate_cost_per_shift() * doctors_per_shift

    def calculate_daily_costs(self, shifts_per_day: Union[int, float], doctors_per_shift: Union[int, float]) -> float:
        # Calculates the daily costs of OpenAI API calls for a hospital.
        return self.calculate_cost_per_hospital_per_shift(doctors_per_shift) * shifts_per_day

    def calculate_monthly_costs(self, daily_costs: Union[int, float]) -> float:
        days_per_month = 30  # Average number of days in a month
        return daily_costs * days_per_month

    def calculate_annual_costs(self, monthly_costs: Union[int, float]) -> float:
        months_per_year = 12  # Number of months in a year
        return monthly_costs * months_per_year

def parse_arguments() -> Optional[argparse.Namespace]:
    """
    Parse command-line arguments for the token costing calculator.
    
    Returns:
        argparse.Namespace or None: Parsed arguments if provided, None if no arguments given
    """
    parser = argparse.ArgumentParser(
        description="Calculate OpenAI API costs for healthcare applications",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python token_calc.py --prompts 50 --multiplier 5 --tokens 2000 --cost 0.06 --doctors 10 --shifts 3
  python token_calc.py --prompts 100 --cost 0.03
  python token_calc.py  # Interactive mode (default)
        """
    )
    
    parser.add_argument(
        '--prompts', 
        type=float, 
        help='Number of prompts sent per doctor\'s shift (default: 50)'
    )
    parser.add_argument(
        '--multiplier', 
        type=float, 
        help='Chain/interaction/augmentation multiplier (default: 5)'
    )
    parser.add_argument(
        '--tokens', 
        type=float, 
        help='Average tokens used per API call (default: 2000)'
    )
    parser.add_argument(
        '--cost', 
        type=float, 
        help='OpenAI price per 1000 tokens in USD (default: 0.06)'
    )
    parser.add_argument(
        '--doctors', 
        type=float, 
        help='Number of doctors on shift per hospital (default: 10)'
    )
    parser.add_argument(
        '--shifts', 
        type=float, 
        help='Number of shifts per day (default: 3)'
    )
    parser.add_argument(
        '--version', 
        action='version', 
        version='Token Costing Estimator 1.0'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Check if any arguments were provided
    if any(vars(args).values()):
        # Validate that all provided arguments are positive
        for arg_name, arg_value in vars(args).items():
            if arg_value is not None and arg_value <= 0:
                parser.error(f"--{arg_name} must be a positive number, got {arg_value}")
        return args
    else:
        # No arguments provided, return None to indicate interactive mode
        return None

def print_pricing():
    """Displays current OpenAI pricing information to help users understand cost structure."""
    print("\n" + "="*60)
    print("CURRENT OPENAI PRICING REFERENCE (as of 2024)")
    print("="*60)
    print("GPT-4 Models:")
    print("  • GPT-4 (8K context):     $0.03/1K input tokens, $0.06/1K output tokens")
    print("  • GPT-4 (32K context):    $0.06/1K input tokens, $0.12/1K output tokens")
    print("  • GPT-4 Turbo:            $0.01/1K input tokens, $0.03/1K output tokens")
    print("\nGPT-3.5 Models:")
    print("  • GPT-3.5 Turbo:          $0.0015/1K input tokens, $0.002/1K output tokens")
    print("\nNote: Prices may vary. Check https://openai.com/pricing for latest rates.")
    print("      This calculator uses a simplified single rate per 1K tokens.")
    print("="*60 + "\n")

def get_input(prompt: str, default_value: Union[str, int, float]) -> Union[str, int, float]:
    """Captures user input or uses default value if no input is provided.
    
    Handles EOF exceptions and keyboard interrupts gracefully.
    
    Args:
        prompt (str): The prompt message to display to the user
        default_value: The default value to use if no input is provided
        
    Returns:
        The user input or default value
        
    Raises:
        KeyboardInterrupt: Re-raised to allow caller to handle graceful shutdown
        EOFError: Re-raised to allow caller to handle EOF conditions
    """
    try:
        user_input = input(f"{prompt} [{default_value}]: ")
        return user_input.strip() if user_input.strip() else default_value
    except EOFError:
        print(f"\nEOF detected. Using default value: {default_value}")
        return default_value
    except KeyboardInterrupt:
        print(f"\n\nOperation cancelled by user. Using default value: {default_value}")
        return default_value

def display_results(cost_per_shift: float, cost_per_hospital_per_shift: float, 
                   daily_costs: float, monthly_costs: float, annual_costs: float) -> None:
    # Formats and displays the calculated cost results in a table format.
    max_cost_length = max(len(f"{cost_per_shift:,.2f}"), 
                          len(f"{cost_per_hospital_per_shift:,.2f}"), 
                          len(f"{daily_costs:,.2f}"), 
                          len(f"{monthly_costs:,.2f}"), 
                          len(f"{annual_costs:,.2f}"))

    cost_format = f"{{:>{max_cost_length + 1},.2f}}"

    result = f"""
LLM Costing Analysis:
  Description                             |       Cost 
---------------------------------------------------------
| OpenAI Cost per shift                   | ${cost_format.format(cost_per_shift)} |
| Cost per hospital per shift             | ${cost_format.format(cost_per_hospital_per_shift)} |
| Daily Costs of OpenAI API Calls         | ${cost_format.format(daily_costs)} |
| OpenAI API costs per hospital per month | ${cost_format.format(monthly_costs)} |
| Annual cost per hospital for OpenAI API | ${cost_format.format(annual_costs)} |
---------------------------------------------------------
    """
    print(result)

def describe_scenario(prompts_per_shift: Union[int, float], multiplier: Union[int, float], 
                     avg_tokens_per_call: Union[int, float], token_cost_per_thousand: Union[int, float],
                     doctors_per_shift: Union[int, float], shifts_per_day: Union[int, float]) -> str:
    # Creates a descriptive paragraph of the given scenario using user inputs.
    description = (
        f"The scenario involves an example app 'Doctor Diagnosis Assistant App', which utilizes the OpenAI API. "
        f"Each doctor's shift involves sending an average of {prompts_per_shift} prompts to the API. "
        f"The average chain callbacks/augmentation multiplier is set at {multiplier}, "
        f"with an average usage of {avg_tokens_per_call} tokens per API call. "
        f"The cost of using the OpenAI API is ${token_cost_per_thousand:.2f} per 1000 tokens. "
        f"In each shift, there are {doctors_per_shift} doctors working at the hospital, "
        f"and the hospital operates {shifts_per_day} shifts per day."
    )
    return description

def print_pricing() -> None:
    """Displays current OpenAI pricing information to help users understand cost structure."""
    print("\n" + "="*60)
    print("CURRENT OPENAI PRICING REFERENCE (as of 2024)")
    print("="*60)
    print("GPT-4 Models:")
    print("  • GPT-4 (8K context):     $0.03/1K input tokens, $0.06/1K output tokens")
    print("  • GPT-4 (32K context):    $0.06/1K input tokens, $0.12/1K output tokens")
    print("  • GPT-4 Turbo:            $0.01/1K input tokens, $0.03/1K output tokens")
    print("\nGPT-3.5 Models:")
    print("  • GPT-3.5 Turbo:          $0.0015/1K input tokens, $0.002/1K output tokens")
    print("\nNote: Prices may vary. Check https://openai.com/pricing for latest rates.")
    print("      This calculator uses a simplified single rate per 1K tokens.")
    print("="*60 + "\n")

def setup_logging(log_level: str = "INFO", log_file: str = "token_calculator.log") -> None:
    """
    Configure comprehensive logging for the application.
    
    Sets up both file and console logging with appropriate formatters and handlers.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to the log file
    """
    # Convert string log level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(numeric_level)
    
    # Clear any existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    # File handler for detailed logging
    try:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)  # File gets all messages
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
    except IOError as e:
        print(f"Warning: Could not create log file '{log_file}': {e}")
    
    # Console handler for important messages only
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)  # Console gets warnings and errors only
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Log the setup completion
    logging.info("Logging system initialized")
    logging.info(f"Log level set to: {log_level}")
    logging.info(f"Log file: {log_file}")

def export_to_csv(calculation_data: Dict[str, Any], filename: Optional[str] = None) -> str:
    """
    Export calculation results to a CSV file.
    
    Args:
        calculation_data: Dictionary containing all calculation parameters and results
        filename: Optional custom filename. If None, generates timestamp-based filename
        
    Returns:
        str: The filename of the created CSV file
    """
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"openai_cost_analysis_{timestamp}.csv"
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow(['Metric', 'Value', 'Unit'])
            
            # Write input parameters
            writer.writerow(['=== INPUT PARAMETERS ===', '', ''])
            writer.writerow(['Prompts per shift', calculation_data['prompts_per_shift'], 'prompts'])
            writer.writerow(['Chain/interaction multiplier', calculation_data['multiplier'], 'multiplier'])
            writer.writerow(['Average tokens per call', calculation_data['avg_tokens_per_call'], 'tokens'])
            writer.writerow(['Cost per 1000 tokens', calculation_data['token_cost_per_thousand'], 'USD'])
            writer.writerow(['Doctors per shift', calculation_data['doctors_per_shift'], 'doctors'])
            writer.writerow(['Shifts per day', calculation_data['shifts_per_day'], 'shifts'])
            
            # Write calculated results
            writer.writerow(['', '', ''])
            writer.writerow(['=== CALCULATED RESULTS ===', '', ''])
            writer.writerow(['Cost per shift', f"${calculation_data['cost_per_shift']:.2f}", 'USD'])
            writer.writerow(['Cost per hospital per shift', f"${calculation_data['cost_per_hospital_per_shift']:.2f}", 'USD'])
            writer.writerow(['Daily costs', f"${calculation_data['daily_costs']:.2f}", 'USD'])
            writer.writerow(['Monthly costs', f"${calculation_data['monthly_costs']:.2f}", 'USD'])
            writer.writerow(['Annual costs', f"${calculation_data['annual_costs']:.2f}", 'USD'])
            
            # Write metadata
            writer.writerow(['', '', ''])
            writer.writerow(['=== METADATA ===', '', ''])
            writer.writerow(['Export timestamp', calculation_data['timestamp'], ''])
            writer.writerow(['Application', 'Token Costing Estimator', ''])
            writer.writerow(['Scenario', calculation_data['scenario_description'][:100] + '...', ''])
        
        return filename
        
    except IOError as e:
        raise IOError(f"Failed to write CSV file '{filename}': {e}")

def export_to_json(calculation_data: Dict[str, Any], filename: Optional[str] = None) -> str:
    """
    Export calculation results to a JSON file.
    
    Args:
        calculation_data: Dictionary containing all calculation parameters and results
        filename: Optional custom filename. If None, generates timestamp-based filename
        
    Returns:
        str: The filename of the created JSON file
    """
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"openai_cost_analysis_{timestamp}.json"
    
    try:
        # Structure the data for JSON export
        export_data = {
            "metadata": {
                "application": "Token Costing Estimator",
                "version": "1.0",
                "export_timestamp": calculation_data['timestamp'],
                "scenario_description": calculation_data['scenario_description']
            },
            "input_parameters": {
                "prompts_per_shift": calculation_data['prompts_per_shift'],
                "multiplier": calculation_data['multiplier'],
                "avg_tokens_per_call": calculation_data['avg_tokens_per_call'],
                "token_cost_per_thousand": calculation_data['token_cost_per_thousand'],
                "doctors_per_shift": calculation_data['doctors_per_shift'],
                "shifts_per_day": calculation_data['shifts_per_day']
            },
            "calculated_results": {
                "cost_per_shift": {
                    "value": calculation_data['cost_per_shift'],
                    "formatted": f"${calculation_data['cost_per_shift']:.2f}",
                    "unit": "USD"
                },
                "cost_per_hospital_per_shift": {
                    "value": calculation_data['cost_per_hospital_per_shift'],
                    "formatted": f"${calculation_data['cost_per_hospital_per_shift']:.2f}",
                    "unit": "USD"
                },
                "daily_costs": {
                    "value": calculation_data['daily_costs'],
                    "formatted": f"${calculation_data['daily_costs']:.2f}",
                    "unit": "USD"
                },
                "monthly_costs": {
                    "value": calculation_data['monthly_costs'],
                    "formatted": f"${calculation_data['monthly_costs']:.2f}",
                    "unit": "USD"
                },
                "annual_costs": {
                    "value": calculation_data['annual_costs'],
                    "formatted": f"${calculation_data['annual_costs']:.2f}",
                    "unit": "USD"
                }
            }
        }
        
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(export_data, jsonfile, indent=2, ensure_ascii=False)
        
        return filename
        
    except IOError as e:
        raise IOError(f"Failed to write JSON file '{filename}': {e}")
    except (TypeError, ValueError) as e:
        raise ValueError(f"Failed to serialize data to JSON: {e}")

def main() -> None:
    # Initialize logging system
    setup_logging()
    logging.info("Token Costing Estimator application started")
    
    try:
        # Load configuration-based defaults
        try:
            logging.info("Loading configuration settings")
            config = load_config()
            default_prompts_per_shift = config.get("default_prompts_per_shift", 50)
            default_multiplier = config.get("default_multiplier", 5)
            default_avg_tokens_per_call = config.get("default_avg_tokens_per_call", 2000)
            default_token_cost_per_thousand = config.get("default_token_cost_per_thousand", 0.06)
            default_doctors_per_shift = config.get("default_doctors_per_shift", 10)
            default_shifts_per_day = config.get("default_shifts_per_day", 3)
            logging.info(f"Configuration loaded successfully with defaults: prompts={default_prompts_per_shift}, multiplier={default_multiplier}, tokens={default_avg_tokens_per_call}, cost={default_token_cost_per_thousand}, doctors={default_doctors_per_shift}, shifts={default_shifts_per_day}")
        except ConfigurationError as e:
            logging.warning(f"Configuration error: {e}")
            print(f"⚠️  Configuration warning: {e}")
            print("Using built-in default values.")
            # Fallback to hardcoded defaults
            default_prompts_per_shift = 50
            default_multiplier = 5
            default_avg_tokens_per_call = 2000
            default_token_cost_per_thousand = 0.06
            default_doctors_per_shift = 10
            default_shifts_per_day = 3
            logging.info("Using built-in fallback defaults")

        # Parse command-line arguments
        args = parse_arguments()
        
        if args is not None:
            # Command-line mode: use provided arguments or defaults
            prompts_per_shift = args.prompts if args.prompts is not None else default_prompts_per_shift
            multiplier = args.multiplier if args.multiplier is not None else default_multiplier
            avg_tokens_per_call = args.tokens if args.tokens is not None else default_avg_tokens_per_call
            token_cost_per_thousand = args.cost if args.cost is not None else default_token_cost_per_thousand
            doctors_per_shift = args.doctors if args.doctors is not None else default_doctors_per_shift
            shifts_per_day = args.shifts if args.shifts is not None else default_shifts_per_day
            
            # Display the values being used in CLI mode
            print("Token Costing Estimator - Command Line Mode")
            print("=" * 50)
            print(f"Prompts per shift: {prompts_per_shift}")
            print(f"Chain/interaction multiplier: {multiplier}")
            print(f"Average tokens per call: {avg_tokens_per_call}")
            print(f"Cost per 1000 tokens: ${token_cost_per_thousand}")
            print(f"Doctors per shift: {doctors_per_shift}")
            print(f"Shifts per day: {shifts_per_day}")
            print("=" * 50)
        else:
            # Interactive mode: collect input from the user
            print("Token Costing Estimator - Interactive Mode")
            print("=" * 50)
            prompts_per_shift = float(get_input("Enter the number of prompts sent per doctor's shift", default_prompts_per_shift))
            multiplier = float(get_input("Enter the chain/interaction/augmentation multiplier", default_multiplier))
            avg_tokens_per_call = float(get_input("Enter the average tokens used per API call", default_avg_tokens_per_call))
            print_pricing()  # Prints the current OpenAI pricing
            token_cost_per_thousand = float(get_input("Enter the OpenAI price per 1000 tokens (GPT-4=$0.06) (in $)", default_token_cost_per_thousand))
            doctors_per_shift = float(get_input("Enter the number of doctors on shift per hospital", default_doctors_per_shift))
            shifts_per_day = float(get_input("Enter the number of shifts per day", default_shifts_per_day))

        # Initialize calculator and perform calculations
        calculator = OpenAICostCalculator(prompts_per_shift, multiplier, avg_tokens_per_call, token_cost_per_thousand)
        cost_per_shift = calculator.calculate_cost_per_shift()
        cost_per_hospital_per_shift = calculator.calculate_cost_per_hospital_per_shift(doctors_per_shift)
        daily_costs = calculator.calculate_daily_costs(shifts_per_day, doctors_per_shift)
        monthly_costs = calculator.calculate_monthly_costs(daily_costs)
        annual_costs = calculator.calculate_annual_costs(monthly_costs)

        # Display results
        description = describe_scenario(prompts_per_shift, multiplier, avg_tokens_per_call, token_cost_per_thousand, doctors_per_shift, shifts_per_day)
        print("\nScenario Description:")
        print(description)
        display_results(cost_per_shift, cost_per_hospital_per_shift, daily_costs, monthly_costs, annual_costs)
        
        # Prepare data for export
        calculation_data = {
            'timestamp': datetime.now().isoformat(),
            'prompts_per_shift': prompts_per_shift,
            'multiplier': multiplier,
            'avg_tokens_per_call': avg_tokens_per_call,
            'token_cost_per_thousand': token_cost_per_thousand,
            'doctors_per_shift': doctors_per_shift,
            'shifts_per_day': shifts_per_day,
            'cost_per_shift': cost_per_shift,
            'cost_per_hospital_per_shift': cost_per_hospital_per_shift,
            'daily_costs': daily_costs,
            'monthly_costs': monthly_costs,
            'annual_costs': annual_costs,
            'scenario_description': description
        }
        
        # Offer export options (only in interactive mode to avoid interrupting CLI workflows)
        if args is None:  # Interactive mode
            print("\n" + "="*50)
            print("DATA EXPORT OPTIONS")
            print("="*50)
            print("Would you like to export these results to a file?")
            print("1. Export to CSV")
            print("2. Export to JSON")
            print("3. Export to both formats")
            print("4. No export (continue)")
            
            try:
                export_choice = get_input("Enter your choice (1-4)", "4").strip()
                
                if export_choice in ['1', '3']:
                    try:
                        csv_filename = export_to_csv(calculation_data)
                        print(f"✅ CSV export successful: {csv_filename}")
                    except (IOError, ValueError) as e:
                        print(f"❌ CSV export failed: {e}")
                
                if export_choice in ['2', '3']:
                    try:
                        json_filename = export_to_json(calculation_data)
                        print(f"✅ JSON export successful: {json_filename}")
                    except (IOError, ValueError) as e:
                        print(f"❌ JSON export failed: {e}")
                
                if export_choice not in ['1', '2', '3', '4']:
                    print("Invalid choice. No export performed.")
                    
            except (EOFError, KeyboardInterrupt):
                print("\nExport cancelled.")
        else:  # CLI mode - silent operation, no export prompts
            pass

    except KeyboardInterrupt:
        print("\n\n" + "="*50)
        print("OPERATION CANCELLED")
        print("="*50)
        print("The cost calculation was interrupted by the user.")
        print("Thank you for using the Token Costing Estimator!")
        print("="*50)
        return
    except EOFError:
        print("\n\n" + "="*50)
        print("INPUT STREAM ENDED")
        print("="*50)
        print("The input stream ended unexpectedly (EOF detected).")
        print("This can happen when running in non-interactive environments.")
        print("All default values have been used for the calculation.")
        print("="*50)
    except ValueError as e:
        print("\n" + "="*50)
        print("INVALID INPUT ERROR")
        print("="*50)
        print(f"Error: {e}")
        print("\nThis error typically occurs when:")
        print("• Non-numeric values are entered for numeric fields")
        print("• Negative values are provided where positive numbers are expected")
        print("• Invalid characters are included in numeric inputs")
        print("\nPlease restart the program and ensure all inputs are valid positive numbers.")
        print("="*50)
    except Exception as e:
        print("\n" + "="*50)
        print("UNEXPECTED ERROR")
        print("="*50)
        print(f"An unexpected error occurred: {e}")
        print(f"Error type: {type(e).__name__}")
        print("\nThis is likely a bug in the program. Please report this issue with:")
        print("• The exact error message above")
        print("• The inputs you provided")
        print("• Your operating system and Python version")
        print("="*50)

if __name__ == "__main__":
    main()





























