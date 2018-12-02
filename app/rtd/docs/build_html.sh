rm -rf /opt/SCRIPTS/sphinx-docs/static/_script_docs/*
rm -rf /opt/SCRIPTS/sphinx-docs/static/_build/*
source /opt/SCRIPTS/sphinx-docs/venv/bin/activate
find /opt | grep -e "\.rst$" -e "\.md$" | grep -v sphinx-docs | grep -v "/python" | grep -v "__remove__" | xargs -I{} cp {} /opt/SCRIPTS/sphinx-docs/static/_script_docs/
make html

