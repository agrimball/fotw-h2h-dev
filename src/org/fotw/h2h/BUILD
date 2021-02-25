load("@rules_python//python:defs.bzl", "py_binary", "py_library", "py_test")

py_binary(
    name = "h2h",
    srcs = ["h2h.py"],
    deps = [
        ":historian",
        ":history_warnings",
    ],
)

py_test(
    name = "h2h_test",
    srcs = [":h2h_test.py"],
    deps = [
        ":h2h",
        ":historian",
    ],
)

py_library(
    name = "historian",
    srcs = ["historian.py"],
)

py_test(
    name = "historian_test",
    srcs = [":historian_test.py"],
    data = [":h2h-testing-csv.csv"],
    deps = [":historian"],
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
