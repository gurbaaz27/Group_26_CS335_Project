package main

var b int = 6

func main() {
	var a [4][2]float64 = [4][2]float64{{1.0, 2.1}, {3.9, 4.3}, {5.85, 6.2}, {7.1, 8.119}}

	var sum float64 = 0

	// for i := 0; i < 4 ; i++ {
	// 	for j := 0; j < 2 ; j++ {
	// 		a[i][j] 
	// 	} 
	// }

	for i := 0; i < 4 ; i++ {
		for j := 0; j < 2 ; j++ {
			sum += a[i][j]
		} 
		printf(sum)
	}

	printf(sum)

	return
}
