package main

var num float64 = 22.0

func main() {
	const denom float64 = 7.0

	a := 0.001

	z := num * a

	printf(num / denom)
	printf(a*a)
	printf(z)

	return
}
