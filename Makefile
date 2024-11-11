build: lock
	poetry build

lock: dependencies
	poetry lock

dependencies:
	pip install -U -r requirements.txt
	pip install -U -r docs/requirements.txt

clean:
	rm -rf build && \
	find . -type f -name '*.pyc' -exec rm {} \;