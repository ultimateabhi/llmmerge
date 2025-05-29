# llmmerge

A custom LLM-based Git merge driver.


# Usage as a Git Merge Driver

After installing the package, run the script: tools/add_git_global_options.sh to add the custom git merge driver as the secondary option for unresolved conflicts to the current installation of git.

You will also need to acquire a chatGPT API-key, and create the following environment variable in the shell running the git-merge command:

   export OPENAI_API_KEY="ChatGPT-API-KEY"

# ToDo Features

1. For large input files, you can pre-process the input prompt so that the size of the prompt is lesser by using a language parser and sending only the required context -- using git diff line numbers to identify the context. You can then stitch together the merged function and the rest of the common file to get the merged file.

2. Make a series of merge drivers with a series of increasingly complex/resource-intensive LLMs. To be used when the previous LLM fails to resolve conflict, satisfactorily.