package main

var A *float32

func main() {
	var a int = 5
	var b *int = &a
	var c **int = &b
	d := &c
	
	var e float32 = 4.2
	A = &e 

	printf(*b)
	printf(**c)
	printf(*b * **c)
	printf(**d)
	printf(*A)

	return
}