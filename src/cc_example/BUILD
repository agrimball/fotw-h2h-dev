load("@rules_cc//cc:defs.bzl", "cc_binary", "cc_library")

cc_binary(
    name = "hello_worlder",
    srcs = ["hello_worlder.cc"],
    deps = [":messages"],
)

cc_library(
    name = "messages",
    srcs = ["messages.cc"],
    hdrs = ["messages.h"],
)
