package main

// shortcircuiting
const y string = "yes"
const n string = "no"

func main() {
	var a int = 27

	if a == 27 || a == 28 {
		if a + 3 == 31 && a * a == 729 {
			printf(n)
			printf(a)
		} else {
			if a - 3 != 24 {
				printf(n)
				printf(a)
			} else {
				printf(y)
				printf(a)
			}
		}
	}

	return
}
