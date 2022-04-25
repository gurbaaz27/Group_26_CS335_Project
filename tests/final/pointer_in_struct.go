package main

type Pointer struct {
	pointer *int64
}

type Job struct {
	JobId   int64
	Status  bool
	Stipend float64
	Point Pointer
}

func main() {
	var a Job
	var b int64 = 9
	
	a.JobId = 108
	a.Status = false
	a.Stipend = 90000.0
	a.Point.pointer = &b

	printf(a.JobId)
	printf(a.Status)
	printf(a.Stipend)
	printf(*a.Point.pointer)

	return
}
