# Running the algorithm

Example run for 2021-03-03:

bazel-bin/src/org/fotw/h2h/h2h
  --participants_csv_path /home/agrimball/current-participants-v2.csv
  --host_csv_path /home/agrimball/2020-12-09-h2h-host.csv
  --updated_host_csv_path /home/agrimball/2021-03-03-h2h-host.csv
  --match_date 2021-03-03
  --N 100

TODO(agrimball): This would ideally be an example shell script that's tested somewhere...
