SHELL := /bin/bash
GO_BUILD_LDFLAGS :=$(shell govvv -flags -pkg github.com/will7200/Yugioh-bot/bot/base)

GEN_COMMAND = ''
GEN_OUTPUT = ''

install_proto:
	protoc -I. -I${GOPATH}/src \
	-I${GOPATH}/src/github.com/grpc-ecosystem/grpc-gateway/third_party/googleapis \
	-I${GOPATH}/src/github.com/grpc-ecosystem/grpc-gateway/ \
	--swagger_out=logtostderr=true:. \
	--go_out=plugins=grpc:. \
	--grpc-gateway_out=logtostderr=true:. \
	--twirp_out=. \
	bot/rpc/control/service.proto

build:
	source vendor/gocv.io/x/gocv/env.sh && \
	go build -o dlbot -ldflags="$(GO_BUILD_LDFLAGS)" main.go

generate_lua_wrapper:
	[ -e ${GEN_OUTPUT} ] && rm ${GEN_OUTPUT}; go build gen/main.go gen/luaprovider.go gen/comparator.go && \
		./main ${GEN_COMMAND} ${GEN_OUTPUT}