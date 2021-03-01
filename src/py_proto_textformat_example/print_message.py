from src.py_proto_textformat_example.message_pb2 import MessageSet
from com_google_protobuf_python_srcs.python.google.protobuf import text_format

import sys

def main(argv):
  m = MessageSet()
  m.message.append('Hello')
  m.message.append('World!')
  print(text_format.MessageToString(m))

if __name__ == '__main__':
  main(sys.argv)
