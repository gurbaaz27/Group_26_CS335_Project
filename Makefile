test=1


parser:
	python src/parser.py tests/parser/${test}.go


scanner:
	python src/lexer.py tests/scanner/${test}.go


graph:
	dot -Tpdf ${test}.dot -o ${test}.pdf


scanner-all:
	for f in tests/scanner/*; do \
		python src/lexer.py $$f; \
		if [ $$? -eq 0 ]; then \
			echo "✅ Test case $$number successful"; \
		else \
			echo "❌ Test case $$number unsuccessful"; \
		fi; \
	done


clean:
	rm -rf src/parser.out
	rm -rf src/parsetab.py