load("@rules_cc//cc:defs.bzl", "cc_binary", "cc_library")

cc_binary(
    name = "hello_worlder",
    srcs = ["hello_worlder.cc"],
    deps = [
        ":messages",
        "@com_github_gflags_gflags//:gflags",
    ],
)

cc_library(
    name = "messages",
    srcs = ["messages.cc"],
    hdrs = ["messages.h"],
    deps = ["@com_google_absl//absl/strings"],
)

cc_test (
    name = "messages_test",
    srcs = [
        "messages_test.cc",
    ],
    deps = [
        ":messages",
        "@gtest//:gtest",
        "@gtest//:gtest_main"
    ],
)
