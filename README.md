# Servision
Servision is a modular API server that can process media with machine learning and computer vision algorithms

## Tasks left
 - Fully test firebase integration, apply user data to jobs and use auth checks on all queries
 - Create a sample model that is computationally intensive and will produce multiple files,
    - Then test the task check and download queries
    - Benchmark performance by queueing multiple tasks
 - Make the program load the algorithms by name rather than having to pre-import them

## Goals
 - Integration with Firebase authentication
 - Workers that run processing jobs asynchronously
 - Insertion of any model/algorithm
