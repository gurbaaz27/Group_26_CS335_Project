package main

func power(a int, b int, mod int) int {
	var ans int = 1

	if a == 0 {
		return 0
	}
	for ; b > 0 ; {
		if b % 2 == 1 {
			ans *= a
			ans %= mod
		}
		b /= 2
		a *= a
		a = a % mod
	}

	return ans
}

func main() {
	printf("(5 ^ 5) % 1000 =")
	var res int = power(5, 5, 1000)
	printf(res)
}