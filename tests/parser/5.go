func foo() {
    Printf("foo")
}

// recursion and global string

func fact(n int) int {
    if n == 0 {
        return 1
    }
    return n * fact(n-1)
}


// This is intentional mistake, as globally shortvardecl is not allowed
a := "sgasdg"

func main() {
    Printf(fact(7)a)

}