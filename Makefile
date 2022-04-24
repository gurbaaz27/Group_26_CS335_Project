test=1

final:
	python src/compiler.py tests/final/${test}.go


ir:
	python src/compiler.py tests/3ac/${test}.go


semantic:
	python src/compiler.py tests/semantic/${test}.go


parser:
	python src/compiler.py tests/parser/${test}.go


scanner:
	python src/lexer.py tests/scanner/${test}.go


graph:
	dot -Tpdf ${test}.dot -o ${test}.pdf


clean:
	rm -rf src/parser.out
	rm -rf src/parsetab.py
	rm -rf *.dot
	rm -rf *.csv
	rm -rf *.png
	rm -rf *.3ac
	rm -rf *.s