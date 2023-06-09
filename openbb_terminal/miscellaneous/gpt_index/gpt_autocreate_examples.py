"""
To run: python gpt_autocreate_examples.py
"""
import os
import random
import time
from pathlib import Path

import openai
from tqdm import tqdm

from openbb_terminal.core.session.current_user import get_current_user

PACKAGE_DIRECTORY = Path(__file__).parent.parent.parent
GPT_INDEX_DIRECTORY = PACKAGE_DIRECTORY / "miscellaneous" / "gpt_index/"


current_user = get_current_user()
os.environ["OPENAI_API_KEY"] = current_user.credentials.API_OPENAI_KEY


# Function to get GPT-4 response
def get_gpt_response(prompt):
    GPT_MODEL_NAME = "gpt-4"
    conversation = [
        {
            "role": "system",
            "content": "You are a helpful assistant that is well versed on financial terminals and concepts.",
        },
        {"role": "user", "content": prompt},
    ]
    print("\n Sending prompt to GPT-4...")

    max_retries = 5
    retry_delay = 5  # Time delay in seconds between retries

    for attempt in range(max_retries):
        try:
            response = openai.ChatCompletion.create(
                model=GPT_MODEL_NAME,
                messages=conversation,
                max_tokens=4000,
                n=1,
                stop=None,
                temperature=0.5,
            )
            if response is not None:
                return response.choices[0]["message"]["content"].strip()
        except Exception as e:
            print(f"Attempt {attempt + 1} failed with error: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Max retries reached. Aborting.")
                raise


# Folder containing text files
folder_path = GPT_INDEX_DIRECTORY

# Create a validation.csv file if it doesn't exist
validation_file = "validation.txt"
if not os.path.exists(validation_file):
    with open(validation_file, "w") as txtfile:
        txtfile.write("natural_text:cmd\n")

