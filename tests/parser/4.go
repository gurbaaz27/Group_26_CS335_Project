func main() {

    Printf("go" + "lang")

    Printf("1+1 =", 1+1)
    Printf("7.0/3.0 =", 7.0/3.0)

    Printf(true && false)
    Printf(true || false)
    Printf(!true)
    var a = "initial"
    Printf(a)

    var b int = 1
    Printf(b, c)

    var d = true
    Printf(d)

    var e int
    Printf(e)

    f := "apple"
    Printf(f)
    	
    const s string = "constant"
    const n = 500000000



    if 7%2 == 0 {
        Printf("7 is even")
    } else {
        Printf("7 is odd")
    }

    if 8%4 == 0 {
        Printf("8 is divisible by 4")
    }

    if num := 9; num < 0 {
        Printf(num, "is negative")
    } else if num < 10 {
        Printf(num, "has 1 digit")
    } else {
        Printf(num, "has multiple digits")
    }


    var a [5]int
    Printf("emp:", a)

    a[4] = 100
    Printf("set:", a)
    Printf("get:", a[4])

    Printf("len:", len(a))

    b := [5]int{1, 2, 3, 4, 5}
    Printf("dcl:", b)

    var twoD [2][3]int
    for i := 0; i < 2; i++ {
        for j := 0; j < 3; j++ {
            twoD[i][j] = i + j
        }
    }
}