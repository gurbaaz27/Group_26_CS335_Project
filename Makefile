test=1


scanner:
	python src/lexer.py tests/scanner/${test}.go


all:
	for f in tests/scanner/*; do \
		python src/lexer.py $$f; \
		if [ $$? -eq 0 ]; then \
			echo "✅ Test case $$number successful"; \
		else \
			echo "❌ Test case $$number unsuccessful"; \
		fi; \
	done