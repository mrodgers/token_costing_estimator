# Token Costing Estimator/Calculator

This repository contains a Python script for calculating the cost of using OpenAI's API in a healthcare application scenario. The script is designed to provide an estimate of the costs associated with using OpenAI's language models based on various input parameters such as the number of prompts sent per doctor's shift, token usage, and OpenAI's pricing.

## Features

- **Cost Calculation**: Comprehensive calculation of total tokens used per doctor's shift
- **Multi-level Analysis**: Estimation of costs at shift, daily, monthly, and annual levels
- **Hospital-wide Costing**: Calculation of total costs per hospital per shift
- **Robust Error Handling**: Graceful handling of user input errors, EOF conditions, and keyboard interrupts
- **Type Safety**: Full type hint coverage for improved code reliability and IDE support
- **Interactive Pricing Reference**: Built-in display of current OpenAI pricing information
- **Input Validation**: Comprehensive validation of all user inputs with clear error messages

## Installation

To run this script, you will need Python 3.6 or higher installed on your system. The application uses only Python's built-in standard library modules, so **no external dependencies are required**.

### Quick Start

1. Ensure you have Python 3.6+ installed:
   ```bash
   python --version
   # or
   python3 --version
   ```

2. No additional packages need to be installed - the script is ready to run!

## Setup

1. **Clone the Repository**: Clone this repository to your local machine using:
   ```bash
   git clone https://github.com/mrodgers/token_costing_estimator.git
   ```
## Usage

To run the script, navigate to the directory containing the script and execute:

```bash
python token_calc.py

Enter the number of prompts sent per doctor's shift [50]: 
Enter the chain/interaction/augmentation multiplier [5]: 
Enter the average tokens used per API call [2000]: {}
Enter the OpenAI price per 1000 tokens (GPT-4=$0.06) (in $) [0.06]: 
Enter the number of doctors on shift per hospital [10]: 
Enter the number of shifts per day [3]: 

Scenario Description:
The scenario involves an example app 'Doctor Diagnosis Assistant App', which utilizes the OpenAI API. Each doctor's shift involves sending an average of 50.0 prompts to the API. The average chain callbacks/augmentation multiplier is set at 5.0, with an average usage of 2000.0 tokens per API call. The cost of using the OpenAI API is $0.06 per 1000 tokens. In each shift, there are 10.0 doctors working at the hospital, and the hospital operates 3.0 shifts per day.

LLM Costing Analysis:
  Description                             |       Cost 
---------------------------------------------------------
| OpenAI Cost per shift                   | $      30.00 |
| Cost per hospital per shift             | $     300.00 |
| Daily Costs of OpenAI API Calls         | $     900.00 |
| OpenAI API costs per hospital per month | $  27,000.00 |
| Annual cost per hospital for OpenAI API | $ 324,000.00 |
---------------------------------------------------------
```


Follow the prompts to enter the required parameters or use the default values.

## Contributing

Contributions are welcome! Feel free to fork the repository and submit pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

Matt Rodgers - mrodgers.junk gmail

Project Link: [https://github.com/mrodgers/token_costing_estimator](https://github.com/mrodgers/token_costing_estimator)


