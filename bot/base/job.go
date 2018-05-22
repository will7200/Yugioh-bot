package base

import (
	"errors"
	"fmt"
	"strconv"
	"strings"
	"sync"
	"time"

	"github.com/cenkalti/backoff"
	"github.com/eapache/channels"
	"github.com/satori/go.uuid"
	"github.com/will7200/mjs/utils/iso8601"
)

var (
	RFC3339WithoutTimezone = "2006-01-02T15:04:05"
	ErrInvalidJob          = errors.New("Invalid job. Job must contain name and executor")
	RegisteredExecutors    = map[string]GenericHandler{}
	RegisteredMiddleware   = map[string][]GenericMiddlewareHandler{}
)

func RegisterExecutor(key string, handler GenericHandler) {
	RegisteredExecutors[key] = handler
}

func RegisterExecutorWithMiddleware(key string, handler GenericHandler, middleware []GenericMiddlewareHandler) {
	RegisteredExecutors[key] = handler
	RegisteredMiddleware[key] = middleware
}

type ErrInvalidExecutor error

type errorExecutor struct {
	executor string
}

func (e *errorExecutor) Error() string {
	return fmt.Sprintf("Invalid executor. Executor %s does not exists or is not registered", e.executor)
}

func NewExecutorError(executor string) ErrInvalidExecutor {
	return &errorExecutor{executor: executor}
}

// GenericHandler is a job handler without any custom context.
type GenericHandler func(*Job) (interface{}, error)

// GenericMiddlewareHandler is a middleware without any custom context.
type GenericMiddlewareHandler func(*Job, NextMiddlewareFunc) error

// NextMiddlewareFunc is a function type (whose instances are named 'next') that you call to advance to the next middleware.
type NextMiddlewareFunc func() error

// Job
type Job struct {
	Name string `json:"Name"` // command is required
	ID   string `json:"ID"`

	Executor     string
	FunctionName string                 `json:"Function,omitempty"`
	Args         map[string]interface{} `json:"args"`
	Unique       bool                   `json:"unique,omitempty"`

	Description string `json:"Description,omitempty"`
	IsActive    bool   `json:"Active"`

	SendResult   bool
	SendTo       channels.NativeChannel
	Schedule     string    `json:"Schedule"`
	ScheduleTime time.Time `json:"Schedule Time"`
	NextRunAt    time.Time `json:"Next Run At"`

	Epsilon         string            `json:"epsilon,omitempty"`
	DelayDuration   *iso8601.Duration `json:"-"`
	EpsilonDuration *iso8601.Duration `json:"-"`

	LastRunAt      time.Time
	TimesRan       int64
	SuccessfulRuns int64
	TimesToRepeat  int64

	BackOff backoff.BackOff

	jobTimer *time.Timer
	lock     sync.RWMutex
}

// NewJob
func NewJob(name, executor, runInterval string, repeatTimes int64, args map[string]interface{}) *Job {
	var runTimes string
	id, err := uuid.NewV4()
	if err != nil {
		panic(err)
	}
	j := &Job{
		Name:     name,
		ID:       id.String(),
		IsActive: true,
		Args:     args,
		Executor: executor,
	}
	t := time.Now().Add(2 * time.Second).Format("2006-01-02T15:04:05Z-0700")
	runTimes = ""
	if repeatTimes > 0 {
		runTimes = strconv.FormatInt(repeatTimes, 10)
	}
	j.Schedule = fmt.Sprintf("R%s/%s/%s", runTimes, t, runInterval)
	return j
}

// NewJobFromMap
func NewJobFromMap(args map[string]interface{}) *Job {
	id, err := uuid.NewV4()
	if err != nil {
		panic(err)
	}
	return &Job{
		Name:     args["Name"].(string),
		ID:       id.String(),
		IsActive: true,
		Args:     args["Args"].(map[string]interface{}),
		Executor: args["Executor"].(string),
		Schedule: args["Scheduler"].(string),
	}
}

// NewOneOffJob
func NewOneOffJob(name, executor string, args map[string]interface{}) *Job {
	return &Job{
		Name:       name,
		Executor:   executor,
		IsActive:   true,
		Args:       args,
		Schedule:   "",
		Epsilon:    "",
		SendResult: true,
	}
}

// setArg sets a single named argument on the job.
func (j *Job) setArg(key string, val interface{}) {
	if j.Args == nil {
		j.Args = make(map[string]interface{})
	}
	j.Args[key] = val
}

