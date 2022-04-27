package main

func foo() bool {
	printf("This should print")
	return true
}

func main() {
	a := 0
	if ((a > 0 && foo()) && (a >= 0 && foo())) {
		printf("This should not print in first line")
	} else {
		printf("This should print in first line")
	}
	return
}