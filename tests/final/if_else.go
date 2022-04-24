package main

// var b int = 9

// func hello() {
// 	printf(4.0)
// 	return
// }

func main() {
	var a int = 5
	const y string = "Yes"
	const b string = "No"

	if a == 5 {
		printf(y)
	}

	var i int

	if i = 9; i < 10 {
		printf(y)
	}

	if a < 4 {
		printf(b)
	} else {
		printf(y)
	}

	if i = 10; i < 9 {
		printf(b)
	} else {
		printf(y)
	}

	a = 7

	if a*a == 25 {
		printf(b)
	} else if a*a == 49{
		printf(y)
	} else {
		printf(b)
	}

	if a+3 == 11 {
		printf(b)
	} else {
		if a+3 == 10 {
			printf(y)
		} else {
			printf(b)
		}
	}

	if a = 8; a*a == 25 {
		printf(b)
	} else if a*a == 49{
		printf(b)
	} else {
		printf(y)
	}

	return
}
