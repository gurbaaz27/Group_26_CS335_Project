package main

func foo() bool {
	printf("This should not print")
	return true
}

func main() {
	a := 0
	if a >= 0 || foo() {
		printf("This should print in first line")
	}
	if a > 0 && foo() {
		printf("This should not print in second line")
	} else {
		printf("This should print in second line")
	}

	return
}