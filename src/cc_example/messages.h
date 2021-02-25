#ifndef SRC_CC_EXAMPLE_MESSAGES_H_
#define SRC_CC_EXAMPLE_MESSAGES_H_
// We use #ifndef and #define logic to ensure that header files are never
// read by the compiler more than once (which can create problems).

#include <string>

// All library functions (which is all functions that are not main)
// belong in a namespace.
namespace cc_example {
  std::string HelloMessage();
}  // End of cc_example namespace

#endif  // SRC_CC_EXAMPLE_MESSAGES_H_
