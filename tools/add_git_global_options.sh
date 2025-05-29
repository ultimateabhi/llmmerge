git config --global merge.llmmerge.name "LLM Merge driver"
git config --global merge.llmmerge.driver "llmmerge-driver %O %A %B %A"

SCRIPT_PATH=$(realpath "$0")
SCRIPT_DIR=$(dirname "$SCRIPT_PATH")

git config --global core.attributesfile ${SCRIPT_DIR}/gitattributes_global