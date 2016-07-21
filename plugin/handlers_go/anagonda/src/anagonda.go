// +build cgo
// Copyright (C) 2013 - 2016 - Oscar Campos <oscar.campos@member.fsf.org>
// This program is Free Software see LICENSE file for details

package main

/*
#include <stdlib.h>
*/
import "C"

import (
	"bytes"
	"encoding/json"
	"fmt"
	"go/build"
	"log"
	"net/rpc"
	"os"
	"os/user"
	"path"
	"path/filepath"
	"unsafe"
)

//export FreeMemory
func FreeMemory(p *C.char) {
	if p != nil {
		C.free(unsafe.Pointer(p))
	}
}

//export CleanSocket
func CleanSocket() bool {
	if err := os.Remove(getSocketPath()); err != nil {
		fmt.Printf("could  not remove sockt file %s: %s\n", getSocketPath(), err)
		return false
	}
	return true
}

//export SetEnvironment
func SetEnvironment(path, root *C.char, cgo bool) bool {
	if err := os.Setenv("GOPATH", C.GoString(path)); err != nil {
		return false
	}
	if err := os.Setenv("GOROOT", C.GoString(root)); err != nil {
		return false
	}
	cgoString := "0"
	if cgo {
		cgoString = "1"
	}
	if err := os.Setenv("CGO_ENABLED", cgoString); err != nil {
		return false
	}
	return true
}

//export GetEnv
func GetEnv() *C.char {
	data, err := json.Marshal(map[string]string{"GOROOT": os.Getenv("GOROOT"), "GOPATH": os.Getenv("GOPATH"), "CGO_ENABLED": os.Getenv("CGO_ENABLED")})
	if err != nil {
		return C.CString(fmt.Sprintf("%s", err))
	}
	return C.CString(fmt.Sprintf("%s", string(data)))
}

//export AutoComplete
func AutoComplete(code, filePath *C.char, offset int) *C.char {
	addr := *g_addr
	if *g_sock == "unix" {
		addr = getSocketPath()
		dir := path.Dir(addr)
		if _, err := os.Stat(dir); os.IsNotExist(err) {
			if err := os.MkdirAll(dir, 0755); err != nil {
				log.Fatalf("Coul not create socket directory in %s: %s\n", dir, err)
			}
		}
	}

	client, err := rpc.Dial(*g_sock, addr)
	if err != nil {
		fmt.Printf("client could not connect: %s\n", err)
		if *g_sock == "unix" && file_exists(addr) {
			os.Remove(addr)
		}

		err = try_run_server_anaconda(addr)
		if err != nil {
			fmt.Printf("while try_to_run_server: %s\n", err.Error())
			return nil
		}
		client, err = try_to_connect(*g_sock, addr)
		if err != nil {
			fmt.Printf("while try to connect: %s\n", err.Error())
			return nil
		}
	}
	defer client.Close()
	output := C.CString(cmd_auto_complete_anaconda(client, C.GoString(code), C.GoString(filePath), offset))

	return output
}

// non exported stuff
func cmd_auto_complete_anaconda(c *rpc.Client, code, filename string, offset int) string {
	context := pack_build_context(&build.Default)
	file, filename, cursor := prepare_file_filename_cursor_anaconda([]byte(code), filename, offset)
	f := new(json_formatter)
	return f.return_candidates(client_auto_complete(c, file, filename, cursor, context))
}

func prepare_file_filename_cursor_anaconda(file []byte, filename string, offset int) ([]byte, string, int) {
	var skipped int
	file, skipped = filter_out_shebang(file)
	cursor := offset - skipped
	if filename != "" && !filepath.IsAbs(filename) {
		cwd, _ := os.Getwd()
		filename = filepath.Join(cwd, filename)
	}
	return file, filename, cursor
}

func (*json_formatter) return_candidates(candidates []candidate, num int) string {
	var buf bytes.Buffer
	if candidates == nil {
		buf.WriteString("[]")
		return buf.String()
	}

	buf.WriteString("[")

	for i, c := range candidates {
		if i != 0 {
			buf.WriteString(", ")
		}
		buf.WriteString(fmt.Sprintf(`{"class": "%s", "name": "%s", "type": "%s"}`,
			c.Class, c.Name, c.Type))
	}
	buf.WriteString("]")
	return buf.String()
}

func try_run_server_anaconda(addr string) error {
	args := []string{fmt.Sprintf("anaGonda-%s.bin", anaGondaVersion), "-s", "-sock", *g_sock, "-addr", addr}
	cwd, _ := os.Getwd()

	var err error
	stdin, err := os.Open(os.DevNull)
	if err != nil {
		return err
	}
	stdout, err := os.OpenFile(os.DevNull, os.O_WRONLY, 0)
	if err != nil {
		return err
	}
	stderr, err := os.OpenFile(os.DevNull, os.O_WRONLY, 0)
	if err != nil {
		return err
	}

	fmt.Println(os.Environ())
	procattr := os.ProcAttr{Dir: cwd, Env: os.Environ(), Files: []*os.File{stdin, stdout, stderr}}
	p, err := os.StartProcess(anaGondaBinaryPath, args, &procattr)
	if err != nil {
		return err
	}

	return p.Release()
}

func getUserAndHome() (string, string, error) {
	usr, err := user.Current()
	if err != nil {
		fmt.Printf("while getting current user: %s\n", err)
		return "", "", err
	}
	return usr.Username, usr.HomeDir, nil
}

func doAnacondaServer() int {
	g_config.read()
	if g_config.ForceDebugOutput != "" {
		// forcefully enable debugging and redirect logging into the
		// specified file
		*g_debug = true
		f, err := os.Create(g_config.ForceDebugOutput)
		if err != nil {
			panic(err)
		}
		log.SetOutput(f)
	}

	addr := *g_addr
	if file_exists(addr) {
		log.Printf("unix socket: '%s' already exists\n", addr)
		return 1
	}
	g_daemon = new_daemon(*g_sock, addr)
	if *g_sock == "unix" {
		// cleanup unix socket file
		defer os.Remove(addr)
	}

	rpc.Register(new(RPC))

	g_daemon.loop()
	return 0
}
