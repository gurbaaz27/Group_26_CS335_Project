package main

var b int = 6

func main() {
	var a int = 5
	const y string = "Yes"
	const n string = "No"

	switch a {
		case 1: printf(y)
		case 2: printf(n)
		case 6: printf(a)
		default: printf(a+100)
	}

	switch a {
		case 1: b = b + 100
		case 2: b++
		case 5: b *= 9
		default: b--
	}

	printf(b)

	return
}
