// multilevel pointers

func localSwap(this int, that string) {
	hold := this
	this = that
	that = hold
}

func realSwap(this int, that *string) {
	hold := *this
	*this = *that
	*that = hold
}

func main() {

	x := 10 //dummy value
	px := &x //assigned address of a variable
	ppx := &px //assigned address of another pointer

	Printf("x =", x, ",px =", *px, ",ppx =", **ppx)
	*px = *px * 2
	Printf("x =", x, ",px =", *px, ",ppx =", **ppx)
	**ppx = **ppx + 5
	Printf("x =", x, ",px =", *px, ",ppx =", **ppx)

	this := "this"
	that := "that"

	Printf("this = ", this, "that = ", that)
	localSwap(this, that)
	Printf("After swap: this = ", this, "that = ", that) //no change
	realSwap(&this, &that)
	Printf("After real swap: this = ", this, "that = ", that)
}

