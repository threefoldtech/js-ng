.PHONY: tests docs api_docs docs-serve

tests:
	pytest tests -s

coverage:
	pytest tests -s --cov=jumpscale

api_docs:
	pdoc3 jumpscale --html --output-dir docs/api --force

docs: api_docs

docs-serve:
	python3 -m http.server -d docs
