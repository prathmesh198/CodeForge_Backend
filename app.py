from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from jose import JWTError, jwt
from compiler import execute_code
from probelm import load_problems
from db.database import get_db_connection

from db.models import (
    create_user,
    get_user_by_email,
    get_user_by_id,
    create_submission,
    get_solved_problems,
    get_submission_count,
    get_solved_count
)

from auth import (
    hash_password,
    verify_password,
    create_access_token,
    SECRET_KEY,
    ALGORITHM
)


app = FastAPI()



app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)




oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="login"
)




class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ExecuteRequest(BaseModel):
    problem_id: int
    language: str
    code: str
    submit: bool = False




@app.get("/")
def read_root():

    return {
        "message": "CodeForge API is running"
    }




@app.post("/register")
def register(data: RegisterRequest):

    existing_user = get_user_by_email(
        data.email
    )

    if existing_user:

        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    password_hash = hash_password(
        data.password
    )

    user_id = create_user(
        data.username,
        data.email,
        password_hash
    )

    return {
        "message": "Registration successful",
        "user_id": user_id
    }




@app.post("/login")
def login(data: LoginRequest):

    user = get_user_by_email(
        data.email
    )

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    password_valid = verify_password(
        data.password,
        user["password_hash"]
    )

    if not password_valid:

        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    token = create_access_token({
        "sub": str(user["id"]),
        "username": user["username"]
    })

    return {
        "message": "Login successful",
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"]
        }
    }




def get_current_user(
    token: str = Depends(oauth2_scheme)
):

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id = payload.get("sub")

        if user_id is None:

            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

        try:

            user_id = int(user_id)

        except (ValueError, TypeError):

            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

    except JWTError:

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    user = get_user_by_id(
        user_id
    )

    if user is None:

        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    return user




@app.get("/me")
def current_user(
    user=Depends(get_current_user)
):

    return {
        "user": user
    }




@app.post("/logout")
def logout():

    return {
        "message": "Logout successful"
    }




@app.get("/problem")
def read_problem():

    problems = load_problems()

    # Never expose hidden tests
    safe_problems = []

    for problem in problems:

        safe_problem = problem.copy()

        if "test_cases" in safe_problem:

            safe_problem["test_cases"] = [
                test
                for test in safe_problem["test_cases"]
                if not test.get("hidden", False)
            ]

        safe_problems.append(
            safe_problem
        )

    return safe_problems




@app.get("/problem/{problem_id}")
def read_problem_by_id(
    problem_id: int
):

    problems = load_problems()

    for problem in problems:

        if int(problem.get("id")) == int(problem_id):

            safe_problem = problem.copy()

            # NEVER SEND HIDDEN TEST CASES
            # TO FRONTEND
            if "test_cases" in safe_problem:

                safe_problem["test_cases"] = [
                    test
                    for test in safe_problem["test_cases"]
                    if not test.get("hidden", False)
                ]

            return safe_problem

    raise HTTPException(
        status_code=404,
        detail="Problem not found"
    )




@app.get("/problem/search")
def search_problem(
    title: str = Query(...)
):

    problems = load_problems()

    filtered_problems = []

    for problem in problems:

        if title.lower() in problem["title"].lower():

            safe_problem = problem.copy()

            if "test_cases" in safe_problem:

                safe_problem["test_cases"] = [
                    test
                    for test in safe_problem["test_cases"]
                    if not test.get("hidden", False)
                ]

            filtered_problems.append(
                safe_problem
            )

    if not filtered_problems:

        raise HTTPException(
            status_code=404,
            detail="No problems found"
        )

    return filtered_problems




@app.get("/solution")
def read_solution():

    return {
        "Solution": "This is a simple solution"
    }



@app.get("/Roadmap")
def read_roadmap():

    return {
        "Roadmap": "This is a simple roadmap"
    }




