load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

## Language Build Rules

http_archive(
    name = "zlib",
    build_file = "@com_google_protobuf//:third_party/zlib.BUILD",
    sha256 = "629380c90a77b964d896ed37163f5c3a34f6e6d897311f1df2a7016355c45eff",
    strip_prefix = "zlib-1.2.11",
    urls = ["https://github.com/madler/zlib/archive/v1.2.11.tar.gz"],
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

git_repository(
    name = "com_github_gflags_gflags",
    remote = "https://github.com/gflags/gflags.git",
    tag = "v2.2.2"
)

## PROTO ##

http_archive(
    name = "six",
    build_file = "@com_google_protobuf//:third_party/six.BUILD",
    sha256 = "d16a0141ec1a18405cd4ce8b4613101da75da0e9a7aec5bdd4fa804d0e0eba73",
    urls = ["https://pypi.python.org/packages/source/s/six/six-1.12.0.tar.gz"],
)

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

## Python text formatter
http_archive(
    name = "com_google_protobuf_python_srcs",
    strip_prefix = "protobuf-master",
    urls = ["https://github.com/protocolbuffers/protobuf/archive/master.zip"],
    build_file = "//src/workspace_third_party:com_google_protobuf_python_srcs.BUILD.bazel",
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
