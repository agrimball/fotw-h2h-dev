load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

## Language Build Rules

http_archive(
    name = "zlib",
    urls = [
        "https://mirror.bazel.build/zlib.net/zlib-1.2.11.tar.gz",
    ],
    sha256 = "c3e5e9fdd5004dcb542feda5ee4f0ff0744628baf8ed2dd5d66f8ca1197cb1a1",
    strip_prefix = "zlib-1.2.11",
    build_file = "//src/workspace_third_party:zlib.BUILD.bazel",
)

http_archive(
    name = "rules_python",
    strip_prefix = "rules_python-master/",
    url = "https://github.com/bazelbuild/rules_python/archive/master.zip",
)

http_archive(
    name = "rules_cc",
    strip_prefix = "rules_cc-master/",
    url = "https://github.com/bazelbuild/rules_cc/archive/master.zip",
)

## GoogleTest C++

load("@bazel_tools//tools/build_defs/repo:git.bzl", "git_repository")

git_repository(
    name = "gtest",
    remote = "https://github.com/google/googletest",
    branch = "v1.10.x",
)

## PROTO ##

# proto_library rules implicitly depend on @com_google_protobuf//:protoc,
# which is the proto-compiler.
# This statement defines the @com_google_protobuf repo.
http_archive(
    name = "com_google_protobuf",
    strip_prefix = "protobuf-master",
    urls = ["https://github.com/protocolbuffers/protobuf/archive/master.zip"],
)

# java_proto_library rules implicitly depend on @com_google_protobuf_java//:java_toolchain,
# which is the Java proto runtime (base classes and common utilities).
http_archive(
    name = "com_google_protobuf_java",
    strip_prefix = "protobuf-master",
    urls = ["https://github.com/protocolbuffers/protobuf/archive/master.zip"],
)

http_archive(
    name = "bazel_skylib",
    strip_prefix = "bazel-skylib-master",
    urls = ["https://github.com/bazelbuild/bazel-skylib/archive/master.zip"],
)

load("@bazel_skylib//lib:versions.bzl", "versions")

versions.check(minimum_bazel_version = "0.5.4")

# android_sdk_repository(
#     name = "androidsdk",
#     api_level = 26,
#     build_tools_version = "26.0.1"
# )

# http_archive(
#     name = "io_bazel_rules_appengine",
#     sha256 = "f4fb98f31248fca5822a9aec37dc362105e57bc28e17c5611a8b99f1d94b37a4",
#     strip_prefix = "rules_appengine-0.0.6",
#     url = "https://github.com/bazelbuild/rules_appengine/archive/0.0.6.tar.gz",
# )
# load("@io_bazel_rules_appengine//appengine:appengine.bzl", "appengine_repositories")
# appengine_repositories()
