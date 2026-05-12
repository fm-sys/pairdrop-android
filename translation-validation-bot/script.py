import os
import time
from deep_translator import GoogleTranslator
import requests
import re

# extracting all the input from environments
INPUT_PR_NUMBER = os.environ['INPUT_PR']

print("PR number: " + INPUT_PR_NUMBER)

printcache=""
def print2cache(str):
    global printcache
    printcache += str
    printcache += "\n"

repository = os.getenv("GITHUB_REPOSITORY", "fm-sys/pairdrop-android")
url = 'https://github.com/' + repository + '/pull/' + INPUT_PR_NUMBER + '.diff'
r = requests.get(url + "", allow_redirects=True)
text = r.content.decode()

translator = GoogleTranslator(source="auto", target="en")

table_initialized = False
counter = 0

for line in text.splitlines():
    if line.startswith("+"):
        match = re.search("<string.*?name=\"(.+?)\".*?>(.*)</string>", line)
        if match:
            if not table_initialized:
                table_initialized = True
                print2cache("ID|Translation|Reverse translated source string\n-|-|-")
            success = False
            retries = 0
            max_retries = 5
            while not success and retries < max_retries:
                counter += 1
                retries += 1
                try:
                    source_text = match.group(2).replace("\\n", " \\n ")
                    translated_text = translator.translate(source_text)
                    print("API call #" + str(counter) + " ok")
                    success = True
                except Exception:
                    print("API call #" + str(counter) + " failed, wait some seconds and try again...")
                    time.sleep(60)
            if success:
                print2cache(f"{match.group(1)}|{source_text} (auto)|{translated_text} (en)")
            else:
                print2cache(f"{match.group(1)}|translation failed|translation failed after retries")
        elif line.startswith("+++"):
            print2cache("\n\n" + line + "\n")
            table_initialized = False


ACTION_ENV_DELIMITER = "__ENV_DELIMITER__"
def _build_file_input(name, value):
    return (
        f"{name}"
        f"<<{ACTION_ENV_DELIMITER}\n"
        f"{value}\n"
        f"{ACTION_ENV_DELIMITER}\n".encode("utf-8")
    )

with open(os.environ["GITHUB_OUTPUT"], "ab") as f:
    f.write(_build_file_input("content", printcache.strip()))
