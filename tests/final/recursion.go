// You can edit this code!
// Click here and start typing.
package main

const mod int = 900

func foo(a int, b int) int {
	// printf(a)
	if b == 1 {
		if a > 0 {
			return (foo(a-1, 0) + (b+6)*(foo(a-1, 0)) + (foo(a-1, 0))) % mod
		}
	} else {
		if a > 0 {
			return (a*foo(a-1, 1) + a*3) % mod
		}
	}
	return 0
}

func main() {
	var i int 
	for i = 1; i <= 10; i++ {
		printf(foo(i,1))
	}
	return
}