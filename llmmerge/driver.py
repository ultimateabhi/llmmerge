import sys
from llmmerge.core import llm_merge

def main():
    if len(sys.argv) != 5:
        print("Usage: llmmerge-driver <base> <ours> <theirs> <output>")
        sys.exit(2)
    base, ours, theirs, output = sys.argv[1:5]
    merged_file_string = llm_merge(base, ours, theirs)
    if merged_file_string:
        with open(output, "w") as f_out:
            f_out.write(merged_file_string)
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
