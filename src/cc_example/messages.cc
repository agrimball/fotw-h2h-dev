#include <string>
#include <vector>

#include "absl/strings/str_join.h"

#include "src/cc_example/messages.h"

namespace cc_example {

    std::string HelloMessage() {
        std::vector<std::string> v = {"Hello", "World!\n"};
        return absl::StrJoin(v, " ");
    }

}  // End of cc_example namespace