.PHONY: tests docs

tests:
	pytest tests -s

coverage:
	pytest tests -s --cov=jumpscale

docs:
	pdoc3 jumpscale --html --output-dir docs/api --overwrite
