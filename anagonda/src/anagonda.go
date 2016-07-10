// Copyright (C) 2013 - 2016 - Oscar Campos <oscar.campos@member.fsf.org>
// This program is Free Software see LICENSE file for details

package main

import "C"

import (
    "os"
    "go/build"
    "fmt"
    "bytes"
    "net/rpc"
    "path/filepath"
)

//export AutoComplete
func AutoComplete(code, path *C.char, offset int) *C.char {
    addr := *g_addr
    if *g_sock == "unix" {
        addr = get_socket_filename()
    }

    client, err := rpc.Dial(*g_sock, addr)
    if err != nil {
        fmt.Printf("client could not connect: %s\n", err)
        if *g_sock == "unix" && file_exists(addr) {
            os.Remove(addr)
        }

        err = try_run_server_anaconda()
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
    output := C.CString(cmd_auto_complete_anaconda(client, C.GoString(code), C.GoString(path), offset))

    return output
}

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

    buf.WriteString(fmt.Sprintf(`[%d, [`, num))

    for i, c := range candidates {
        if i != 0 {
            buf.WriteString(", ")
        }
        buf.WriteString(fmt.Sprintf(`{"class": "%s", "name": "%s", "type": "%s"}`,
            c.Class, c.Name, c.Type))
    }
    buf.WriteString("]]")
    return buf.String()
}

func try_run_server_anaconda() error {
    args := []string{fmt.Sprintf("anaGonda-%s.bin", anaGondaVersion), "-s", "-sock", *g_sock, "-addr", *g_addr}
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

    fmt.Println(anaGondaBinaryPath, args)
    procattr := os.ProcAttr{Dir: cwd, Env: os.Environ(), Files: []*os.File{stdin, stdout, stderr}}
    p, err := os.StartProcess(anaGondaBinaryPath, args, &procattr)
    if err != nil {
        return err
    }

    return p.Release()
}
