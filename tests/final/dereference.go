package main

func main() {
	a := 2.0
	b := &a
	c := &b
	d := *b
	e := **c
	printf(e)
	**c = 1.09
	*b = 1.909

	z := 4.9098 + **c
	printf(z)

	var w float32 = 3.0
	*(&w) = 5.90
	printf(w)
	printf(d)
}