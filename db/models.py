from db.database import get_db_connection



# USER


def create_user(username, email, password_hash):

    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
        INSERT INTO users
        (username, email, password_hash)
        VALUES (%s, %s, %s)
    """

    cursor.execute(
        query,
        (username, email, password_hash)
    )

    connection.commit()

    user_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return user_id


def get_user_by_email(email):

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT *
        FROM users
        WHERE email = %s
    """

    cursor.execute(query, (email,))

    user = cursor.fetchone()

    cursor.close()
    connection.close()

    return user


def get_user_by_id(user_id):

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT id, username, email, created_at
        FROM users
        WHERE id = %s
    """

    cursor.execute(query, (user_id,))

    user = cursor.fetchone()

    cursor.close()
    connection.close()

    return user


# PROFILE


def create_profile(
    user_id,
    full_name=None,
    bio=None,
    profile_image=None,
    github_url=None,
    linkedin_url=None
):

    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
        INSERT INTO user_profiles
        (
            user_id,
            full_name,
            bio,
            profile_image,
            github_url,
            linkedin_url
        )
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    cursor.execute(
        query,
        (
            user_id,
            full_name,
            bio,
            profile_image,
            github_url,
            linkedin_url
        )
    )

    connection.commit()

    cursor.close()
    connection.close()


def get_profile(user_id):

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT *
        FROM user_profiles
        WHERE user_id = %s
    """

    cursor.execute(query, (user_id,))

    profile = cursor.fetchone()

    cursor.close()
    connection.close()

    return profile


def update_profile(
    user_id,
    full_name,
    bio,
    profile_image,
    github_url,
    linkedin_url
):

    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
        UPDATE user_profiles
        SET
            full_name = %s,
            bio = %s,
            profile_image = %s,
            github_url = %s,
            linkedin_url = %s
        WHERE user_id = %s
    """

    cursor.execute(
        query,
        (
            full_name,
            bio,
            profile_image,
            github_url,
            linkedin_url,
            user_id
        )
    )

    connection.commit()

    cursor.close()
    connection.close()



# SUBMISSION


def create_submission(
    user_id,
    problem_id,
    problem_title,
    language,
    code,
    status,
    passed_tests,
    total_tests,
    runtime_ms=None,
    memory_kb=None
):

    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
        INSERT INTO submissions
        (
            user_id,
            problem_id,
            problem_title,
            language,
            code,
            status,
            passed_tests,
            total_tests,
            runtime_ms,
            memory_kb
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    cursor.execute(
        query,
        (
            user_id,
            problem_id,
            problem_title,
            language,
            code,
            status,
            passed_tests,
            total_tests,
            runtime_ms,
            memory_kb
        )
    )

    connection.commit()

    submission_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return submission_id


def get_user_submissions(user_id):

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            id,
            problem_id,
            problem_title,
            language,
            status,
            passed_tests,
            total_tests,
            runtime_ms,
            memory_kb,
            submitted_at
        FROM submissions
        WHERE user_id = %s
        ORDER BY submitted_at DESC
    """

    cursor.execute(query, (user_id,))

    submissions = cursor.fetchall()

    cursor.close()
    connection.close()

    return submissions


def get_problem_submissions(user_id, problem_id):

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT *
        FROM submissions
        WHERE user_id = %s
        AND problem_id = %s
        ORDER BY submitted_at DESC
    """

    cursor.execute(
        query,
        (user_id, problem_id)
    )

    submissions = cursor.fetchall()

    cursor.close()
    connection.close()

    return submissions


def get_submission(submission_id, user_id):

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT *
        FROM submissions
        WHERE id = %s
        AND user_id = %s
    """

    cursor.execute(
        query,
        (submission_id, user_id)
    )

    submission = cursor.fetchone()

    cursor.close()
    connection.close()

    return submission

def get_solved_problems(user_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT
            problem_id,
            problem_title,
            MIN(submitted_at) AS solved_at
        FROM submissions
        WHERE user_id = %s
        AND status = 'Accepted'
        GROUP BY problem_id, problem_title
        ORDER BY solved_at DESC
    """

    cursor.execute(query, (user_id,))

    result = cursor.fetchall()

    cursor.close()
    connection.close()

    return result
def get_submission_count(user_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
        SELECT COUNT(*)
        FROM submissions
        WHERE user_id = %s
    """

    cursor.execute(query, (user_id,))

    result = cursor.fetchone()[0]

    cursor.close()
    connection.close()

    return result
def get_solved_count(user_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
        SELECT COUNT(DISTINCT problem_id)
        FROM submissions
        WHERE user_id = %s
        AND status = 'Accepted'
    """

    cursor.execute(query, (user_id,))

    result = cursor.fetchone()[0]

    cursor.close()
    connection.close()

    return result