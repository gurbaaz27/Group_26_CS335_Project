package main

const a string = "First string"
var b string = "Second string"

func main() {
	const c string = "Third string"
	var d string = "Fourth string"

	printf(a + b)
	printf(b + d)
	printf(c + a)
	printf(d + b + c)

	return
}
