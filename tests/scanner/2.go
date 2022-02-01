// Slice and For Loop
package main

import "fmt"

func main() {
	/* This is a slice
	declaration only */s := make([]string, 3) // random comment

	fmt.Println("emp🚀", s) // This is a valid emoji inside the string
	s[0] = "abc"
	s[1] = "bcd"
	s[2] = "c"
	fmt.Println("set:", s)
	fmt.Println("get:", s[2])

	fmt.Println("len:", len(s))

	s = append(s, "d")
	s = append(s, "e", "f")
	twoD := make([][]int, 3)
	for i := 0; i < 3; i++ {
		innerLen := i + 1
		twoD[i] = make([]int, innerLen)
		for j := 0; j < innerLen; j++ {
			twoD[i][j] = i + j
		}
	}

	i := 1
	for i <= 3 {
		fmt.Println(i)
		i = i + 1
	}
}
