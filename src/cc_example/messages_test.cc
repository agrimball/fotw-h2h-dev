#include "gtest/gtest.h"

#include "src/cc_example/messages.h"

namespace cc_example{

    TEST(MessagesTest,HelloMessage) {
        EXPECT_EQ(HelloMessage(),"Hello World!\n");
    }

}  // end of cc_example namespace
