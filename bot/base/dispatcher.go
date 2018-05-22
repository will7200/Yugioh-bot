package base

import (
	"time"

	"github.com/emirpasic/gods/lists/arraylist"
	rbt "github.com/emirpasic/gods/trees/redblacktree"
	"github.com/satori/go.uuid"
)

var (
	log = CheckWithSourcedLog().With("package", "bot.base")
)

// WorkRequest contains identifier along with job
type WorkRequest struct {
	job  *Job
	ID   uuid.UUID
	when *Timer
}

// Dispatcher keeps track of the workers
type Dispatcher struct {
	Workers     *arraylist.List
	Work        chan WorkRequest
	WorkerQueue chan chan WorkRequest
	Check       chan *Job
	timer       *time.Timer
	quit        chan struct{}
	Waiting     *rbt.Tree
}

// AddFutureJob wraps a job into a work request that executes after a time duration
func (d *Dispatcher) AddFutureJob(w *Job, t time.Duration) {
	uid, err := uuid.NewV4()
	if err != nil {
		panic(err)
	}
	work := WorkRequest{job: w, ID: uid}
	d.AddWorkRequest(work, t)
}

// RemoveWaiting removes a waiting job from the queue
func (d *Dispatcher) RemoveWaiting(t *WorkRequest) {
	_, found := d.Waiting.Get(t.ID.String())
	if found {
		t.when.Stop()
		d.AddJob(*t)
		d.Waiting.Remove(t.ID.String())
	}
}

// AddWorkRequest Runs a work request after specified time duration
func (d *Dispatcher) AddWorkRequest(w WorkRequest, t time.Duration) {
	w.job.lock.Lock()
	defer w.job.lock.Unlock()
	f := func() {
		d.RemoveWaiting(&w)
	}
	w.when = NewAfterFunc(t, f)
	w.job.jobTimer = w.when.timer
	d.Waiting.Put(w.ID.String(), w)
}

// AddJob adds a job to the dispatcher
func (d *Dispatcher) AddJob(w WorkRequest) {
	log.Debugf("Workrequest Added To Queue -- Running %s shortly", w.job.Name)
	d.Work <- w
}

// StartDispatcher starts the dispatcher will the amount of workers specified
func (d *Dispatcher) StartDispatcher(nworkers int) {
	// First, initialize the channel we are going to but the workers' work channels into.
	d.Work = make(chan WorkRequest, nworkers)
	d.WorkerQueue = make(chan chan WorkRequest, 100)
	d.quit = make(chan struct{}, 1)
	d.Check = make(chan *Job, 100)
	d.Workers = arraylist.New()
	d.Waiting = rbt.NewWithStringComparator()
	// Now, create all of our workers.
	for i := 0; i < nworkers; i++ {
		log.Infof("Starting worker %d", i+1)
		worker := NewWorker(i+1, d.WorkerQueue, d.Check)
		worker.Start()
		d.Workers.Add(worker)
	}
	go func() {
		for {
			select {
			case work := <-d.Work:
				go func() {
					worker := <-d.WorkerQueue
					worker <- work
				}()
			case work := <-d.Check:
				go func(j *Job, d *Dispatcher) {
					j.CheckSchedule(d)
				}(work, d)
			}
		}
	}()
}

// ScaleWorkers does nothing for now
func (d *Dispatcher) ScaleWorkers(n int) {
	if n < 1 || n > 100 || n == len(d.Work) {
		return
	}
}
