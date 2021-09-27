# flake8
echo -e "[Begin flake8]\n"
flake8 .
echo -e "\n[End flake8]"

# mypy
echo -e "[Begin mypy]\n"
mypy --ignore-missing-imports --install-types .
echo -e "\n[End mypy]"
	
# bandit
echo -e "[Begin bandit]\n"
bandit -r .
echo -e "\n[End bandit]"
