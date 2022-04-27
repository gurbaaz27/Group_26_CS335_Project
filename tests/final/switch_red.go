package main



func main() {
	var a int
	var b int 
	scanf(&a)
	scanf(&b)
	c := 2*a + 1
	d := 2*a + 2
	e := 2*a + 3
	f := 2*a + 4

	switch b + 1 {
		case c:
			printf("a")
		case d:
			printf("b") 
		case e:
			printf("c")
		case f:
			printf("d")
	}
}