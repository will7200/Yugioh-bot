package base

import (
	"time"

	"github.com/cenkalti/backoff"
)

// Worker
type Worker struct {
	ID          int
	Work        chan WorkRequest
	WorkerQueue chan chan WorkRequest
	CheckQueue  chan *Job
	QuitChan    chan struct{}
}

// NewWorker creates a new worker
func NewWorker(id int, workerQueue chan chan WorkRequest, check chan *Job) Worker {
	worker := Worker{
		ID:          id,
		Work:        make(chan WorkRequest),
		WorkerQueue: workerQueue,
		CheckQueue:  check,
		QuitChan:    make(chan struct{}),
	}

	return worker
}

// Stop tells the worker to stop listening for work requests.
//
// Note that the worker will only stop *after* it has finished its work.
func (w *Worker) Stop() {
	go func() {
		w.QuitChan <- struct{}{}
	}()
}

// Start  the worker by starting a goroutine, that is
// an infinite "for-select" loop.
func (w *Worker) Start() {
	go func() {
		for {
			//time.Sleep(time.Second*60)
			// Add ourselves into the worker queue.
			w.WorkerQueue <- w.Work
			select {
			case work := <-w.Work:
				work.job.lock.Lock()
				work.job.LastRunAt = time.Now()
				work.job.lock.Unlock()
				if executor, ok := RegisteredExecutors[work.job.Executor]; ok {
					work.job.lock.RLock()
					var skipExectuor bool
					var err error
					var result interface{}
					if middlewares, ok := RegisteredMiddleware[work.job.Executor]; ok {
						currentMiddleware := 0
						maxMiddleware := len(middlewares)
						var next NextMiddlewareFunc
						next = func() error {
							if currentMiddleware < maxMiddleware {
								mw := middlewares[currentMiddleware]
								currentMiddleware++
								return mw(work.job, next)
							}
							return nil
						}
						err := next()
						if err != nil {
							log.Errorf("Could not complete %s instance %s due to:  %s", work.job.Name, work.job.ID, err.Error())
							skipExectuor = true
						}
					}
					if !skipExectuor {
						if work.job.BackOff != nil {
							operation := func() error {
								result, err = executor(work.job)
								if err != nil {
									return err
								}
								if work.job.SendTo != nil && result != nil && err == nil && work.job.SendResult {
									work.job.SendTo <- result
								}
								return nil
							}
							err = backoff.RetryNotify(operation, work.job.BackOff, func(e error, duration time.Duration) {
								log.Warnf("Request %s with job %s failed",
									work.ID, work.job.Name)
								log.Warnf("Waiting %s for next run ", duration.String())
							})
							if err == nil {
								work.job.BackOff.Reset()
							}
						} else {
							result, err = executor(work.job)

							if work.job.SendTo != nil && result != nil && err == nil && work.job.SendResult {
								work.job.SendTo <- result
							}
						}
					}
					work.job.lock.RUnlock()
					work.job.lock.Lock()
					work.job.TimesRan += 1
					if err == nil {
						work.job.SuccessfulRuns += 1
					}
					work.job.lock.Unlock()
				} else {
					log.Warnf("Job -- %s is empty, Disabling until fixed", work.job.Name)
					work.job.lock.Lock()
					work.job.IsActive = false
					work.job.lock.Unlock()
				}

				w.CheckQueue <- work.job
			case <-w.QuitChan:
				// We have been asked to stop.
				log.Infof("Worker %d stopping", w.ID)
				return
			}
		}
	}()
}
