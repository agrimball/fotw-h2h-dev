// C++ standard library imports first.
#include <iostream>

// External library imports next.
#include <gflags/gflags.h>

// Within-repository library imports next.
#include "src/cc_example/messages.h"

DEFINE_bool(act_surprised, false, "Acts surprised when called upon to say hello world");

int main(int argc, char *argv[]) {
    gflags::ParseCommandLineFlags(&argc, &argv, true);
    
    if (FLAGS_act_surprised) {
        std::cout << "What!? I'm supposed to do something?\n";
    }
    std::cout << cc_example::HelloMessage();
    return 0;
}
