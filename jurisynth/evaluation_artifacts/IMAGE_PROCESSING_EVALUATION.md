# Image Processor corpus completion record

The Image Processor used a zero-provider-budget NVIDIA NIM configuration. This
record therefore reports completion time and reliability, not provider billing.
GPU rental is an external infrastructure cost and is not represented as a NIM
per-image charge.

- Eligible images: 27,829
- Indexed descriptions: 27,771
- Recorded processing errors: 58 (0.21% of eligible images)
- Indexed completion rate: 99.79%
- Sum of per-batch logged elapsed time: 185.5 minutes (about 3.09 hours)
- Aggregate observed rate: about 2.50 images/second

The elapsed total is the best completion-time estimate available because it
comes from the completed corpus log. It is workload- and infrastructure-
specific, so it should not be presented as a universal throughput guarantee.