@app.get("/profile")
def profile(
    current_user=Depends(get_current_user)
):

    user_id = current_user["id"]

    solved_problems = get_solved_problems(
        user_id
    )

    submission_count = get_submission_count(
        user_id
    )

    solved_count = get_solved_count(
        user_id
    )

    return {

        "user": {
            "id": current_user["id"],
            "username": current_user["username"],
            "email": current_user["email"]
        },

        "stats": {
            "solved": solved_count,
            "submissions": submission_count
        },

        "solved_problems": solved_problems
    }




@app.post("/execute")
def execute(
    request: ExecuteRequest,
    current_user=Depends(get_current_user)
):

    problems = load_problems()

    print("======================================")
    print("CODEFORGE EXECUTION")
    print("======================================")

    print(
        "TOTAL PROBLEMS:",
        len(problems)
    )

    print(
        "REQUEST PROBLEM ID:",
        request.problem_id
    )

    print(
        "LANGUAGE:",
        request.language
    )

    print(
        "SUBMIT:",
        request.submit
    )

    print(
        "USER:",
        current_user["username"]
    )

    # ======================================================
    # FIND PROBLEM
    # ======================================================

    problem = next(
        (
            p
            for p in problems
            if int(p.get("id")) ==
            int(request.problem_id)
        ),
        None
    )

    if problem is None:

        raise HTTPException(
            status_code=404,
            detail="Problem not found"
        )

    print(
        "FOUND PROBLEM:",
        problem.get("title")
    )

    print(
        "FUNCTION:",
        problem.get("function_name")
    )

    # ======================================================
    # ALL TESTS
    # ======================================================

    all_tests = problem.get(
        "test_cases",
        []
    )

    print(
        "ALL TEST CASES:",
        all_tests
    )

    print(
        "TEST COUNT:",
        len(all_tests)
    )

    # ======================================================
    # RUN CODE
    # ======================================================
    #
    # Run Code:
    # ONLY visible tests
    #
    # hidden = False
    #
    # ======================================================

    if not request.submit:

        test_cases = [
            test
            for test in all_tests
            if not test.get(
                "hidden",
                False
            )
        ]

    # ======================================================
    # SUBMIT
    # ======================================================
    #
    # Submit:
    # ALL tests
    #
    # ======================================================

    else:

        test_cases = all_tests

    print(
        "TESTS TO RUN:",
        len(test_cases)
    )

    # ======================================================
    # NO TESTS
    # ======================================================

    if len(test_cases) == 0:

        return {
            "status": "Test Case Error",
            "passed_tests": 0,
            "total_tests": 0,
            "runtime_ms": None,
            "memory_kb": None,
            "error": (
                "No test cases found "
                "for this problem"
            )
        }

    # ======================================================
    # COUNTERS
    # ======================================================

    passed_tests = 0

    total_tests = len(
        test_cases
    )

    total_runtime = 0.0

    max_memory = 0

    # ======================================================
    # RUN EACH TEST
    # ======================================================

    for index, test in enumerate(
        test_cases
    ):

        print(
            "\n--------------------------------------"
        )

        print(
            f"RUNNING TEST {index + 1}:",
            test
        )

        test_input = test.get(
            "input"
        )

        expected_output = test.get(
            "expected_output"
        )

        print(
            "INPUT:",
            test_input
        )

        print(
            "EXPECTED:",
            expected_output
        )

        # ==================================================
        # EXECUTE COMPILER
        # ==================================================

        result = execute_code(
            code=request.code,
            language=request.language,
            function_name=problem.get(
                "function_name"
            ),
            test_input=test_input
        )

        print(
            "JUDGE RESULT:",
            result
        )

        # ==================================================
        # STATUS
        # ==================================================

        status_description = result.get(
            "status",
            {}
        ).get(
            "description",
            "Runtime Error"
        )

        # ==================================================
        # EXECUTION ERROR
        # ==================================================

        if status_description != "Accepted":

            return {
                "status": status_description,
                "passed_tests": passed_tests,
                "total_tests": total_tests,
                "runtime_ms": result.get(
                    "time"
                ),
                "memory_kb": result.get(
                    "memory"
                ),
                "error": (
                    result.get("stderr")
                    or result.get(
                        "compile_output"
                    )
                    or result.get(
                        "message"
                    )
                    or "Execution failed"
                )
            }

        # ==================================================
        # RUNTIME
        # ==================================================

        try:

            runtime = result.get(
                "time"
            )

            if runtime is not None:

                total_runtime += (
                    float(runtime) * 1000
                )

        except (
            ValueError,
            TypeError
        ):

            pass

        # ==================================================
        # MEMORY
        # ==================================================

        try:

            memory = result.get(
                "memory"
            )

            if memory is not None:

                max_memory = max(
                    max_memory,
                    int(memory)
                )

        except (
            ValueError,
            TypeError
        ):

            pass

        # ==================================================
        # ACTUAL OUTPUT
        # ==================================================

        actual_output = (
            result.get(
                "stdout"
            )
            or ""
        ).strip()

        expected_output = str(
            expected_output
        ).strip()

        # ==================================================
        # NORMALIZE OUTPUT
        # ==================================================

        actual_normalized = " ".join(
            actual_output.split()
        )

        expected_normalized = " ".join(
            expected_output.split()
        )

        print(
            "ACTUAL:",
            actual_normalized
        )

        print(
            "EXPECTED:",
            expected_normalized
        )

        # ==================================================
        # WRONG ANSWER
        # ==================================================

        if actual_normalized != expected_normalized:

            return {
                "status": "Wrong Answer",
                "passed_tests": passed_tests,
                "total_tests": total_tests,
                "runtime_ms": (
                    round(
                        total_runtime,
                        2
                    )
                    if total_runtime
                    else None
                ),
                "memory_kb": (
                    max_memory
                    if max_memory
                    else None
                ),
                "actual_output": actual_output,
                "expected_output": expected_output
            }

        # ==================================================
        # PASSED
        # ==================================================

        passed_tests += 1

        print(
            "TEST RESULT: PASSED"
        )

    # ======================================================
    # ALL TESTS PASSED
    # ======================================================

    print(
        "\n======================================"
    )

    print(
        "ALL TESTS PASSED"
    )

    print(
        "PASSED:",
        passed_tests
    )

    print(
        "TOTAL:",
        total_tests
    )

    print(
        "RUNTIME:",
        total_runtime
    )

    print(
        "MEMORY:",
        max_memory
    )

    print(
        "======================================"
    )

    # ======================================================
    # SAVE SUBMISSION
    # ======================================================

    if request.submit:

        try:

            create_submission(
                user_id=current_user["id"],
                problem_id=problem["id"],
                problem_title=problem["title"],
                language=request.language,
                code=request.code,
                status="Accepted",
                passed_tests=passed_tests,
                total_tests=total_tests,
                runtime_ms=(
                    int(total_runtime)
                    if total_runtime
                    else None
                ),
                memory_kb=(
                    max_memory
                    if max_memory
                    else None
                )
            )

            print(
                "SUBMISSION SAVED"
            )

        except Exception as e:

            print(
                "SUBMISSION SAVE ERROR:",
                e
            )

    # ======================================================
    # RESPONSE
    # ======================================================

    return {
        "status": "Accepted",
        "passed_tests": passed_tests,
        "total_tests": total_tests,
        "runtime_ms": (
            round(
                total_runtime,
                2
            )
            if total_runtime
            else None
        ),
        "memory_kb": (
            max_memory
            if max_memory
            else None
        )
    }


# ==================================================
# DATABASE TEST
# ==================================================

@app.get("/db-test")
def database_test():

    connection = get_db_connection()

    cursor = connection.cursor()

    cursor.execute(
        "SELECT 1"
    )

    result = cursor.fetchone()

    cursor.close()

    connection.close()

    return {
        "message":
            "Database connected successfully",

        "result":
            result
    }