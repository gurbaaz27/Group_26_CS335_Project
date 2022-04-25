package main


func main() {
	n := 5
	var a [5]int
	var c int
	for i := 0; i < n; i++ {
		scanf(&c)
		a[i] = c
	}

	start := 0
	end := n - 1
	var key int = 8
	for start <= end {
		m := start + (end-start)/2

		if (a[m] == (key)) {
			printf("found")
		}

		if (a[m] <  int(key)) {
			start = m + 1
		} else {
			end = m - 1
		}
	}
}