load("@rules_python//python:defs.bzl", "py_binary", "py_library", "py_test")
load("@com_google_protobuf//:protobuf.bzl", "py_proto_library")

py_binary(
    name = "h2h",
    srcs = ["h2h.py"],
    deps = [
      ":h2h_py_proto",
      ":historian",
      ":history_warnings",
      ":match_generator",
      "@com_google_protobuf_python_srcs//:python_srcs",
    ],
)

py_test(
    name = "h2h_test",
    srcs = ["h2h_test.py"],
    deps = [
        ":h2h",
        ":historian",
    ],
)

py_library(
  name = "match_generator",
  srcs = ["match_generator.py"],
  deps = [
    ":h2h_py_proto",
  ],
)

py_library(
  name = "historian",
  srcs = ["historian.py"],
  deps = [
    ":h2h_py_proto",
  ],
)

py_test(
    name = "historian_test",
    srcs = [":historian_test.py"],
    data = [
      ":h2h-testing-textproto.txt",
    ],
    deps = [
      ":historian",
      "@com_google_protobuf_python_srcs//:python_srcs",
    ],
)

py_library(
    name = "history_warnings",
    srcs = ["history_warnings.py"],
)

py_test(
    name = "history_warnings_test",
    srcs = ["history_warnings_test.py"],
    deps = [
        ":historian",
        ":history_warnings",
    ],
)

py_proto_library(
    name = "h2h_py_proto",
    srcs = ["h2h.proto"],
)
