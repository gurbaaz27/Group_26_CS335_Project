package main

func main() {
	var a [8]float64 = [8]float64{1.1, 2.2, 3.3, 4.4, 5.5, 6.6, 7.7, 8.8}

	var sum float64 = 0

	for i := 0; i < 8 ; i++ {
		sum += a[i]
	}

	printf(sum)

	return
}
