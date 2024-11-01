# Servision
Servision is a modular API server that can process media with machine learning and computer vision algorithms

## How to Use
 - Servision can be used to run algorithms on file inputs. The algorithms can be anything provided a few simple requirements are met:
    - All required libraries are in 'requirements.txt'
    - It's in its own module '{name}.py' in the server/algorithms folder, and it's name is added to the 'algorithms' part of the config.json
    - The algorithm module contains the function `proc_call(token, store_path, out_path) -> tuple[int, str]`
       - token: The task id, `{algo}_{uid}_{timestamp}`, which should be used in any output filenames
       - store_path: the location of the input file
       - out_path: the location where any output should be written
       - returns (int, str): Status code (0=ok, 1=error), and message, which if status=0, returns out_path. 



## Tasks left
 - Fully test firebase integration, apply user data to jobs and use auth checks on all queries
 - Create a sample model that is computationally intensive and will produce multiple files,
    - Then test the task check and download queries
    - Benchmark performance by queueing multiple tasks

## Goals
 - Integration with Firebase authentication
 - Workers that run processing jobs asynchronously
 - Insertion of any model/algorithm
