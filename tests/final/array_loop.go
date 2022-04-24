package main

var b int = 6

func main() {
	var a [8]int = [8]int{1, 2, 3, 4, 5, 6, 7, 8}

	var sum int = 0

	for i := 0; i < 8 ; i++ {
		sum += a[i]
		printf(sum)
	}

	printf(sum)

	return
}
