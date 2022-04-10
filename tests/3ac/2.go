// for loop and operators and multilevel pointers

func main() {

	x := 10    //dummy value
	px := &x   //assigned address of a variable
	ppx := &px //assigned address of another pointer

	*px = *px * 2

	**ppx = **ppx + 5

	a := 2
	b := &a
	c := &b
	d := *b
	e := **c
	**c = 1
	*b = 1

	z := 4 + **c

	j := 0

	for i := 0; i < 5; i++ {
		j++
	}

	// var x [3]int
	// x[1] = 3

	// var y *int
	// y = &x[1]

}
