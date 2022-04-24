package main

const a string = "j :"
const b string = "i :"
const c string = "====="

func main() {

	for i := 0; i < 10 ; i++ {
		if i % 2 == 0 {
			continue
		} 
		printf(i)
	}

	printf(c)

	for i := 0; i < 10; i++ {
		for j := 0; j < 10; j++ {
			for k := 0; k < 10; k++ {
				if k % 2 == 0 {
					continue
				}
				printf(k)
			}
			if j % 2 == 1 {
				continue
			}
			printf(a)
			printf(j)
		}
		if i > 0 && i < 9 {
			continue
		}
		printf(b)
		printf(i)
	}

	return
}