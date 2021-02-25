load("@rules_cc//cc:defs.bzl", "cc_binary", "cc_library")

cc_binary(
    name = "hello_worlder",
    srcs = ["hello_worlder.cc"],
    deps = [":constants"],
)

cc_library(
    name = "constants",
    srcs = ["constants.cc"],
    hdrs = ["constants.h"],
)
