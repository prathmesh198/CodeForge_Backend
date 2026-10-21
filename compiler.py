import requests
import time
import json
import re


JUDGE0_URL = "https://ce.judge0.com/submissions"

LANGUAGE_IDS = {
    "python": 71,
    "java": 62,
    "cpp": 54
}


def submit_to_judge0(source_code, language):

    language = language.lower()

    if language not in LANGUAGE_IDS:
        return {
            "status": {"description": "Compilation Error"},
            "stderr": f"Unsupported language: {language}",
            "stdout": None,
            "compile_output": None,
            "time": None,
            "memory": None
        }

    payload = {
        "source_code": source_code,
        "language_id": LANGUAGE_IDS[language],
        "stdin": ""
    }

    try:

        response = requests.post(
            JUDGE0_URL,
            params={
                "base64_encoded": "false",
                "wait": "false"
            },
            json=payload,
            timeout=15
        )

        if response.status_code not in [200, 201]:
            return {
                "status": {
                    "description": "Judge0 Request Error"
                },
                "stderr": response.text,
                "stdout": None,
                "compile_output": None,
                "time": None,
                "memory": None
            }

        token = response.json().get("token")

        if not token:
            return {
                "status": {
                    "description": "Judge0 Request Error"
                },
                "stderr": "Judge0 did not return a submission token.",
                "stdout": None,
                "compile_output": None,
                "time": None,
                "memory": None
            }

        # ----------------------------------------------------
        # Poll Judge0
        # ----------------------------------------------------

        for _ in range(30):

            time.sleep(1)

            result_response = requests.get(
                f"{JUDGE0_URL}/{token}",
                params={
                    "base64_encoded": "false"
                },
                timeout=15
            )

            if result_response.status_code != 200:
                continue

            result = result_response.json()

            status_id = result.get(
                "status",
                {}
            ).get(
                "id"
            )

            # 1 = In Queue
            # 2 = Processing
            if status_id not in [1, 2]:
                return result

        return {
            "status": {
                "description": "Time Limit Exceeded"
            },
            "stderr": "Judge0 execution timeout.",
            "stdout": None,
            "compile_output": None,
            "time": None,
            "memory": None
        }

    except requests.exceptions.Timeout:

        return {
            "status": {
                "description": "Judge0 Request Timeout"
            },
            "stderr": "Judge0 request timed out.",
            "stdout": None,
            "compile_output": None,
            "time": None,
            "memory": None
        }

    except Exception as e:

        return {
            "status": {
                "description": "Judge0 Request Error"
            },
            "stderr": str(e),
            "stdout": None,
            "compile_output": None,
            "time": None,
            "memory": None
        }


# ============================================================
# INPUT PARSER
# ============================================================

def parse_input(test_input):

    if isinstance(
        test_input,
        (dict, list, int, float, bool)
    ):
        return test_input

    if test_input is None:
        return None

    try:
        return json.loads(test_input)

    except Exception:
        return test_input




