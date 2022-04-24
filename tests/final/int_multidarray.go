package main

var b int = 6

func main() {
	var a [4][2]int = [4][2]int{{1, 2}, {3, 4}, {5, 6}, {7, 8}}

	var sum int = 0

	for i := 0; i < 4 ; i++ {
		for j := 0; j < 2 ; j++ {
			a[i][j]--
		} 
	}

	for i := 0; i < 4 ; i++ {
		for j := 0; j < 2 ; j++ {
			sum += a[i][j]
		} 
		printf(sum)
	}

	printf(sum)

	return
}
