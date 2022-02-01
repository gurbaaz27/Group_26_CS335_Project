test=1


scanner:
	python src/lexer.py tests/scanner/${test}.go


all:
	number=1 ; while [[ $$number -le 12 ]] ; do \
		python src/lexer.py tests/scanner/$$number.go; \
		if [[ $$? -eq 0 ]]; then \
			echo "✅ Test case $$number successful"; \
		else \
			echo "❌ Test case $$number unsuccessful"; \
		fi; \
		((number = number + 1)) ; \
	done