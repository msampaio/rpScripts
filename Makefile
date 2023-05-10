build: dependencies
	python -m build

dependencies:
	pip install -U -r requirements.txt

clean:
	rm -rf build && \
	find . -type f -name '*.pyc' -exec rm {} \;

compile: dependencies clean
	pyinstaller rpscripts.spec