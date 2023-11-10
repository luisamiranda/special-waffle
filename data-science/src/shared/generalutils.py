#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os


def replace_in_file(file_path, old_string, new_string):
    # Replace text in a file and write the file back to disk

    with open(file_path) as f:
        newText = f.read().replace(old_string, new_string)

    with open(file_path, "w") as f:
        f.write(newText)

    return


def list_files_recursive(path):
    for root, dirs, files in os.walk(path):
        for file in files:
            print(os.path.join(root, file))
    return
