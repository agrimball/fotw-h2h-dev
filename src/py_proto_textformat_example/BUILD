load("@rules_python//python:defs.bzl", "py_binary", "py_library", "py_test")
load("@com_google_protobuf//:protobuf.bzl", "py_proto_library")

py_binary(
    name = "print_message",
    srcs = ["print_message.py"],
    deps = [
      ":message_py_proto",
      "@com_google_protobuf_python_srcs//:python_srcs",
    ],
)

py_proto_library(
    name = "message_py_proto",
    srcs = ["message.proto"],
)
