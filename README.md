# llmmerge

A custom LLM-based Git merge driver.


# Usage as a Git Merge Driver

After installing the package, run the script: tools/add_git_global_options.sh to add the custom git merge driver as the secondary option for unresolved conflicts to the current installation of git.

You will also need to acquire a chatGPT API-key, and create the following environment variable in the shell running the git-merge command:

   export OPENAI_API_KEY="ChatGPT-API-KEY"

# ToDo Features

1. For large input files, you can pre-process the input prompt so that the size of the prompt is not 3 times the input file, by filtering out the common functions and classes etc.

2. Make a series of merge drivers with a series of increasingly complex/resource-intensive LLMs. To be used when the previous LLM fails to resolve conflict, satisfactorily.