# Development for the FotW H2H Algorithm

Code is built using Bazel (see http://bazel.build)

## Example build and run

bazel build src/org/fotw/h2h:h2h

bazel-bin/src/org/fotw/h2h/h2h (followed by various command line arguments)

If you run the binary with no command line arguments, you'll get an error telling you what arguments exist.


## Example Test

bazel test src/org/fotw/h2h:all
