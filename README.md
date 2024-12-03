# Servision
Servision is a modular API server that can process media with machine learning and computer vision algorithms

## How to Use
 - Servision can be used to run algorithms on user-uploaded files. The algorithms can be anything provided a few simple requirements are met:
    - Its module name is added to the 'algorithms' part of the config.json
    - All required imports are in 'requirements.txt'
    - It's in its own module '{name}.py' in the server/algorithms folder
    - The algorithm module contains the function `proc_call(token, store_path, out_path) -> tuple[int, str]`
       - token: The task id, `{algo}_{uid}_{timestamp}`, which should be used in any output filenames
       - store_path: the location of the input file
       - out_path: the folder where any output files should be written
       - returns (int, str): Status code (0=ok, 1=error), and message, which if status=0, returns out_path  
   
      It is recommended that error checking be done in proc_call(), i.e. checking if the paths exist
 - Servision is integrated with firebase for authentication.
    - Generate a new private key and download the certificate from your firebase console
    - Add the path to your certificate as the environment variable `FB_CERT_PATH`
    - When making requests to the server, include the headers `authorization` with a valid token.



## Tasks left
 - Fully test firebase integration, apply user data to jobs and use auth checks on all queries
 - Create a sample model that is computationally intensive and will produce multiple files,
    - Then test the task check and download queries
    - Benchmark performance by queueing multiple tasks