def java_value(value, parameter_type=""):

    if value is None:
        return "null"

    if isinstance(value, bool):
        return "true" if value else "false"

    if isinstance(value, str):

        escaped = (
            value
            .replace("\\", "\\\\")
            .replace('"', '\\"')
        )

        return f'"{escaped}"'

    if isinstance(value, list):

        parameter_type = parameter_type.strip()

        # ----------------------------------------------------
        # int[]
        # ----------------------------------------------------

        if parameter_type == "int[]":

            values = []

            for item in value:
                values.append(str(item))

            return (
                "new int[]{"
                + ",".join(values)
                + "}"
            )

        # ----------------------------------------------------
        # Integer[]
        # ----------------------------------------------------

        if parameter_type == "Integer[]":

            values = []

            for item in value:
                values.append(str(item))

            return (
                "new Integer[]{"
                + ",".join(values)
                + "}"
            )

        # ----------------------------------------------------
        # String[]
        # ----------------------------------------------------

        if parameter_type == "String[]":

            values = []

            for item in value:

                escaped = (
                    str(item)
                    .replace("\\", "\\\\")
                    .replace('"', '\\"')
                )

                values.append(
                    f'"{escaped}"'
                )

            return (
                "new String[]{"
                + ",".join(values)
                + "}"
            )

        # ----------------------------------------------------
        # double[]
        # ----------------------------------------------------

        if parameter_type == "double[]":

            values = [
                str(item)
                for item in value
            ]

            return (
                "new double[]{"
                + ",".join(values)
                + "}"
            )

        # ----------------------------------------------------
        # boolean[]
        # ----------------------------------------------------

        if parameter_type == "boolean[]":

            values = []

            for item in value:

                values.append(
                    "true"
                    if item
                    else "false"
                )

            return (
                "new boolean[]{"
                + ",".join(values)
                + "}"
            )

        # ----------------------------------------------------
        # long[]
        # ----------------------------------------------------

        if parameter_type == "long[]":

            values = [
                str(item)
                for item in value
            ]

            return (
                "new long[]{"
                + ",".join(values)
                + "}"
            )

        # ----------------------------------------------------
        # float[]
        # ----------------------------------------------------

        if parameter_type == "float[]":

            values = [
                str(item) + "f"
                for item in value
            ]

            return (
                "new float[]{"
                + ",".join(values)
                + "}"
            )

        # ----------------------------------------------------
        # Default array
        # ----------------------------------------------------

        values = [
            str(item)
            for item in value
        ]

        return (
            "new int[]{"
            + ",".join(values)
            + "}"
        )

    if isinstance(value, float):
        return str(value)

    return str(value)




def cpp_value(value):

    if value is None:
        return "nullptr"

    if isinstance(value, bool):

        return (
            "true"
            if value
            else "false"
        )

    if isinstance(value, str):

        escaped = (
            value
            .replace("\\", "\\\\")
            .replace('"', '\\"')
        )

        return f'"{escaped}"'

    if isinstance(value, list):

        values = []

        for item in value:

            if isinstance(item, str):

                escaped = (
                    item
                    .replace("\\", "\\\\")
                    .replace('"', '\\"')
                )

                values.append(
                    f'"{escaped}"'
                )

            elif isinstance(item, bool):

                values.append(
                    "true"
                    if item
                    else "false"
                )

            else:

                values.append(
                    str(item)
                )

        return (
            "{"
            + ",".join(values)
            + "}"
        )

    return str(value)


# ============================================================
# JAVA METHOD INFORMATION
# ============================================================

def get_java_method_info(
    code,
    function_name
):

    # Handles:
    #
    # public int maxProfit(int[] prices)
    # public static int maxProfit(int[] prices)
    # int maxProfit(int[] prices)
    # private List<Integer> twoSum(...)
    #
    # The important part is that the function name is matched
    # directly.

    pattern = (
        r"\b"
        r"(?:public\s+|private\s+|protected\s+)?"
        r"(?:static\s+)?"
        r"(?:final\s+)?"
        r"([\w<>\[\], ?]+?)"
        r"\s+"
        + re.escape(function_name)
        + r"\s*"
        r"\("
        r"([^)]*)"
        r"\)"
    )

    match = re.search(
        pattern,
        code,
        re.MULTILINE
    )

    if not match:

        return None, []

    return_type = match.group(1).strip()

    parameter_text = match.group(2).strip()

    parameters = []

    if parameter_text:

        for parameter in parameter_text.split(","):

            parameter = parameter.strip()

            if not parameter:
                continue

            # Remove annotations
            parameter = re.sub(
                r"@\w+(?:\([^)]*\))?\s*",
                "",
                parameter
            )

            # Remove final
            parameter = re.sub(
                r"\bfinal\b\s*",
                "",
                parameter
            )

            parts = parameter.split()

            if len(parts) < 2:
                continue

            parameter_name = parts[-1]

            parameter_type = " ".join(
                parts[:-1]
            )

            parameters.append(
                (
                    parameter_type,
                    parameter_name
                )
            )

    return return_type, parameters


