import os
import subprocess

# Run black and isort first
subprocess.run(["black", "."], check=False)
subprocess.run(["isort", "."], check=False)

# Fix common patterns
for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith(".py"):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, "r") as f:
                    content = f.read()

                # Fix f-strings without placeholders
                import re

                content = re.sub(r'f"([^{]*)"', r'"\1"', content)
                content = re.sub(r"f'([^{]*)'", r"'\1'", content)

                with open(filepath, "w") as f:
                    f.write(content)
            except:
                pass

print("Quick fixes applied")
