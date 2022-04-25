package main

var sum int = 0

func main() {
	var a [4][2]int = [4][2]int{{1, 2}, {3, 4}, {5, 6}, {7, 8}}

	for i := 0; i < 4 ; i++ {
		for j := 0; j < 2 ; j++ {
			sum += a[i][j]
			break 2*1
		} 
	}

	printf(sum)

	return
}
