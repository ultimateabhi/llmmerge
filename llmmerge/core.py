import re
import subprocess

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

    result = subprocess.run(['git','diff',main_branch,side_branch], capture_output=True, text=True)
    llm_prompt = f"""
Assume you are an expert developer. I have two versions of a file, from it's git commit history. version_1 is the version corresponding to the main branch that I am working on. version_2 is the version from the side branch that I want to merge on top my main branch.

Here is version_1 of the python file:
{main_branch_filestring}

And here is the output of git diff between version_1 and version_2 i.e. for git diff version_1 version_2:
{result.stdout}


You have to resolve the merge conflicts, for merging version_2 on top of version_1.

Please give the output in the below format:
1. ResolvedFile.py: Merged file having the changes in version_2 on top of version_1. Empty file in case there are unresolvable conflicts.
2. Explanation.txt: Please provide an explanation of the changes made from version_1 to version_2.
"""

    response = client.responses.create(
        model="o4-mini-2025-04-16",
        input = llm_prompt)

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
    common_ancestor_branch = f"{base_dir}/checkers/base/comparison_checker.ancestor_3w.py"
    main_branch = f"{base_dir}/checkers/base/comparison_checker.main_3w.py"
    side_branch = f"{base_dir}/checkers/base/comparison_checker.maintenance_3w.py"
    # side_branch = f"{base_dir}/checkers/base/comparison_checker.maintenance_latest.py"

    # main_branch = f"{base_dir}/checkers/base/comparison_checker.maintenance_3w.py"
    # side_branch = f"{base_dir}/checkers/base/comparison_checker.maintenance_3w.py"
    # side_branch = f"{base_dir}/checkers/base/comparison_checker.py"

    with open(common_ancestor_branch,'r') as f:
        common_ancestor_filestring = f.read()
    with open(main_branch,'r') as f:
        main_branch_filestring = f.read()
    with open(side_branch,'r') as f:
        side_branch_filestring = f.read()

    import subprocess
    result = subprocess.run(['git','diff',main_branch,side_branch], capture_output=True, text=True)

    response = client.responses.create(
        model="o4-mini-2025-04-16",
        input = f"""
Assume you are an expert developer. I have two versions of a file, from it's git commit history. version_1 is the version corresponding to the main branch that I am working on. version_2 is the version from the side branch that I want to merge on top my main branch.

Here is version_1 of the python file:
{main_branch_filestring}

And here is the output of git diff between version_1 and version_2 i.e. for git diff version_1 version_2:
{result.stdout}


You have to resolve the merge conflicts, for merging version_2 on top of version_1.

Please give the output in the below format:
1. ResolvedFile.py: Merged file having the changes in version_2 on top of version_1. Empty file in case there are unresolvable conflicts.
2. Explanation.txt: Please provide an explanation of the changes made from version_1 to version_2.
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




