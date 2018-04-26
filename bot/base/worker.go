package base

import (
	"time"
)

type Worker struct {
	ID          int
	Work        chan WorkRequest
	WorkerQueue chan chan WorkRequest
	CheckQueue  chan *Job
	QuitChan    chan struct{}
}

func NewWorker(id int, workerQueue chan chan WorkRequest, check chan *Job) Worker {
	// Create, and return the worker.
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
				work.Run.lock.Lock()
				work.Run.LastRunAt = time.Now()
				work.Run.lock.Unlock()
				if executor, ok := RegisteredExecutors[work.Run.Executor]; ok {
					work.Run.lock.RLock()
					var skipExectuor bool
					var err error
					var result interface{}
					if middlewares, ok := RegisteredMiddleware[work.Run.Executor]; ok {
						currentMiddleware := 0
						maxMiddleware := len(middlewares)
						var next NextMiddlewareFunc
						next = func() error {
							if currentMiddleware < maxMiddleware {
								mw := middlewares[currentMiddleware]
								currentMiddleware++
								return mw(work.Run, next)
							}
							return nil
						}
						err := next()
						if err != nil {
							log.Errorf("Could not complete %s instance %s due to:  %s", work.Run.Name, work.Run.ID, err.Error())
							skipExectuor = true
						}
					}
					if !skipExectuor {
						result, err = executor(work.Run)

						if work.Run.SendTo != nil && result != nil && err == nil && work.Run.SendResult {
							work.Run.SendTo <- result
						}
					}
					work.Run.lock.RUnlock()
					work.Run.lock.Lock()
					work.Run.TimesRan += 1
					if err == nil {
						work.Run.SuccessfulRuns += 1
					}
					work.Run.lock.Unlock()
				} else {
					log.Warnf("Job -- %s is empty, Disabling until fixed", work.Run.Name)
					work.Run.lock.Lock()
					work.Run.IsActive = false
					work.Run.lock.Unlock()
				}

				w.CheckQueue <- work.Run
			case <-w.QuitChan:
				// We have been asked to stop.
				log.Infof("Worker %d stopping", w.ID)
				return
			}
		}
	}()
}