// ParseSchedule
func (j *Job) ParseSchedule(allowPastSchedules bool) error {
	var err error
	splitTime := strings.Split(j.Schedule, "/")
	if len(splitTime) != 3 {
		return fmt.Errorf(
			"Schedule not formatted correctly. Should look like: R/2014-03-08T20:00:00Z/PT2H",
		)
	}
	// Handle Repeat Amount
	if splitTime[0] == "R" {
		// Repeat forever
		j.TimesToRepeat = -1
	} else {
		j.TimesToRepeat, err = strconv.ParseInt(strings.Split(splitTime[0], "R")[1], 10, 0)
		if err != nil {
			log.Errorf("Error converting TimesToRepeat to an int: %s", err)
			return err
		}
	}

	j.ScheduleTime, err = time.Parse("2006-01-02T15:04:05Z-0700", splitTime[1])
	if err != nil {
		log.Debug("Parsing without timezone")
		j.ScheduleTime, err = time.Parse(RFC3339WithoutTimezone, splitTime[1])
		if err != nil {
			log.Errorf("Error converting scheduleTime to a time.Time: %s", err)
			return err
		}
	}
	if (time.Duration(j.ScheduleTime.UnixNano()-time.Now().UnixNano())) < 0 && !allowPastSchedules {
		return fmt.Errorf("Schedule time has passed on Job with id of %s", j.ID)
	}

	log.Debugf("Job %s:%s scheduled", j.Name, j.ID)
	infinity := "\xE2\x88\x9E"
	if j.TimesToRepeat != -1 {
		infinity = strconv.FormatInt(j.TimesToRepeat, 10)
	}
	log.Debugf("Starting %s will repeat for %s", j.ScheduleTime, infinity)

	if j.TimesToRepeat != 0 {
		j.DelayDuration, err = iso8601.FromString(splitTime[2])
		if err != nil {
			log.Errorf("Error converting delayDuration to a iso8601.Duration: %s", err)
			return err
		}
		log.Debugf("Delay Duration: %s", j.DelayDuration.ToDuration())
	}

	if j.Epsilon != "" {
		j.EpsilonDuration, err = iso8601.FromString(j.Epsilon)
		if err != nil {
			log.Errorf("Error converting j.Epsilon to iso8601.Duration: %s", err)
			return err
		}
	}

	return nil
}

// CheckSchedule
func (j *Job) CheckSchedule(d *Dispatcher) {
	if !j.IsActive {
		return
	}
	if j.TimesToRepeat == -1 {
		j.StartWaiting(d)
		return
	}
	if int(j.TimesRan) < int(j.TimesToRepeat) {
		j.StartWaiting(d)
		return
	}
}

// Init
func (j *Job) Init(d *Dispatcher) error {
	j.lock.Lock()

	err := j.validation()
	if err != nil {
		return err
	}

	u4, err := uuid.NewV4()
	if err != nil {
		log.Errorf("Error occured when generating uuid: %s", err)
		return err
	}
	j.ID = u4.String()

	if j.Schedule == "" {
		// If schedule is empty, its a one-off job.
		d.AddFutureJob(j, 1*time.Nanosecond)
		return nil
	}

	err = j.ParseSchedule(true)
	if err != nil {
		return err
	}
	j.lock.Unlock()
	j.StartWaiting(d)
	return nil
}

// StartWaiting
func (j *Job) StartWaiting(d *Dispatcher) {
	waitDuration := j.GetWaitDuration()

	log.Infof("%s Scheduled to run in: %s", j.Name, waitDuration)

	j.lock.Lock()
	j.NextRunAt = time.Now().Add(waitDuration)
	j.lock.Unlock()

	d.AddFutureJob(j, waitDuration)
}

// GetWaitDuration
func (j *Job) GetWaitDuration() time.Duration {
	waitDuration := time.Duration(j.ScheduleTime.UnixNano() - time.Now().UnixNano())
	if waitDuration < 0 {
		if j.TimesToRepeat == 0 {
			return 0
		}
		if j.LastRunAt.IsZero() {
			waitDuration = j.DelayDuration.ToDuration()
			t := j.ScheduleTime
			for {
				t = t.Add(waitDuration)
				if t.After(time.Now()) {
					break
				}
			}
			waitDuration = t.Sub(time.Now())
		} else {
			waitDuration = j.DelayDuration.ToDuration()
			t := j.ScheduleTime
			for {
				t = t.Add(waitDuration)
				if t.After(time.Now()) {
					break
				}
			}
			waitDuration = t.Sub(time.Now())
		}
	}

	return waitDuration
}

// SetChannel
func (j *Job) SetChannel(ch channels.NativeChannel) {
	j.lock.Lock()
	defer j.lock.Unlock()
	j.SendTo = ch
}

// CloseChannel
func (j *Job) CloseChannel() {
	j.lock.Lock()
	defer j.lock.Unlock()
	j.SendResult = false
	close(j.SendTo)
	j.SendTo = nil
}

// validation
func (j *Job) validation() error {
	var err error
	if j.Name == "" || j.Executor == "" {
		err = ErrInvalidJob
	} else if _, ok := RegisteredExecutors[j.Executor]; !ok {
		err = NewExecutorError(j.Executor)
	} else {
		return nil
	}
	return err
}
