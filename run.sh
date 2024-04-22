# Load python environment 
#source venv/bin/activate

# Create python package
python setup.py sdist #bdist_wheel

# Upload to PYPI
twine upload dist/*


