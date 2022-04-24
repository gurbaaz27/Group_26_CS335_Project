package main

// var b int = 9

// func hello() {
// 	printf(4.0)
// 	return
// }

func main() {
	// var a int = 1
	// var b int = 2
	// printf(a + b)
	var a int = 5
	var i int
	for i = 0; i < 10; i++ { // incdec doesnt work rn
		a = a + 1
	}
	printf(a)
	for ; i < 20; i++ { // incdec doesnt work rn
		a = a + 1
	}
	printf(a)
	for i = 0; ; i++ { // incdec doesnt work rn
		a = a + 1
		break
	}
	printf(a)
	for i = 0; i < 10; { // incdec doesnt work rn
		a = a + 1
		i++
	}
	printf(a)
	for ; i < 20 ; { // incdec doesnt work rn
		a = a + 1
		i++
	}
	printf(a)
	for i = 0; ; { // incdec doesnt work rn
		a = a + 1
		i++
		break
	}
	printf(a)
	for ; ; i++ { // incdec doesnt work rn
		a = a + 1
		break
	}
	printf(a)
	i = 0
	for ; ;  { // incdec doesnt work rn
		a = a + 1
		i++
		if i == 10 {
			break
		}
	}
	printf(a)
	// printf(a)
	// printf(s + a)
	// var b int = 1
	// printf(b << 4)
	// hello()

	// if i > 10 {py
	// 	i = i + 1
	// } else {
	// 	i = i + 2
	// }
	// b = 10
	// var b int8 = 5
	// b = 11
	// var b bool = true
	// var c float64 = 0.9
	// a = a + 5
	return
}