# Loop through each file in the folder with tqdm progress bar
for file_name in tqdm(os.listdir(folder_path)):
    if file_name.endswith(".txt"):
        print(f"\nProcessing file: {file_name}")
        file_path = os.path.join(folder_path, file_name)

        # Read the file content
        with open(file_path, encoding="utf-8") as file:
            file_content = file.read()

        # Check if the file_content has the word 'Examples:' in it
        if "Examples:" in file_content:
            continue

        # Create the prompt with help text and request for examples
        # prompt = f"here is some help text: {file_content}. Now provide me an explanation to this code:"

        prompt = f"""
            Given specific help text on a command and its parent command, for example:
            '
            parent_command: stocks/options/
            usage: oi [-m MIN] [-M MAX] [-c] [-p] [-e] [-h] [--export EXPORT][--sheet-name SHEET_NAME [SHEET_NAME ...]]
            [--raw]       [--source ]  Plot open interest. Open interest represents the number of contracts that exist.
            optional arguments:   -m MIN, --min MIN     Min strike to plot (default: -1)   -M MAX, --max MAX     Max
            strike to plot (default: -1)   -c, --calls   Flag to plot call options only (default: False)   -p, --puts
            Flag to plot put options only (default: False)   -e, --expiration                Select expiration
            date (YYYY-MM-DD) (default: )   -h, --help            show this help message (default: False)
            --export EXPORT       Export raw data into csv, json, xlsx and figure into
            png, jpg, pdf, svg (default: )   --sheet-name SHEET_NAME [SHEET_NAME ...]
            Name of excel sheet to save data to. Only valid for
            .xlsx files. (default: None)   --raw                 Flag to display raw data (default: False)   --source
            Data source to select from (default: YahooFinance)  For more information and examples, use 'about oi'
            to access the related guide.

            Examples:
            - Load <SYMBOL> and plot open interest for all options: stocks/load <SYMBOL>/options/oi
            - Load <SYMBOL> and plot open interest for call options only: stocks/load <SYMBOL>/options/oi -c
            - Load <SYMBOL> and plot open interest for put options only: stocks/load <SYMBOL>/options/oi -p
            - Load <SYMBOL> and plot open interest for strike prices
            between 10 and 50: stocks/load <SYMBOL>/options/oi -m 10 -M 50
            - Load <SYMBOL> and plot open interest for options expiring on a
            specific date: stocks/load <SYMBOL>/options/oi -e 2022-12-31
            - Load <SYMBOL> and plot open interest using a specific data
            source: stocks/load <SYMBOL>/options/oi --source Nasdaq
            - Load <SYMBOL> and export raw data in csv format: stocks/load <SYMBOL>/options/oi --export csv
            - Load <SYMBOL> and save data to a specific excel sheet: stocks/load <SYMBOL>/options/oi --sheet-name Sheet1
            - Load <SYMBOL> and display raw data: stocks/load <SYMBOL>/options/oi --raw
            '

            Knowing that, I want you to do the same with the following help text. Here are the rules:
            1. make sure to provide the minimum amount of examples required to cover all the possible ways to use the
            command with its parameters between 1-10.
            2. vary the natural language by not using the same sentences, vary the synonyms and
            the order of the sentences but always make sure to reference the command in the exampkle sentence.
            3. Based on the help text and summary, decide whether to load a <SYMBOL> before using each specific command
            (only some commands will not need to load a symbol if you dont refer to a specific company or symbol). for
            example: 'stocks/options/vol -m 50' --> 'stocks/load <SYMBOL>/options/vol -m 50'
                i) if in the examples, you plan to use a symbol in the example text, make sure to load it in
                the command text.
            4. Do not provide actual stock symbols, instead use <SYMBOL> as a
            placeholder. for example: 'stocks/load <SYMBOL>/options/vol -m 50'
            5. If it is related to crypto, use <COIN> as a placeholder. for example: 'crypto/load <COIN>/vol -m 50'
            6. If it is related to forex, use <PAIR> as a placeholder. for example: 'forex/load <PAIR>/vol -m 50'
            7. If it is related to futures, use <FUTURE> as a placeholder. for example:'futures/load <FUTURE>/vol -m 50'
            8. Every example must have the specific command from the specific help text.
            9. Do not start every command with - Load <> etc. Make sure the commands are varied and not repetitive.
            10. Do not have an example command that only asks for help and uses -h or --help.
            11. DO not use load <SYMBOL> in every example. You should use it when needed to load specific symbols or
            currencies. You must deduce if load is needed for a command based on the summary and the parent command.

            You must not add additional text and always provide the following format:

            Examples:
            <Examples>

            Here is the help text: {file_content}
            """  # noqa: S608

        # Get the GPT-3.5 response
        gpt_response = get_gpt_response(prompt)

        # write back everything
        # Extract the parent_command from file_content
        # parent_command = file_content.split("parent_command: ")[1].split("\n")[0].strip()

        # Append the response to the file
        # Write the modified file_content back to the file
        with open(file_path, "a") as file:
            file.write("\n")
            file.write(f"{gpt_response}")

        print(f"Appended GPT-4 examples to {file_name}")

        # Read the file content with the new prompt
        with open(file_path) as file:
            file_content = file.read()

        # Extract the examples section
        examples_section = file_content.split("Examples:")[-1]

        # Split the examples_section into a list of examples
        examples_list = examples_section.split("\n")

        # Filter out empty lines and remove leading/trailing whitespaces
        examples_list = [
            example.strip() for example in examples_list if example.strip()
        ]

        # only keep the first 50% of the examples
        if len(examples_list) > 2:
            examples_list = examples_list[: int(len(examples_list) / 2)]

        # Pick a random example
        random_example = random.choice(examples_list)

        # Remove the "-" at the beginning of the example only once
        random_example = random_example.replace("- ", "", 1)

        # also check if the example has a <SYMBOL> in it, if it does, replace with a random symbol from the symbols list
        symbols_list = ["AAPL", "MSFT", "TSLA", "GOOG", "BA", "GME"]
        crypto_list = ["BTC", "ETH", "DOGE", "ADA", "XRP", "LTC"]
        forex_list = ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "NZDUSD", "USDCAD"]
        futures_list = ["ES", "NQ", "YM", "RTY", "CL", "GC"]
        if any(
            tag in random_example
            for tag in ["<SYMBOL>", "<SIMILAR_TICKER>", "<TICKER>"]
        ):
            random_example = random_example.replace(
                "<TICKER>", random.choice(symbols_list)
            )
            random_example = random_example.replace(
                "<SYMBOL>", random.choice(symbols_list)
            )
            random_example = random_example.replace(
                "<SIMILAR_TICKER>", random.choice(symbols_list)
            )
        elif any(tag in random_example for tag in ["<COIN>", "<CRYPTO>"]):
            random_example = random_example.replace(
                "<COIN>", random.choice(crypto_list)
            )
            random_example = random_example.replace(
                "<CRYPTO>", random.choice(crypto_list)
            )
        elif any(tag in random_example for tag in ["<PAIR>", "<FOREX>"]):
            random_example = random_example.replace("<PAIR>", random.choice(forex_list))
            random_example = random_example.replace(
                "<FOREX>", random.choice(forex_list)
            )
        elif any(tag in random_example for tag in ["<FUTURE>"]):
            random_example = random_example.replace(
                "<FUTURE>", random.choice(futures_list)
            )

        # Create a prompt to request GPT-3.5 to make a minor tweak
        tweak_prompt = f"""
        Here is a random example of a natural command and how to call it using command line in a financial terminal:
        Load AAPL and print the last 10 messages: stocks/load AAPL/ba/messages -l 10

        Here is the same example with a minor tweak:
        Load TSLA and print the last 20 messages: stocks/load TSLA/ba/messages -l 20

        The tweak is that the symbol AAPL was changed to TSLA and the number of messages was changed from 10 to 20.
        I want you to do the same thing for the following example:
        '{random_example}'

        It is important that the tweak is minor and does not change the overall functionality of the command.
        The tweak should be to stock symbols, coins, forex pairs, futures, numbers, etc. but not to the command itself.
        Your response is to be a single line of text that is the tweaked example with no additional tex beside natural
        language and the command line command.
        """

        # Get the GPT-3.5 tweaked response
        tweaked_example = get_gpt_response(tweak_prompt)

        # Check if the tweaked_example is empty, if so, use the original random_example
        tweaked_example = (
            random_example if not tweaked_example.strip() else tweaked_example.strip()
        )

        # Append the extracted data to the validation.txt file
        with open(validation_file, "a") as txtfile:
            txtfile.write(f"{tweaked_example}\n")
