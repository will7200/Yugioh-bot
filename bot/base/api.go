package base

import (
	"net"
	"os"
	"os/signal"
	"syscall"
)

const (
	HomeDir             = "~/DLBot"
	osArgsDebugContains = "debug"
)

var (
	Version    string
	BuildDate  string
	GitCommit  string
	GitSummary string
	GitState   string
	GitBranch  string
)

func GetListener(failure chan struct{}) (net.Listener, error) {
	listener, err := net.Listen("unix", "/tmp/go.sock")
	if err != nil {
		return nil, err
	}
	sigc := make(chan os.Signal, 1)
	signal.Notify(sigc, os.Interrupt, os.Kill, syscall.SIGTERM)
	go func(c chan os.Signal) {
		// Wait for a SIGINT or SIGKILL:
		sig := <-c
		log.Infof("Caught signal %s: shutting down.", sig)
		// Stop listening (and unlink the socket if unix type):
		listener.Close()
		// And we're done:
		os.Exit(0)
	}(sigc)
	go func(c chan struct{}) {
		// Wait for a SIGINT or SIGKILL:
		sig := <-c
		log.Warnf("Caught signal %s: shutting down.", sig)
		// Stop listening (and unlink the socket if unix type):
		listener.Close()
		// And we're done:
		os.Exit(1)
	}(failure)
	return listener, nil
}
