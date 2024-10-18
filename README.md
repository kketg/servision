# Servision
Servision is a modular API server that can process media with machine learning and computer vision algorithms

## Tasks left
 - Fully test firebase integration, apply user data to jobs and use auth checks on all queries
 - Algorithm may split videos into multiple segments and they will be returned as such, build download query to accomodate that
    i.e. add a "has_next" attribute to the return data if there are more files to download
    This could be done using the postgres instance, for each successfully completed task, and entry is made with a list of returnable filenames

## Goals
 - Integration with Firebase authentication
 - Workers that run processing jobs asynchronously
 - Insertion of any model/algorithm