# ============================================================
# JAVA PARAMETERS
# ============================================================

def get_java_parameters(
    code,
    function_name
):

    return_type, parameters = get_java_method_info(
        code,
        function_name
    )

    if return_type is None:
        return []

    return parameters


# ============================================================
# JAVA RETURN TYPE
# ============================================================

def get_java_return_type(
    code,
    function_name
):

    return_type, parameters = get_java_method_info(
        code,
        function_name
    )

    if return_type is None:
        return "void"

    return return_type


# ============================================================
# JAVA DRIVER
# ============================================================

def create_java_driver(
    user_code,
    function_name,
    test_input
):

    user_code = user_code.strip()

    # --------------------------------------------------------
    # Remove public from Solution
    # --------------------------------------------------------

    user_code = re.sub(
        r"public\s+class\s+Solution",
        "class Solution",
        user_code
    )

    # --------------------------------------------------------
    # Remove public from Main if user accidentally added Main
    # --------------------------------------------------------

    user_code = re.sub(
        r"public\s+class\s+Main",
        "class Main",
        user_code
    )

    # --------------------------------------------------------
    # Get method information
    # --------------------------------------------------------

    return_type, parameters = get_java_method_info(
        user_code,
        function_name
    )

    if return_type is None:

        raise ValueError(
            f"Could not find Java function: {function_name}"
        )

    print(
        "JAVA RETURN TYPE:",
        return_type
    )

    print(
        "JAVA PARAMETERS:",
        parameters
    )

    # --------------------------------------------------------
    # Parse input
    # --------------------------------------------------------

    data = parse_input(test_input)

    declarations = []
    arguments = []

    # ========================================================
    # DICTIONARY INPUT
    # ========================================================

    if isinstance(data, dict):

        for parameter_type, parameter_name in parameters:

            if parameter_name not in data:

                raise ValueError(
                    f"Missing test input parameter: "
                    f"{parameter_name}"
                )

            value = data[
                parameter_name
            ]

            declaration = (
                f"{parameter_type} "
                f"{parameter_name} = "
                f"{java_value(value, parameter_type)};"
            )

            declarations.append(
                declaration
            )

            arguments.append(
                parameter_name
            )

    # ========================================================
    # LIST INPUT
    # ========================================================

    elif isinstance(data, list):

        # ----------------------------------------------------
        # One parameter
        #
        # Example:
        #
        # int[] prices
        #
        # [7,1,5,3,6,4]
        # ----------------------------------------------------

        if len(parameters) == 1:

            parameter_type, parameter_name = (
                parameters[0]
            )

            declaration = (
                f"{parameter_type} "
                f"{parameter_name} = "
                f"{java_value(data, parameter_type)};"
            )

            declarations.append(
                declaration
            )

            arguments.append(
                parameter_name
            )

        # ----------------------------------------------------
        # Multiple parameters
        #
        # Example:
        #
        # int[] nums, int target
        #
        # [[2,7,11,15],9]
        # ----------------------------------------------------

        else:

            if len(data) != len(parameters):

                raise ValueError(
                    "Number of test inputs does not "
                    "match function parameters."
                )

            for i, (
                parameter_type,
                parameter_name
            ) in enumerate(parameters):

                value = data[i]

                declaration = (
                    f"{parameter_type} "
                    f"{parameter_name} = "
                    f"{java_value(value, parameter_type)};"
                )

                declarations.append(
                    declaration
                )

                arguments.append(
                    parameter_name
                )

    # ========================================================
    # SINGLE VALUE
    # ========================================================

    else:

        if len(parameters) != 1:

            raise ValueError(
                "Test input does not match "
                "function parameters."
            )

        parameter_type, parameter_name = (
            parameters[0]
        )

        declaration = (
            f"{parameter_type} "
            f"{parameter_name} = "
            f"{java_value(data, parameter_type)};"
        )

        declarations.append(
            declaration
        )

        arguments.append(
            parameter_name
        )

    # ========================================================
    # FUNCTION CALL
    # ========================================================

    call = (
        f"solution.{function_name}"
        f"({', '.join(arguments)})"
    )

    # ========================================================
    # OUTPUT
    # ========================================================

    if return_type == "void":

        output_code = f"""
        {call};
"""

    elif "[]" in return_type:

        output_code = f"""
        System.out.println(
            java.util.Arrays.toString(
                {call}
            )
        );
"""

    elif return_type.startswith("List<"):

        output_code = f"""
        System.out.println(
            {call}
        );
"""

    else:

        output_code = f"""
        System.out.println(
            {call}
        );
"""

    # ========================================================
    # MAIN
    # ========================================================

    driver = f"""
public class Main {{

    public static void main(String[] args) {{

        Solution solution = new Solution();

        {chr(10).join(declarations)}

        {output_code}
    }}
}}
"""

    return (
        user_code
        + "\n\n"
        + driver
    )


