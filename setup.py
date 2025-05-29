from setuptools import setup, find_packages

setup(
    name="llmmerge",
    version="0.2.0",
    packages=find_packages(),
    install_requires=[],  # Add dependencies here if needed
    entry_points={
        "console_scripts": [
            "llmmerge-driver = llmmerge.driver:main"
        ]
    },
    author="Abhishek Agarwal",
    email="ultimateabhi@gmail.com",
    description="A custom LLM-based git merge driver.",
    python_requires=">=3.10",
)
