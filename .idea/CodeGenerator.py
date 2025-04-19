import json
import re
import subprocess

import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


def generate_pojo(schema_data, target_language, type_name="GeneratedPojo"):
    try:
        quicktype_path = r"C:\Users\mprav\AppData\Roaming\npm\quicktype.cmd"

        json_string = json.dumps(schema_data)
        print(json_string)
        print(target_language)
        result = subprocess.run(
            [quicktype_path, "--lang", target_language, "--top-level", type_name],
            input=json_string,
            capture_output=True,
            text=True
        )

        print(result)
        print(result.stdout)
        if result.returncode == 0:
            return result.stdout
        else:
            return f"Error: {result.stderr}"
    except Exception as e:
        return f"An error occurred: {e}"


@app.route("/", methods=["GET"])
def home():
    return "QuickType Python API is running!"


@app.route("/generatepojo", methods=["POST"])
def generate_pojo_api():
    data = request.get_json()
    print(data)
    json_string = data.get("jsonString")
    target_language = data.get("targetLanguage")
    type_name = data.get("typeName", "GeneratedPojo")

    if isinstance(json_string, str):  # If jsonString is a string, parse it
        json_string = json.loads(json_string)

    print(json_string)

    if not json_string or not target_language:
        return jsonify({"error": "Missing 'jsonString' or 'targetLanguage'"}), 400

    generated_code = generate_pojo(json_string, target_language, type_name)
    return jsonify({"code": generated_code})


@app.route("/getfdc3refschemalist", methods=["GET"])
def get_fdc3_ref_schema_names():
    page_url = "https://fdc3.finos.org/docs/next/context/spec#standard-context-types"
    response = requests.get(page_url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    schema_names = []
    section_ids = ["standard-context-types"]

    for section_id in section_ids:
        section_header = soup.find("h2", id=section_id)
        if section_header:
            print(section_header)
            ul_element = section_header.find_next_sibling("ul")
            if ul_element:
                for li in ul_element.find_all("li"):
                    text = li.get_text(strip=True)
                    match = re.match(r"(fdc3\.[a-zA-Z0-9\.]+)", text)
                    print(match)
                    if match:
                        schema_names.append(match.group(1))

    return schema_names


if __name__ == "__main__":
    app.run(port=5000, debug=True)