# ============================================================
# PYTHON PARAMETERS
# ============================================================

def get_python_parameters(
    code,
    function_name
):

    pattern = (
        r"def\s+"
        + re.escape(function_name)
        + r"\s*\((.*?)\)"
    )

    match = re.search(
        pattern,
        code,
        re.DOTALL
    )

    if not match:
        return []

    text = match.group(1).strip()

    if not text:
        return []

    parameters = []

    for item in text.split(","):

        item = item.strip()

        if not item:
            continue

        # Remove default value
        item = item.split("=")[0].strip()

        # Remove type annotation
        parameter_name = (
            item.split(":")[0]
            .strip()
        )

        parameters.append(
            parameter_name
        )

    return parameters


# ============================================================
# PYTHON DRIVER
# ============================================================

def create_python_driver(
    user_code,
    function_name,
    test_input
):

    data = parse_input(test_input)

    parameters = get_python_parameters(
        user_code,
        function_name
    )

    if not parameters:

        raise ValueError(
            f"Could not find Python function: "
            f"{function_name}"
        )

    arguments = []

    # --------------------------------------------------------
    # Dictionary
    # --------------------------------------------------------

    if isinstance(data, dict):

        for parameter in parameters:

            if parameter not in data:

                raise ValueError(
                    f"Missing test input parameter: "
                    f"{parameter}"
                )

            arguments.append(
                repr(data[parameter])
            )

    # --------------------------------------------------------
    # List
    # --------------------------------------------------------

    elif isinstance(data, list):

        if len(parameters) == 1:

            arguments.append(
                repr(data)
            )

        else:

            if len(data) != len(parameters):

                raise ValueError(
                    "Number of test inputs does not "
                    "match function parameters."
                )

            for value in data:

                arguments.append(
                    repr(value)
                )

    # --------------------------------------------------------
    # Single value
    # --------------------------------------------------------

    else:

        if len(parameters) != 1:

            raise ValueError(
                "Test input does not match "
                "function parameters."
            )

        arguments.append(
            repr(data)
        )

    # --------------------------------------------------------
    # Function call
    # --------------------------------------------------------

    call = (
        f"solution.{function_name}"
        f"({', '.join(arguments)})"
    )

    driver = f"""

if __name__ == "__main__":

    solution = Solution()

    result = {call}

    print(result)
"""

    return (
        user_code
        + "\n"
        + driver
    )


# ============================================================
# C++ PARAMETERS
# ============================================================

