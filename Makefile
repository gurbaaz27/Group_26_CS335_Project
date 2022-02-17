test=1


parser:
	python src/parser.py tests/parser/${test}.go


scanner:
	python src/lexer.py tests/scanner/${test}.go


scanner-all:
	for f in tests/scanner/*; do \
		python src/lexer.py $$f; \
		if [ $$? -eq 0 ]; then \
			echo "✅ Test case $$number successful"; \
		else \
			echo "❌ Test case $$number unsuccessful"; \
		fi; \
	done


parser-all:
	for f in tests/parser/*; do \
		python src/parser.py $$f; \
		if [ $$? -eq 0 ]; then \
			echo "✅ Test case $$number successful"; \
		else \
			echo "❌ Test case $$number unsuccessful"; \
		fi; \
	done
