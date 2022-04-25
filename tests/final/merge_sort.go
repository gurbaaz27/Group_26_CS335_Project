package main

var arr [7]int = [7]int{33444, 3, 311, 13, 55, 0, 300}

func merge(start int, mid int, end int) {
	if start == end {
		return
	}
	var a = start
	var b = mid + 1
    
	var temp [7]int
	for base := start; base < end+1; base++ {
		if a == mid+1 {
			temp[base] = arr[b]
			b++
			continue
		}
		if b == end+1 {
			temp[base] = arr[a]
			a++
			continue
		}

		if arr[a] < arr[b] {
			temp[base] = arr[a]
			a++
			continue
		} else {
			temp[base] = arr[b]
			b++
			continue
		}

	}

	for base := start; base < end+1; base++ {
		arr[base] = temp[base]
	}
	
   return 

}

func mergesort(start int, end int) {
	if start == end {
		return
	}
	a := (start + end) / 2
	 mergesort(start, a)
	 mergesort(a+1, end)
// 	for i := 0; i < 7; i++ {
// 		printf(arr[i])
//    }
	merge(start, a, end)
// 	for i := 0; i < 7; i++ {
// 		printf(arr[i])
//    }

}

func main() {
	mergesort(0, 6)
	for i := 0; i < 7; i++ {
	     printf(arr[i])
	}
}