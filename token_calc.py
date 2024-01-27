import logging
from bs4 import BeautifulSoup
import json

class OpenAICostCalculator:
    """
    A class to calculate the cost of using OpenAI's API for an application.
    
    Attributes:
        prompts_per_shift (float): The number of prompts sent per doctor's shift.
        multiplier (float): The multiplier for chain interactions or augmentations.
        avg_tokens_per_call (float): Average tokens used per API call.
        token_cost_per_thousand (float): Cost of OpenAI API per 1000 tokens.
    """

    def __init__(self, prompts_per_shift, multiplier, avg_tokens_per_call, token_cost_per_thousand):
        # Validates the input parameters.
        self.validate_inputs(prompts_per_shift, multiplier, avg_tokens_per_call, token_cost_per_thousand)
        self.prompts_per_shift = prompts_per_shift
        self.multiplier = multiplier
        self.avg_tokens_per_call = avg_tokens_per_call
        self.token_cost_per_thousand = token_cost_per_thousand

    @staticmethod
    def validate_inputs(prompts_per_shift, multiplier, avg_tokens_per_call, token_cost_per_thousand):
        # Ensures all input parameters are positive numbers.
        if not all(isinstance(arg, (int, float)) and arg > 0 for arg in [prompts_per_shift, multiplier, avg_tokens_per_call, token_cost_per_thousand]):
            raise ValueError("All parameters should be positive numbers.")

    def calculate_tokens_per_shift(self):
        # Calculates the total number of tokens used per shift.
        return self.prompts_per_shift * self.multiplier * self.avg_tokens_per_call

    def calculate_cost_per_shift(self):
        # Calculates the total cost per shift based on the number of tokens used.
        tokens_per_shift = self.calculate_tokens_per_shift()
        return (tokens_per_shift / 1000) * self.token_cost_per_thousand

    def calculate_cost_per_hospital_per_shift(self, doctors_per_shift):
        # Calculates the total cost per hospital per shift.
        return self.calculate_cost_per_shift() * doctors_per_shift

    def calculate_daily_costs(self, shifts_per_day, doctors_per_shift):
        # Calculates the daily costs of OpenAI API calls for a hospital.
        return self.calculate_cost_per_hospital_per_shift(doctors_per_shift) * shifts_per_day

    def calculate_monthly_costs(self, daily_costs):
        days_per_month = 30  # Average number of days in a month
        return daily_costs * days_per_month

    def calculate_annual_costs(self, monthly_costs):
        months_per_year = 12  # Number of months in a year
        return monthly_costs * months_per_year

def get_input(prompt, default_value):
    # Captures user input or uses default value if no input is provided.
    user_input = input(f"{prompt} [{default_value}]: ")
    return user_input if user_input else default_value

def display_results(cost_per_shift, cost_per_hospital_per_shift, daily_costs, monthly_costs, annual_costs):
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

def describe_scenario(prompts_per_shift, multiplier, avg_tokens_per_call, token_cost_per_thousand, doctors_per_shift, shifts_per_day):
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

def print_pricing():
    # Retrieves and prints the current OpenAI pricing information in JSON format.
    openai_pricing = {
        # ... (pricing data goes here)
    }
    print(json.dumps(openai_pricing, indent=4))
    return

def main():
    try:
        # Default values for the calculator
        default_prompts_per_shift = 50
        default_multiplier = 5
        default_avg_tokens_per_call = 2000
        default_token_cost_per_thousand = 0.06 # from openai pricing
        default_doctors_per_shift = 10
        default_shifts_per_day = 3

        # User inputs with defaults
        # Collects input from the user or uses default values
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

    except ValueError as e:
        print(f"Invalid input: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
