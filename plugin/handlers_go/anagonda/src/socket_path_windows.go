// +build windows,cgo
// Copyright (C) 2013 - 2016 - Oscar Campos <oscar.campos@member.fsf.org>
// This program is Free Software see LICENSE file for details

package main

import (
    "os"
    "fmt"
    "path/filepath"
)

func getSocketPath() string {
    user, home, err := getUserAndHome()
    if err != nil {
        return filepath.Join(os.TempDir(), "anaGonda-daemon.universal")
    }
    return filepath.Join(home, "Anaconda", "Go", fmt.Sprintf("anaGonda-daemon.%s", user))
}
