package main

type ErrorMessage struct {
	Id int64
	Message string
}

type JobResponse struct {
	JobId   int64
	Status  bool
	Error ErrorMessage
	Remarks string
}

func main() {
	var a JobResponse
	a.JobId = 22
	a.Status = true
	a.Error.Id = 1
	a.Error.Message = "Error encountered captain!"
	a.Remarks = "Nice work"
	printf(a.JobId)
	printf(a.Status)
	printf(a.Remarks)
	printf(a.Error.Id)
	printf(a.Error.Message)

	return
}