def get_cpp_parameters(
    code,
    function_name
):

    pattern = (
        r"(?:public:|private:|protected:)?\s*"
        r"(?:static\s+)?"
        r"[\w:<>, ?\[\]&*]+"
        r"\s+"
        + re.escape(function_name)
        + r"\s*\((.*?)\)"
    )

    match = re.search(
        pattern,
        code,
        re.DOTALL
    )

    if not match:
        return []

    text = match.group(1).strip()

    if not text:
        return []

    parameters = []

    for item in text.split(","):

        item = item.strip()

        parts = item.split()

        if len(parts) < 2:
            continue

        parameter_name = parts[-1]

        parameter_type = " ".join(
            parts[:-1]
        )

        parameters.append(
            (
                parameter_type,
                parameter_name
            )
        )

    return parameters


# ============================================================
# C++ RETURN TYPE
# ============================================================

def get_cpp_return_type(
    code,
    function_name
):

    pattern = (
        r"(?:public:|private:|protected:)?\s*"
        r"(?:static\s+)?"
        r"([\w:<>, ?\[\]&*]+)"
        r"\s+"
        + re.escape(function_name)
        + r"\s*\("
    )

    match = re.search(
        pattern,
        code
    )

    if not match:
        return "void"

    return match.group(1).strip()


# ============================================================
# C++ OUTPUT
# ============================================================

def cpp_output_code(
    call,
    return_type
):

    return_type = return_type.strip()

    # --------------------------------------------------------
    # vector
    # --------------------------------------------------------

    if "vector" in return_type:

        return f"""
        auto result = {call};

        for (size_t i = 0; i < result.size(); i++) {{

            if (i > 0)
                cout << " ";

            cout << result[i];
        }}

        cout << endl;
"""

    # --------------------------------------------------------
    # Array
    # --------------------------------------------------------

    if "[]" in return_type:

        return f"""
        auto result = {call};

        for (auto value : result) {{

            cout << value << " ";
        }}

        cout << endl;
"""

    # --------------------------------------------------------
    # Normal value
    # --------------------------------------------------------

    return f"""
        cout << {call} << endl;
"""


# ============================================================
# C++ DRIVER
# ============================================================

def create_cpp_driver(
    user_code,
    function_name,
    test_input
):

    data = parse_input(test_input)

    parameters = get_cpp_parameters(
        user_code,
        function_name
    )

    if not parameters:

        raise ValueError(
            f"Could not find C++ function: "
            f"{function_name}"
        )

    declarations = []
    arguments = []

    # ========================================================
    # DICTIONARY
    # ========================================================

    if isinstance(data, dict):

        for parameter_type, parameter_name in parameters:

            if parameter_name not in data:

                raise ValueError(
                    f"Missing test input parameter: "
                    f"{parameter_name}"
                )

            value = data[
                parameter_name
            ]

            declaration = (
                f"{parameter_type} "
                f"{parameter_name} = "
                f"{cpp_value(value)};"
            )

            declarations.append(
                declaration
            )

            arguments.append(
                parameter_name
            )

    # ========================================================
    # LIST
    # ========================================================

    elif isinstance(data, list):

        if len(parameters) == 1:

            parameter_type, parameter_name = (
                parameters[0]
            )

            # vector<int>
            if "vector" in parameter_type:

                declaration = (
                    f"{parameter_type} "
                    f"{parameter_name} = "
                    f"{cpp_value(data)};"
                )

            else:

                declaration = (
                    f"{parameter_type} "
                    f"{parameter_name} = "
                    f"{cpp_value(data)};"
                )

            declarations.append(
                declaration
            )

            arguments.append(
                parameter_name
            )

        else:

            if len(data) != len(parameters):

                raise ValueError(
                    "Number of test inputs does not "
                    "match function parameters."
                )

            for i, (
                parameter_type,
                parameter_name
            ) in enumerate(parameters):

                declaration = (
                    f"{parameter_type} "
                    f"{parameter_name} = "
                    f"{cpp_value(data[i])};"
                )

                declarations.append(
                    declaration
                )

                arguments.append(
                    parameter_name
                )

    # ========================================================
    # SINGLE VALUE
    # ========================================================

    else:

        if len(parameters) != 1:

            raise ValueError(
                "Test input does not match "
                "function parameters."
            )

        parameter_type, parameter_name = (
            parameters[0]
        )

        declaration = (
            f"{parameter_type} "
            f"{parameter_name} = "
            f"{cpp_value(data)};"
        )

        declarations.append(
            declaration
        )

        arguments.append(
            parameter_name
        )

    # ========================================================
    # FUNCTION CALL
    # ========================================================

    call = (
        f"solution.{function_name}"
        f"({', '.join(arguments)})"
    )

    # ========================================================
    # RETURN TYPE
    # ========================================================

    return_type = get_cpp_return_type(
        user_code,
        function_name
    )

    # ========================================================
    # OUTPUT
    # ========================================================

    output_code = cpp_output_code(
        call,
        return_type
    )

    # ========================================================
    # MAIN
    # ========================================================

    driver = f"""
int main() {{

    Solution solution;

    {chr(10).join(declarations)}

    {output_code}

    return 0;
}}
"""

    # IMPORTANT:
    # Includes must come before Solution.

    return (
        "#include <bits/stdc++.h>\n"
        "using namespace std;\n\n"
        + user_code
        + "\n\n"
        + driver
    )


