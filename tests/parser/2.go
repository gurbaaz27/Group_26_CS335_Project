
//##this has struct and functions returning structs

type Company struct {
    Name string
    Workers []worker
}

type worker struct {
    Name string
    Other []int
}

func NewWorker(name string) worker {
    // note that you cannot declare and initialise struct in one line
    // in our implementation
    var wrk worker
    wrk.Name =  name
    cmp.Workers = append(cmp.Workers, wrk)
    return wrk
}

func main() {
    var cmp Company
    cmp.Name = "Acme"
    wrk := cmp.NewWorker("Bugs")
    for i := 1; i <= 10; i++ {
        wrk.Other = append(wrk.Other, i)
        break 2
    }
    Printf(wrk)
    Printf(cmp)
}