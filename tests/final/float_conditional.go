package main

var num float32 = 22.0

func main() {
	const y string = "Yes"
	const n string = "No"

	const denom float32 = 7.0

	var a float32 = 0.001

	z := num * a

	printf(num / denom)
	printf(a*a)
	printf(z)

	if !(a > z) {
		printf(y)
	} else {
		printf(n)
	}

	return
}