# ============================================================
# MAIN EXECUTION
# ============================================================

def execute_code(
    code: str,
    language: str,
    function_name: str = None,
    test_input=None
):

    language = language.lower()

    # ========================================================
    # VALIDATION
    # ========================================================

    if not function_name:

        return {
            "status": {
                "description": "Compilation Error"
            },
            "stderr": "Problem function_name is missing.",
            "stdout": None,
            "compile_output": None,
            "time": None,
            "memory": None
        }

    if test_input is None:

        return {
            "status": {
                "description": "Compilation Error"
            },
            "stderr": "Test input is missing.",
            "stdout": None,
            "compile_output": None,
            "time": None,
            "memory": None
        }

    # ========================================================
    # GENERATE DRIVER
    # ========================================================

    try:

        if language == "java":

            executable_code = create_java_driver(
                code,
                function_name,
                test_input
            )

        elif language == "python":

            executable_code = create_python_driver(
                code,
                function_name,
                test_input
            )

        elif language == "cpp":

            executable_code = create_cpp_driver(
                code,
                function_name,
                test_input
            )

        else:

            return {
                "status": {
                    "description": "Compilation Error"
                },
                "stderr": (
                    f"Unsupported language: {language}"
                ),
                "stdout": None,
                "compile_output": None,
                "time": None,
                "memory": None
            }

    except Exception as e:

        print("\n======================================")
        print("DRIVER GENERATION ERROR")
        print("======================================")
        print(str(e))
        print("======================================\n")

        return {
            "status": {
                "description": "Compilation Error"
            },
            "stderr": str(e),
            "stdout": None,
            "compile_output": None,
            "time": None,
            "memory": None
        }

    # ========================================================
    # DEBUG GENERATED CODE
    # ========================================================

    print("\n======================================")
    print("GENERATED CODE")
    print("======================================")
    print(executable_code)
    print("======================================\n")

    # ========================================================
    # SEND TO JUDGE0
    # ========================================================

    result = submit_to_judge0(
        executable_code,
        language
    )

    # ========================================================
    # DEBUG JUDGE0 RESULT
    # ========================================================

    print("\n======================================")
    print("JUDGE0 RESULT")
    print("======================================")

    print("STATUS:")
    print(result.get("status"))

    print("\nCOMPILE OUTPUT:")
    print(result.get("compile_output"))

    print("\nSTDERR:")
    print(result.get("stderr"))

    print("\nSTDOUT:")
    print(result.get("stdout"))

    print("\nTIME:")
    print(result.get("time"))

    print("\nMEMORY:")
    print(result.get("memory"))

    print("======================================\n")

    return result