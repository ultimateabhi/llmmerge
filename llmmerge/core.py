import re
from openai import OpenAI

def llm_merge(base, ours, theirs):
    """
    Dummy LLM merge function.
    Args:
        base (str): Path to base file
        ours (str): Path to ours file
        theirs (str): Path to theirs file
    Returns:
        str: Path to resolved file if resolved, or empty string if not resolved
    """

    client = OpenAI()

    common_ancestor_branch = base
    main_branch = ours
    side_branch = theirs

    with open(f"{common_ancestor_branch}",'r') as f:
        common_ancestor_filestring = f.read()
    with open(f"{main_branch}",'r') as f:
        main_branch_filestring = f.read()
    with open(f"{side_branch}",'r') as f:
        side_branch_filestring = f.read()

    if main_branch_filestring == side_branch_filestring:
        return main_branch_filestring

    response = client.responses.create(
        model="o4-mini-2025-04-16",
        input = f"""
Assume you are an expert developer.

Here are the three versions of the same python file:
1. version 1:
{common_ancestor_filestring}

2. version 2:
{main_branch_filestring}

3. version 3:
{side_branch_filestring}


These are three versions of the same file from three different commits.
version 2 is the file version from the main branch; version 3: from a side branch; version 1: file version from the common ancestor of main branch and side branch. You have to resolve the merge conflicts.

Please give the output in the below format:
1. ResolvedFile.py: Merged file have the changes in version 3 on top of version 2. Empty file in case there are unresolvable conflicts.
2. Explanation.txt: Please provide an explanation of the changes made from version 2 to version 3.
"""
    )


    content = response.output_text
    # Extract the Python code and explanation using regex
    resolved_code_match = re.search(r"1\. ResolvedFile\.py:\s*```python\n(.*?)```", content, re.DOTALL)
    explanation_match = re.search(r"2\. Explanation\.txt:\s*(.*)", content, re.DOTALL)

    resolved_code = resolved_code_match.group(1).strip() if resolved_code_match else ""
    explanation = explanation_match.group(1).strip() if explanation_match else ""

    return resolved_code


if __name__ == "__main__":
    import re
    from openai import OpenAI

    client = OpenAI()

    base_dir="/Users/abhiag/Downloads/git_merge_llm/test_repo/pylint/pylint"
    common_ancestor_branch = "checkers/base/comparison_checker.ancestor_3w.py"
    # main_branch = "checkers/base/comparison_checker.main_3w.py"
    # # side_branch = "checkers/base/comparison_checker.maintenance_3w.py"
    # side_branch = "checkers/base/comparison_checker.maintenance_latest.py"

    main_branch = "checkers/base/comparison_checker.maintenance_3w.py"
    # side_branch = "checkers/base/comparison_checker.maintenance_3w.py"
    side_branch = "checkers/base/comparison_checker.py"

    with open(f"{base_dir}/{common_ancestor_branch}",'r') as f:
        common_ancestor_filestring = f.read()
    with open(f"{base_dir}/{main_branch}",'r') as f:
        main_branch_filestring = f.read()
    with open(f"{base_dir}/{side_branch}",'r') as f:
        side_branch_filestring = f.read()


    response = client.responses.create(
        model="o4-mini-2025-04-16",
        input = f"""
Assume you are an expert developer.

Here are the three versions of the same python file:
1. version 1:
{common_ancestor_filestring}

2. version 2:
{main_branch_filestring}

3. version 3:
{side_branch_filestring}


These are three versions of the same file from three different commits.
version 2 is the file version from the main branch; version 3: from a side branch; version 1: file version from the common ancestor of main branch and side branch. You have to resolve the merge conflicts.

Please give the output in the below format:
1. ResolvedFile.py: Merged file have the changes in version 3 on top of version 2. Empty file in case there are unresolvable conflicts.
2. Explanation.txt: Please provide an explanation of the changes made from version 2 to version 3.
"""
    )


    content = response.output_text
    # Extract the Python code and explanation using regex
    resolved_code_match = re.search(r"1\. ResolvedFile\.py:\s*```python\n(.*?)```", content, re.DOTALL)
    explanation_match = re.search(r"2\. Explanation\.txt:\s*(.*)", content, re.DOTALL)

    resolved_code = resolved_code_match.group(1).strip() if resolved_code_match else ""
    explanation = explanation_match.group(1).strip() if explanation_match else ""

    print(content)
    # with open("ResolvedFile.py", "w") as f:
    #     f.write(resolved_code)

    # with open("Explanation.txt", "w") as f:
    #     f.write(explanation)




