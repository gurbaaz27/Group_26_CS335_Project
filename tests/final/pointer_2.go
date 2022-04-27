package main


func main() {
	var y int  = 6;
	var x *int = &(y);
	y = 2
	*(&y) = 4
	var g *int = &y;

	var p int = 2
	var a1 int = 5
	var a2 *int = &a1
	var a3 **int = &a2
	var a4 ***int = &a3
	var r ****int = &a4
	printf(****r)
	***r = &p
	printf(****r)
	printf(y)
}