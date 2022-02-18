

// Function for slices

func main() {
	//Unlike arrays, slices are typed only by the elements they contain (not the number of elements). To create an empty slice with non-zero length, use the builtin make. Here we make a slice of strings of length 3 (initially zero-valued).

		s := make([]string, 3)
		s[0] = "a"
        s[1] = "b"
		s[2] = "c"
		s = append(s, "e", "f")
		c := make([]string, len(s))
		l = s[:5]

		twoD := make([][]int, 3)
		for i := 0; i < 3; i++ {
			innerLen := i + 1
			twoD[i] = make([]int, innerLen)
			for j := 0; j < innerLen; j++ {
				twoD[i][j] = i + j
			}
		}
	}